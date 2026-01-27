"""Executor with trace collection and cleanup.

Collects interaction traces during task execution and provides cleanup.
Real agent-to-agent communication enables authentic coordination measurement.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from green.evals.system import LatencyMetrics, evaluate_latency
from green.models import CallType, InteractionStep

if TYPE_CHECKING:
    from green.messenger import Messenger


class Executor:
    """Executor that collects interaction traces and manages cleanup."""

    def __init__(self) -> None:
        """Initialize executor."""
        pass

    async def execute_task(self, task_description: str, messenger: Messenger, agent_url: str) -> list[InteractionStep]:
        """Execute task and collect interaction traces.

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

        try:
            # Record start time
            start_time = datetime.now()

            # Send message via messenger
            await messenger.send_message(url=agent_url, message=task_description)

            # Record end time
            end_time = datetime.now()

            # Calculate latency in milliseconds
            latency = int((end_time - start_time).total_seconds() * 1000)

            # Create interaction step
            step = InteractionStep(
                step_id=str(uuid.uuid4()),
                trace_id=trace_id,
                call_type=CallType.AGENT,
                start_time=start_time,
                end_time=end_time,
                latency=latency,
            )

            traces.append(step)

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

    async def _evaluate_graph(self, traces: list[InteractionStep], graph_evaluator: any) -> dict[str, any] | None:
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
        self, traces: list[InteractionStep], llm_judge: any, graph_results: dict[str, any] | None
    ) -> dict[str, any] | None:
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

    async def evaluate_all(
        self,
        traces: list[InteractionStep],
        graph_evaluator: any,
        llm_judge: any,
        latency_evaluator: any,
    ) -> dict[str, any]:
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

        # Tier 2: Latency evaluation
        tier2_latency = None
        if latency_evaluator is not None:
            try:
                tier2_latency = await latency_evaluator.evaluate(traces)
            except Exception as e:
                tier2_latency = {"error": str(e)}

        return {
            "tier1_graph": tier1_graph,
            "tier2_llm": tier2_llm,
            "tier2_latency": tier2_latency,
        }
