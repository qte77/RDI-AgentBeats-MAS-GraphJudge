"""Executor with trace collection and cleanup.

Collects interaction traces during task execution and provides cleanup.
Real agent-to-agent communication enables authentic coordination measurement.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from common.models import TraceCollectionConfig
from green.evals.system import evaluate_latency
from green.models import CallType, InteractionStep, LatencyMetrics

if TYPE_CHECKING:
    from green.messenger import Messenger


def _is_complete(response: str) -> bool:
    """Check if A2A response contains status='complete' in metadata."""
    try:
        data = json.loads(response)
        return isinstance(data, dict) and data.get("status") == "complete"
    except (json.JSONDecodeError, ValueError, TypeError):
        return False


class Executor:
    """Executor that collects interaction traces and manages cleanup."""

    def __init__(
        self,
        coordination_rounds: int,
        round_delay_seconds: float = 0.1,
        trace_collection: TraceCollectionConfig | None = None,
    ) -> None:
        """Initialize executor.

        Args:
            coordination_rounds: Number of message rounds for fixed-rounds mode
            round_delay_seconds: Delay between rounds in fixed-rounds mode
            trace_collection: Config for adaptive collection (idle + timeout + signals).
                When provided, replaces fixed-rounds loop with hybrid strategy.
        """
        self._coordination_rounds = coordination_rounds
        self._round_delay_seconds = round_delay_seconds
        self._trace_collection = trace_collection

    async def execute_task(
        self, task_description: str, messenger: Messenger, agent_url: str
    ) -> list[InteractionStep]:
        """Execute task and collect interaction traces.

        Dispatches to adaptive collection when TraceCollectionConfig is set,
        otherwise uses fixed-rounds mode for backward compatibility.

        Args:
            task_description: Task description to send to agent
            messenger: Messenger instance for agent communication
            agent_url: URL of agent to communicate with

        Returns:
            List of InteractionStep traces collected during execution

        Raises:
            Exception: If task execution fails (after cleanup)
        """
        try:
            if self._trace_collection is not None:
                return await self._adaptive_execute(
                    task_description, messenger, agent_url, self._trace_collection
                )
            return await self._fixed_execute(task_description, messenger, agent_url)
        finally:
            await messenger.close()

    async def _adaptive_execute(
        self,
        task_description: str,
        messenger: Messenger,
        agent_url: str,
        config: TraceCollectionConfig,
    ) -> list[InteractionStep]:
        """Adaptive trace collection: idle detection + timeout + completion signals.

        Implements the recommended hybrid strategy from docs/trace-collection-strategy.md:
        - Completion signal: stops when response contains status="complete"
        - Idle detection: stops when agent doesn't respond within idle_threshold_seconds
        - Timeout safety: hard stop after max_timeout_seconds

        Args:
            task_description: Initial task message
            messenger: Messenger for agent communication
            agent_url: Agent endpoint URL
            config: Adaptive collection configuration

        Returns:
            List of collected InteractionStep traces
        """
        traces: list[InteractionStep] = []
        trace_id = str(uuid.uuid4())
        previous_step_id: str | None = None
        deadline = time.monotonic() + config.max_timeout_seconds
        round_num = 0

        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break  # Hard timeout exceeded

            per_msg_timeout = min(float(config.idle_threshold_seconds), remaining)
            message = (
                task_description
                if round_num == 0
                else f"Follow-up coordination round {round_num + 1}"
            )

            start_time = datetime.now()
            try:
                response: str = await asyncio.wait_for(
                    messenger.send_message(url=agent_url, message=message),
                    timeout=per_msg_timeout,
                )
            except TimeoutError:
                break  # Idle threshold exceeded or remaining time expired

            end_time = datetime.now()
            latency = int((end_time - start_time).total_seconds() * 1000)
            step_id = str(uuid.uuid4())
            traces.append(
                InteractionStep(
                    step_id=step_id,
                    trace_id=trace_id,
                    call_type=CallType.AGENT,
                    start_time=start_time,
                    end_time=end_time,
                    latency=latency,
                    parent_step_id=previous_step_id,
                )
            )
            previous_step_id = step_id

            if config.use_completion_signals and _is_complete(response):
                break

            round_num += 1

        return traces

    async def _fixed_execute(
        self,
        task_description: str,
        messenger: Messenger,
        agent_url: str,
    ) -> list[InteractionStep]:
        """Fixed-rounds trace collection (legacy backward-compatible mode).

        Args:
            task_description: Initial task message
            messenger: Messenger for agent communication
            agent_url: Agent endpoint URL

        Returns:
            List of collected InteractionStep traces
        """
        traces: list[InteractionStep] = []
        trace_id = str(uuid.uuid4())
        previous_step_id: str | None = None

        for round_num in range(self._coordination_rounds):
            start_time = datetime.now()
            message = (
                task_description
                if round_num == 0
                else f"Follow-up coordination round {round_num + 1}"
            )
            await messenger.send_message(url=agent_url, message=message)
            end_time = datetime.now()
            latency = int((end_time - start_time).total_seconds() * 1000)
            step_id = str(uuid.uuid4())
            traces.append(
                InteractionStep(
                    step_id=step_id,
                    trace_id=trace_id,
                    call_type=CallType.AGENT,
                    start_time=start_time,
                    end_time=end_time,
                    latency=latency,
                    parent_step_id=previous_step_id,
                )
            )
            previous_step_id = step_id

            if round_num < self._coordination_rounds - 1:
                await asyncio.sleep(self._round_delay_seconds)

        return traces

    def _evaluate_latency(self, steps: list[InteractionStep]) -> LatencyMetrics:
        """Evaluate latency metrics from interaction steps.

        Part of Tier 2 assessment. Computes percentiles and identifies
        performance bottlenecks within the same system/run.

        Args:
            steps: List of InteractionStep traces to analyze

        Returns:
            LatencyMetrics with percentiles and slowest agent identification
        """
        return evaluate_latency(steps)

    async def _evaluate_graph(
        self, traces: list[InteractionStep], graph_evaluator: Any
    ) -> dict[str, Any] | None:
        """Execute Tier 1 graph evaluation.

        Args:
            traces: List of interaction steps
            graph_evaluator: Graph evaluator instance

        Returns:
            Graph evaluation results or None if evaluator is None
        """
        if graph_evaluator is None:
            return None

        try:
            return await graph_evaluator.evaluate(traces)
        except Exception as e:
            return {"error": str(e)}

    async def _evaluate_llm(
        self, traces: list[InteractionStep], llm_judge: Any, graph_results: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        """Execute Tier 2 LLM evaluation with graph context.

        Args:
            traces: List of interaction steps
            llm_judge: LLM judge instance
            graph_results: Tier 1 graph evaluation results for context

        Returns:
            LLM evaluation results or None if evaluator is None
        """
        if llm_judge is None:
            return None

        try:
            return await llm_judge.evaluate(traces, graph_results=graph_results)
        except Exception as e:
            return {"error": str(e)}

    async def _evaluate_latency_tier2(
        self, traces: list[InteractionStep], latency_evaluator: Any
    ) -> dict[str, Any] | None:
        """Execute Tier 2 latency evaluation.

        Args:
            traces: List of interaction steps
            latency_evaluator: Latency evaluator instance

        Returns:
            Latency evaluation results or None if evaluator is None
        """
        if latency_evaluator is None:
            return None

        try:
            return await latency_evaluator.evaluate(traces)
        except Exception as e:
            return {"error": str(e)}

    async def evaluate_all(
        self,
        traces: list[InteractionStep],
        graph_evaluator: Any,
        llm_judge: Any,
        latency_evaluator: Any,
    ) -> dict[str, Any]:
        """Orchestrate evaluation across all tiers.

        Executes evaluation in two tiers:
        1. Tier 1: Graph structural analysis
        2. Tier 2: LLM semantic assessment + Latency performance metrics

        Graph results are passed to LLM judge for enriched context.

        Args:
            traces: List of interaction steps to evaluate
            graph_evaluator: Tier 1 graph analysis evaluator
            llm_judge: Tier 2 semantic assessment evaluator
            latency_evaluator: Tier 2 performance metrics evaluator

        Returns:
            Structured response with all evaluation results:
            - tier1_graph: Graph structural metrics
            - tier2_llm: Semantic assessment with reasoning
            - tier2_latency: Performance metrics
        """
        # Tier 1: Graph evaluation (structural analysis)
        tier1_graph_result = await self._evaluate_graph(traces, graph_evaluator)

        # FIXME: Convert Pydantic models to dicts for downstream consumers.
        # Prefer passing Pydantic models directly and updating consumers to use
        # model attributes instead of dict.get() for type safety.
        tier1_graph: dict[str, Any] | None
        if tier1_graph_result is not None and hasattr(tier1_graph_result, "model_dump"):
            tier1_graph = tier1_graph_result.model_dump()  # type: ignore[union-attr]
        elif isinstance(tier1_graph_result, dict):
            tier1_graph = tier1_graph_result
        else:
            tier1_graph = None

        # Tier 2: LLM Judge and Latency evaluation
        # Pass graph results to LLM for enriched context
        tier2_llm = await self._evaluate_llm(
            traces,
            llm_judge,
            tier1_graph,  # type: ignore[arg-type]
        )
        tier2_latency = await self._evaluate_latency_tier2(traces, latency_evaluator)

        return {
            "tier1_graph": tier1_graph,
            "tier2_llm": tier2_llm,
            "tier2_latency": tier2_latency,
        }
