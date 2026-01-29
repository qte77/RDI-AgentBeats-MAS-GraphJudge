"""Executor with trace collection and cleanup.

Collects interaction traces during task execution and provides cleanup.
Real agent-to-agent communication enables authentic coordination measurement.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from green.evals.system import evaluate_latency
from green.models import CallType, InteractionStep, LatencyMetrics

if TYPE_CHECKING:
    from green.messenger import Messenger

# TODO: Implement trace collection strategy from docs/trace-collection-strategy.md
#   Recommended: Hybrid approach (task completion + timeout + idle detection)
# FIXME: Current fixed-rounds approach is placeholder for testing


class Executor:
    """Executor that collects interaction traces and manages cleanup."""

    def __init__(self, coordination_rounds: int, round_delay_seconds: float = 0.1) -> None:
        """Initialize executor.

        Args:
            coordination_rounds: Number of message rounds to simulate coordination
            round_delay_seconds: Delay between coordination rounds in seconds
        """
        self._coordination_rounds = coordination_rounds
        self._round_delay_seconds = round_delay_seconds

    async def execute_task(
        self, task_description: str, messenger: Messenger, agent_url: str
    ) -> list[InteractionStep]:
        """Execute task and collect interaction traces.

        Sends multiple messages to simulate a coordination pattern:
        - Round 1: Initial coordinator request
        - Round 2+: Follow-up coordination messages with parent links

        Args:
            task_description: Task description to send to agent
            messenger: Messenger instance for agent communication
            agent_url: URL of agent to communicate with

        Returns:
            List of InteractionStep traces collected during execution

        Raises:
            Exception: If task execution fails (after cleanup)
        """
        traces: list[InteractionStep] = []
        trace_id = str(uuid.uuid4())
        previous_step_id: str | None = None

        try:
            for round_num in range(self._coordination_rounds):
                # Record start time
                start_time = datetime.now()

                # Send message via messenger
                message = (
                    task_description
                    if round_num == 0
                    else f"Follow-up coordination round {round_num + 1}"
                )
                await messenger.send_message(url=agent_url, message=message)

                # Record end time
                end_time = datetime.now()

                # Calculate latency in milliseconds
                latency = int((end_time - start_time).total_seconds() * 1000)

                # Create interaction step with parent link for coordination graph
                step_id = str(uuid.uuid4())
                step = InteractionStep(
                    step_id=step_id,
                    trace_id=trace_id,
                    call_type=CallType.AGENT,
                    start_time=start_time,
                    end_time=end_time,
                    latency=latency,
                    parent_step_id=previous_step_id,  # Link to previous step
                )

                traces.append(step)
                previous_step_id = step_id

                # Small delay between rounds for realistic timing
                if round_num < self._coordination_rounds - 1:
                    await asyncio.sleep(self._round_delay_seconds)

            return traces

        finally:
            # Always cleanup messenger connections
            await messenger.close()

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
        tier1_graph = await self._evaluate_graph(traces, graph_evaluator)

        # Tier 2: LLM Judge and Latency evaluation
        # Pass graph results to LLM for enriched context
        tier2_llm = await self._evaluate_llm(traces, llm_judge, tier1_graph)
        tier2_latency = await self._evaluate_latency_tier2(traces, latency_evaluator)

        return {
            "tier1_graph": tier1_graph,
            "tier2_llm": tier2_llm,
            "tier2_latency": tier2_latency,
        }
