"""Graph-based coordination analysis with pluggable metric system.

Builds directed graphs from interaction traces and computes coordination quality
metrics using graph theory.
"""

from __future__ import annotations

import networkx as nx
from pydantic import BaseModel

from green.models import InteractionStep


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


class GraphEvaluator:
    """Graph-based coordination analysis evaluator.

    Builds directed graph from TraceData (nodes = agents, edges = interactions)
    and computes pluggable coordination quality metrics.
    """

    def __init__(self) -> None:
        """Initialize graph evaluator."""
        pass

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

        # Compute centrality metrics (pluggable)
        degree_centrality: dict[str, float] = nx.degree_centrality(graph)
        betweenness_centrality: dict[str, float] = nx.betweenness_centrality(graph)
        closeness_centrality = self._compute_closeness_centrality(graph)
        eigenvector_centrality = self._compute_eigenvector_centrality(graph)
        pagerank: dict[str, float] = nx.pagerank(graph)

        # Compute structure metrics (pluggable)
        density_result = nx.density(graph)
        graph_density = float(density_result) if density_result is not None else 0.0  # type: ignore[arg-type]
        clustering_coefficient: float = nx.average_clustering(graph.to_undirected())
        connected_components: int = nx.number_weakly_connected_components(graph)

        # Compute path metrics (pluggable)
        average_path_length, diameter = self._compute_path_metrics(graph)

        # Detect bottlenecks (betweenness > 0.5)
        bottlenecks: list[str] = [agent for agent, centrality in betweenness_centrality.items() if centrality > 0.5]

        # Detect isolated agents (degree = 0)
        isolated_agents: list[str] = [agent for agent, degree in degree_centrality.items() if degree == 0.0]

        # Detect over-centralization (single agent > 70% interactions)
        over_centralized = self._detect_over_centralization(graph)

        return GraphMetrics(
            degree_centrality=degree_centrality,
            betweenness_centrality=betweenness_centrality,
            closeness_centrality=closeness_centrality,
            eigenvector_centrality=eigenvector_centrality,
            pagerank=pagerank,
            graph_density=graph_density,
            clustering_coefficient=clustering_coefficient,
            connected_components=connected_components,
            average_path_length=average_path_length,
            diameter=diameter,
            bottlenecks=bottlenecks,
            isolated_agents=isolated_agents,
            over_centralized=over_centralized,
        )

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

    def _compute_closeness_centrality(self, graph: nx.DiGraph[str]) -> dict[str, float]:
        """Compute closeness centrality with handling for disconnected graphs.

        Args:
            graph: Directed graph

        Returns:
            Closeness centrality for each agent
        """
        if len(graph) == 0:
            return {}

        try:
            result: dict[str, float] = nx.closeness_centrality(graph)
            return result
        except nx.NetworkXError:
            return {str(node): 0.0 for node in graph.nodes()}

    def _compute_eigenvector_centrality(self, graph: nx.DiGraph[str]) -> dict[str, float]:
        """Compute eigenvector centrality with handling for convergence issues.

        Args:
            graph: Directed graph

        Returns:
            Eigenvector centrality for each agent
        """
        if len(graph) == 0:
            return {}

        try:
            result: dict[str, float] = nx.eigenvector_centrality(graph, max_iter=1000)
            return result
        except (nx.PowerIterationFailedConvergence, nx.NetworkXError):
            return {str(node): 0.0 for node in graph.nodes()}

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
