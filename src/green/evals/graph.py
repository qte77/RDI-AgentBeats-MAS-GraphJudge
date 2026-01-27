"""Graph-based coordination analysis with pluggable metric system.

Builds directed graphs from interaction traces and computes coordination quality
metrics using graph theory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import networkx as nx
from pydantic import BaseModel

from green.models import InteractionStep


class GraphMetricPlugin(ABC):
    """Base interface for graph metric plugins.

    Enables adding custom metrics without modifying core GraphEvaluator code.
    Each metric plugin computes a single metric from the graph.
    """

    @abstractmethod
    def compute(self, graph: nx.DiGraph[str]) -> Any:
        """Compute metric from graph.

        Args:
            graph: Directed graph representing agent interactions

        Returns:
            Computed metric value (type depends on specific metric)
        """
        pass


class GraphMetrics(BaseModel):
    """Graph metrics for coordination quality assessment.

    All centrality metrics are pluggable - each is computed independently
    and can be extended without modifying core code.

    Attributes:
        degree_centrality: Degree centrality for each agent
        betweenness_centrality: Betweenness centrality for each agent
        closeness_centrality: Closeness centrality for each agent
        eigenvector_centrality: Eigenvector centrality for each agent
        pagerank: PageRank scores for each agent
        graph_density: Graph density (0-1, >0.3 indicates healthy collaboration)
        clustering_coefficient: Average clustering coefficient
        connected_components: Number of connected components
        average_path_length: Average path length between agents
        diameter: Graph diameter (longest shortest path)
        bottlenecks: List of agents with betweenness > 0.5
        isolated_agents: List of agents with degree = 0
        over_centralized: True if single agent handles > 70% interactions
    """

    model_config = {"extra": "allow"}

    degree_centrality: dict[str, float]
    betweenness_centrality: dict[str, float]
    closeness_centrality: dict[str, float]
    eigenvector_centrality: dict[str, float]
    pagerank: dict[str, float]
    graph_density: float
    clustering_coefficient: float
    connected_components: int
    average_path_length: float
    diameter: int
    bottlenecks: list[str]
    isolated_agents: list[str]
    over_centralized: bool


class DegreeCentralityPlugin(GraphMetricPlugin):
    """Degree centrality metric plugin."""

    def compute(self, graph: nx.DiGraph[str]) -> dict[str, float]:
        return nx.degree_centrality(graph)


class BetweennessCentralityPlugin(GraphMetricPlugin):
    """Betweenness centrality metric plugin."""

    def compute(self, graph: nx.DiGraph[str]) -> dict[str, float]:
        return nx.betweenness_centrality(graph)


class ClosenessCentralityPlugin(GraphMetricPlugin):
    """Closeness centrality metric plugin with disconnected graph handling."""

    def compute(self, graph: nx.DiGraph[str]) -> dict[str, float]:
        if len(graph) == 0:
            return {}
        try:
            result: dict[str, float] = nx.closeness_centrality(graph)
            return result
        except nx.NetworkXError:
            return {str(node): 0.0 for node in graph.nodes()}


class EigenvectorCentralityPlugin(GraphMetricPlugin):
    """Eigenvector centrality metric plugin with convergence handling."""

    def compute(self, graph: nx.DiGraph[str]) -> dict[str, float]:
        if len(graph) == 0:
            return {}
        try:
            result: dict[str, float] = nx.eigenvector_centrality(graph, max_iter=1000)
            return result
        except (nx.PowerIterationFailedConvergence, nx.NetworkXError):
            return {str(node): 0.0 for node in graph.nodes()}


class PageRankPlugin(GraphMetricPlugin):
    """PageRank metric plugin."""

    def compute(self, graph: nx.DiGraph[str]) -> dict[str, float]:
        return nx.pagerank(graph)


class GraphDensityPlugin(GraphMetricPlugin):
    """Graph density metric plugin."""

    def compute(self, graph: nx.DiGraph[str]) -> float:
        density_result: float = nx.density(graph)  # type: ignore[assignment]
        return density_result


class ClusteringCoefficientPlugin(GraphMetricPlugin):
    """Clustering coefficient metric plugin."""

    def compute(self, graph: nx.DiGraph[str]) -> float:
        return nx.average_clustering(graph.to_undirected())


class ConnectedComponentsPlugin(GraphMetricPlugin):
    """Connected components count metric plugin."""

    def compute(self, graph: nx.DiGraph[str]) -> int:
        return nx.number_weakly_connected_components(graph)


class GraphEvaluator:
    """Graph-based coordination analysis evaluator.

    Builds directed graph from TraceData (nodes = agents, edges = interactions)
    and computes pluggable coordination quality metrics.
    """

    def __init__(self) -> None:
        """Initialize graph evaluator with built-in metric plugins."""
        self._plugins: dict[str, GraphMetricPlugin] = {}

        # Register built-in plugins
        self.register_plugin("degree_centrality", DegreeCentralityPlugin())
        self.register_plugin("betweenness_centrality", BetweennessCentralityPlugin())
        self.register_plugin("closeness_centrality", ClosenessCentralityPlugin())
        self.register_plugin("eigenvector_centrality", EigenvectorCentralityPlugin())
        self.register_plugin("pagerank", PageRankPlugin())
        self.register_plugin("graph_density", GraphDensityPlugin())
        self.register_plugin("clustering_coefficient", ClusteringCoefficientPlugin())
        self.register_plugin("connected_components", ConnectedComponentsPlugin())

    def register_plugin(self, name: str, plugin: GraphMetricPlugin) -> None:
        """Register a custom metric plugin.

        Args:
            name: Plugin name (will be used as key in metrics output)
            plugin: GraphMetricPlugin instance
        """
        self._plugins[name] = plugin

    async def evaluate(self, traces: list[InteractionStep]) -> GraphMetrics:
        """Evaluate coordination quality using graph analysis.

        Builds directed graph from interaction traces and computes:
        - Centrality metrics (degree, betweenness, closeness, eigenvector, PageRank)
        - Structure metrics (density, clustering, connected components)
        - Path metrics (average path length, diameter)
        - Detects bottlenecks, isolated agents, over-centralization

        Args:
            traces: List of InteractionStep traces to analyze

        Returns:
            GraphMetrics with all computed metrics
        """
        # Handle empty traces
        if not traces:
            return self._empty_metrics()

        # Build directed graph from traces
        graph = self._build_graph(traces)

        # Compute all registered plugin metrics
        plugin_results: dict[str, Any] = {}
        for name, plugin in self._plugins.items():
            plugin_results[name] = plugin.compute(graph)

        # Extract required metrics from plugin results with type assertions
        degree_centrality: dict[str, float] = plugin_results.get("degree_centrality", {})
        betweenness_centrality: dict[str, float] = plugin_results.get("betweenness_centrality", {})
        closeness_centrality: dict[str, float] = plugin_results.get("closeness_centrality", {})
        eigenvector_centrality: dict[str, float] = plugin_results.get("eigenvector_centrality", {})
        pagerank: dict[str, float] = plugin_results.get("pagerank", {})
        graph_density: float = plugin_results.get("graph_density", 0.0)
        clustering_coefficient: float = plugin_results.get("clustering_coefficient", 0.0)
        connected_components: int = plugin_results.get("connected_components", 0)

        # Compute path metrics (not yet pluginized)
        average_path_length, diameter = self._compute_path_metrics(graph)

        # Detect bottlenecks (betweenness > 0.5)
        bottlenecks: list[str] = [
            agent for agent, centrality in betweenness_centrality.items() if centrality > 0.5
        ]

        # Detect isolated agents (degree = 0)
        isolated_agents: list[str] = [
            agent for agent, degree in degree_centrality.items() if degree == 0.0
        ]

        # Detect over-centralization (single agent > 70% interactions)
        over_centralized = self._detect_over_centralization(graph)

        # Build metrics dict with required fields
        metrics_dict: dict[str, Any] = {
            "degree_centrality": degree_centrality,
            "betweenness_centrality": betweenness_centrality,
            "closeness_centrality": closeness_centrality,
            "eigenvector_centrality": eigenvector_centrality,
            "pagerank": pagerank,
            "graph_density": graph_density,
            "clustering_coefficient": clustering_coefficient,
            "connected_components": connected_components,
            "average_path_length": average_path_length,
            "diameter": diameter,
            "bottlenecks": bottlenecks,
            "isolated_agents": isolated_agents,
            "over_centralized": over_centralized,
        }

        # Add custom plugin results (those not in built-in metrics)
        builtin_keys = {
            "degree_centrality",
            "betweenness_centrality",
            "closeness_centrality",
            "eigenvector_centrality",
            "pagerank",
            "graph_density",
            "clustering_coefficient",
            "connected_components",
        }
        for key, value in plugin_results.items():
            if key not in builtin_keys:
                metrics_dict[key] = value

        return GraphMetrics(**metrics_dict)

    def _build_graph(self, traces: list[InteractionStep]) -> nx.DiGraph[str]:
        """Build directed graph from interaction traces.

        Nodes represent agents (identified by step_id).
        Edges represent interactions (parent_step_id -> step_id).

        Args:
            traces: List of InteractionStep traces

        Returns:
            Directed graph representing agent interactions
        """
        graph: nx.DiGraph[str] = nx.DiGraph()

        # Add nodes for all steps
        for step in traces:
            graph.add_node(step.step_id)

        # Add edges based on parent-child relationships
        for step in traces:
            if step.parent_step_id is not None:
                graph.add_edge(step.parent_step_id, step.step_id)

        return graph

    def _compute_path_metrics(self, graph: nx.DiGraph[str]) -> tuple[float, int]:
        """Compute path metrics (average path length and diameter).

        Handles disconnected graphs by computing metrics on largest component.

        Args:
            graph: Directed graph

        Returns:
            Tuple of (average_path_length, diameter)
        """
        if len(graph) == 0:
            return 0.0, 0

        # For disconnected graphs, compute on largest weakly connected component
        if not nx.is_weakly_connected(graph):
            # Get largest weakly connected component
            components = list(nx.weakly_connected_components(graph))
            largest_cc = max(components, key=len)
            subgraph = graph.subgraph(largest_cc)

            if len(subgraph) <= 1:
                return 0.0, 0

            try:
                avg_path_length: float = nx.average_shortest_path_length(subgraph)
                diameter: int = nx.diameter(subgraph)
                return avg_path_length, diameter
            except nx.NetworkXError:
                return 0.0, 0

        # For connected graphs
        try:
            avg_path_length_connected: float = nx.average_shortest_path_length(graph)
            diameter_connected: int = nx.diameter(graph)
            return avg_path_length_connected, diameter_connected
        except nx.NetworkXError:
            return 0.0, 0

    def _detect_over_centralization(self, graph: nx.DiGraph[str]) -> bool:
        """Detect over-centralization (single agent handles > 70% interactions).

        Args:
            graph: Directed graph

        Returns:
            True if single agent handles > 70% of interactions
        """
        if len(graph) == 0:
            return False

        total_edges = graph.number_of_edges()
        if total_edges == 0:
            return False

        # Check if any single node has > 70% of total degree (in + out)
        for node in graph.nodes():
            in_deg: int = graph.in_degree(node)
            out_deg: int = graph.out_degree(node)
            node_degree = in_deg + out_deg
            if node_degree / (2 * total_edges) > 0.7:
                return True

        return False

    def _empty_metrics(self) -> GraphMetrics:
        """Return empty metrics for empty traces."""
        return GraphMetrics(
            degree_centrality={},
            betweenness_centrality={},
            closeness_centrality={},
            eigenvector_centrality={},
            pagerank={},
            graph_density=0.0,
            clustering_coefficient=0.0,
            connected_components=0,
            average_path_length=0.0,
            diameter=0,
            bottlenecks=[],
            isolated_agents=[],
            over_centralized=False,
        )
