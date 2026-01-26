"""Graph evaluator for analyzing agent coordination patterns."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import networkx as nx
from pydantic import BaseModel

from agentbeats.messenger import TraceData

if TYPE_CHECKING:
    from networkx import DiGraph


class GraphMetrics(BaseModel):
    """Expected structure of graph metrics for evaluations."""

    node_count: int
    edge_count: int
    avg_degree: float | None = None
    density: float | None = None
    centrality_scores: dict[str, float] | None = None


class GraphEvaluator:
    """Evaluates agent coordination using graph analysis."""

    def __init__(self) -> None:
        """Initialize graph evaluator with empty graph."""
        self._graph: DiGraph[Any] | None = None

    def build_graph(self, traces: list[TraceData]) -> DiGraph[Any]:
        """Build a directed graph from agent interaction traces.

        Args:
            traces: List of TraceData objects representing agent interactions

        Returns:
            NetworkX DiGraph with agents as nodes and interactions as edges
        """
        graph: DiGraph[Any] = nx.DiGraph()

        # Extract agent-to-agent interactions from traces
        # Each trace represents an interaction where an evaluator talks to an agent
        for trace in traces:
            agent_url = trace.agent_url
            # Add agent as node if not already present
            if agent_url not in graph:
                graph.add_node(agent_url)

        # Add edges for interactions (evaluator -> agent)
        # Count interactions as edge weights
        for trace in traces:
            agent_url = trace.agent_url
            # For now, we track each agent independently
            # In multi-agent scenarios, we'd extract source/target from trace context
            # This implementation focuses on single-evaluator to multiple-agents pattern
            if "evaluator" not in graph:
                graph.add_node("evaluator")

            if graph.has_edge("evaluator", agent_url):
                # Increment weight for repeated interactions
                graph["evaluator"][agent_url]["weight"] += 1
            else:
                # Create new edge with weight 1
                graph.add_edge("evaluator", agent_url, weight=1)

        self._graph = graph
        return graph

    def compute_metrics(self) -> GraphMetrics:
        """Compute graph metrics for coordination analysis.

        Returns:
            GraphMetrics object with node count, edge count, and centrality scores
        """
        if self._graph is None:
            # Return empty metrics if no graph built yet
            return GraphMetrics(node_count=0, edge_count=0)

        node_count = self._graph.number_of_nodes()
        edge_count = self._graph.number_of_edges()

        # Compute average degree
        if node_count > 0:
            degrees = [deg for _, deg in self._graph.degree()]
            avg_degree = sum(degrees) / node_count
        else:
            avg_degree = None

        # Compute density (actual edges / possible edges)
        density: float | None
        if node_count > 1:
            density = cast(float, nx.density(self._graph))
        else:
            density = None

        # Compute centrality scores (degree centrality)
        if node_count > 0:
            centrality_scores = nx.degree_centrality(self._graph)
        else:
            centrality_scores = None

        return GraphMetrics(
            node_count=node_count,
            edge_count=edge_count,
            avg_degree=avg_degree,
            density=density,
            centrality_scores=centrality_scores,
        )

    def get_metrics(self) -> GraphMetrics:
        """Alias for compute_metrics() for API flexibility.

        Returns:
            GraphMetrics object with node count, edge count, and centrality scores
        """
        return self.compute_metrics()
