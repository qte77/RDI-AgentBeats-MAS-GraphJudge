"""Agent evaluation orchestration logic.

Coordinates calls to evaluators (Graph, LLM Judge, Latency) and aggregates
evaluation results into structured response.
"""

from __future__ import annotations

from typing import Any

from green.models import InteractionStep


class Agent:
    """Agent evaluation orchestrator.

    Coordinates evaluation across three tiers:
    - Tier 1: Graph evaluator (structural analysis)
    - Tier 2: LLM Judge (semantic assessment) + Latency evaluator (performance)

    The Agent implements domain-specific coordination assessment logic by
    passing Tier 1 graph results to the LLM judge for enriched context.
    """

    def __init__(
        self,
        graph_evaluator: Any,
        llm_judge: Any,
        latency_evaluator: Any,
    ) -> None:
        """Initialize Agent with evaluators.

        Args:
            graph_evaluator: Tier 1 graph analysis evaluator
            llm_judge: Tier 2 semantic assessment evaluator
            latency_evaluator: Tier 2 performance metrics evaluator
        """
        self.graph_evaluator = graph_evaluator
        self.llm_judge = llm_judge
        self.latency_evaluator = latency_evaluator

    async def evaluate(self, traces: list[InteractionStep]) -> dict[str, Any]:
        """Evaluate agent coordination quality across all tiers.

        Orchestrates evaluation in two tiers:
        1. Tier 1: Graph structural analysis
        2. Tier 2: LLM semantic assessment + Latency performance metrics

        Graph results are passed to LLM judge for enriched context.

        Args:
            traces: List of interaction steps to evaluate

        Returns:
            Structured response with all evaluation results:
            - tier1_graph: Graph structural metrics
            - tier2_llm: Semantic assessment with reasoning
            - tier2_latency: Performance metrics
            - coordination_summary: Overall coordination quality assessment
        """
        # Tier 1: Graph evaluation (structural analysis)
        tier1_graph = await self._evaluate_tier1_graph(traces)

        # Tier 2: LLM Judge and Latency evaluation
        # Pass graph results to LLM for enriched context
        tier2_llm = await self._evaluate_tier2_llm(traces, tier1_graph)
        tier2_latency = await self._evaluate_tier2_latency(traces)

        # Generate coordination summary
        coordination_summary = self._generate_coordination_summary(
            tier1_graph, tier2_llm, tier2_latency
        )

        return {
            "tier1_graph": tier1_graph,
            "tier2_llm": tier2_llm,
            "tier2_latency": tier2_latency,
            "coordination_summary": coordination_summary,
        }

    async def _evaluate_tier1_graph(self, traces: list[InteractionStep]) -> dict[str, Any] | None:
        """Execute Tier 1 graph evaluation.

        Args:
            traces: List of interaction steps

        Returns:
            Graph evaluation results or None if evaluation fails
        """
        try:
            return await self.graph_evaluator.evaluate(traces)
        except Exception as e:
            return {"error": str(e)}

    async def _evaluate_tier2_llm(
        self,
        traces: list[InteractionStep],
        graph_results: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        """Execute Tier 2 LLM evaluation with graph context.

        Args:
            traces: List of interaction steps
            graph_results: Tier 1 graph evaluation results for context

        Returns:
            LLM evaluation results or None if evaluation fails
        """
        try:
            return await self.llm_judge.evaluate(traces, graph_results=graph_results)
        except Exception as e:
            return {"error": str(e)}

    async def _evaluate_tier2_latency(self, traces: list[InteractionStep]) -> dict[str, Any] | None:
        """Execute Tier 2 latency evaluation.

        Args:
            traces: List of interaction steps

        Returns:
            Latency evaluation results or None if evaluation fails
        """
        try:
            return await self.latency_evaluator.evaluate(traces)
        except Exception as e:
            return {"error": str(e)}

    def _generate_coordination_summary(
        self,
        tier1_graph: dict[str, Any] | None,
        tier2_llm: dict[str, Any] | None,
        tier2_latency: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Generate domain-specific coordination assessment summary.

        Synthesizes findings from all tiers into a coordination quality assessment.

        Args:
            tier1_graph: Graph evaluation results
            tier2_llm: LLM evaluation results
            tier2_latency: Latency evaluation results

        Returns:
            Coordination summary with overall quality assessment
        """
        # Extract key metrics with error handling
        graph_quality = "unknown"
        if tier1_graph and "error" not in tier1_graph:
            density = tier1_graph.get("graph_density", 0)
            graph_quality = "high" if density > 0.3 else "low"

        semantic_quality = "unknown"
        if tier2_llm and "error" not in tier2_llm:
            semantic_quality = tier2_llm.get("coordination_quality", "unknown")

        performance_quality = "unknown"
        if tier2_latency and "error" not in tier2_latency:
            avg_latency = tier2_latency.get("avg_latency", 0)
            performance_quality = "high" if avg_latency < 2000 else "low"

        # Synthesize overall assessment
        quality_scores = {
            "high": 1.0,
            "medium": 0.5,
            "low": 0.25,
            "unknown": 0.0,
        }

        weights = {"graph": 0.4, "semantic": 0.4, "performance": 0.2}

        overall_score = (
            weights["graph"] * quality_scores.get(graph_quality, 0.0)
            + weights["semantic"] * quality_scores.get(semantic_quality, 0.0)
            + weights["performance"] * quality_scores.get(performance_quality, 0.0)
        )

        return {
            "overall_quality": (
                "high" if overall_score > 0.7 else "medium" if overall_score > 0.4 else "low"
            ),
            "overall_score": overall_score,
            "graph_quality": graph_quality,
            "semantic_quality": semantic_quality,
            "performance_quality": performance_quality,
        }
