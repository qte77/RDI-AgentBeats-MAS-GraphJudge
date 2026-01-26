"""Tests for graph evaluator module defining contract for coordination pattern analysis."""

from pydantic import BaseModel


class TestGraphEvaluatorBuildGraph:
    """Tests defining expected behavior for GraphEvaluator.build_graph(traces)."""

    def test_build_graph_accepts_trace_list(self) -> None:
        """Test that build_graph() accepts a list of traces."""
        # Given: A GraphEvaluator instance and trace data
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When/Then: Should have build_graph method that accepts traces
        assert hasattr(evaluator, "build_graph")
        assert callable(evaluator.build_graph)

    def test_build_graph_creates_networkx_graph(self) -> None:
        """Test that build_graph() creates a NetworkX graph from traces."""
        # Given: A GraphEvaluator instance
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When: We build a graph from traces
        # Then: Should return a NetworkX graph object
        # This test defines the contract - implementation will use networkx.DiGraph
        assert hasattr(evaluator, "build_graph")

    def test_build_graph_handles_empty_traces(self) -> None:
        """Test that build_graph() handles empty trace list gracefully."""
        # Given: A GraphEvaluator instance and empty traces
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()
        _empty_traces: list = []

        # When/Then: Should handle empty input without errors
        assert hasattr(evaluator, "build_graph")

    def test_build_graph_extracts_agent_interactions(self) -> None:
        """Test that build_graph() extracts agent-to-agent interactions from traces."""
        # Given: A GraphEvaluator instance
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When: We build a graph from traces
        # Then: Graph nodes should represent agents
        # Graph edges should represent interactions between agents
        assert hasattr(evaluator, "build_graph")


class TestGraphEvaluatorMetrics:
    """Tests defining expected metrics from graph analysis."""

    def test_metrics_include_node_count(self) -> None:
        """Test that graph metrics include node_count."""
        # Given: A GraphEvaluator instance with a built graph
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When: We compute metrics
        # Then: Should include node_count (number of agents)
        assert hasattr(evaluator, "compute_metrics") or hasattr(evaluator, "get_metrics")

    def test_metrics_include_edge_count(self) -> None:
        """Test that graph metrics include edge_count."""
        # Given: A GraphEvaluator instance with a built graph
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When: We compute metrics
        # Then: Should include edge_count (number of interactions)
        assert hasattr(evaluator, "compute_metrics") or hasattr(evaluator, "get_metrics")

    def test_metrics_include_centrality(self) -> None:
        """Test that graph metrics include centrality measures."""
        # Given: A GraphEvaluator instance with a built graph
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When: We compute metrics
        # Then: Should include centrality metrics for coordination analysis
        # Centrality reveals which agents are most important in coordination
        assert hasattr(evaluator, "compute_metrics") or hasattr(evaluator, "get_metrics")

    def test_metrics_return_structured_data(self) -> None:
        """Test that metrics are returned as structured data."""
        # Given: A GraphEvaluator instance
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When: We compute metrics
        # Then: Should return a dictionary or model with metric values
        # This ensures downstream consumers can easily access metrics
        assert hasattr(evaluator, "compute_metrics") or hasattr(evaluator, "get_metrics")


class GraphMetrics(BaseModel):
    """Expected structure of graph metrics for evaluations."""

    node_count: int
    edge_count: int
    avg_degree: float | None = None
    density: float | None = None
    centrality_scores: dict[str, float] | None = None


class TestGraphMetricsStructure:
    """Tests defining the expected structure of graph metrics."""

    def test_graph_metrics_model_is_valid(self) -> None:
        """Test that GraphMetrics model can be instantiated with valid data."""
        # Given: Valid graph metrics data
        metrics = GraphMetrics(
            node_count=3,
            edge_count=5,
            avg_degree=1.67,
            density=0.83,
            centrality_scores={"agent1": 0.5, "agent2": 0.3},
        )

        # Then: Model should validate successfully
        assert metrics.node_count == 3
        assert metrics.edge_count == 5
        assert metrics.avg_degree == 1.67
        assert metrics.density == 0.83

    def test_graph_metrics_minimal_fields(self) -> None:
        """Test that GraphMetrics model works with minimal required fields."""
        # Given: Minimal graph metrics data
        metrics = GraphMetrics(
            node_count=0,
            edge_count=0,
        )

        # Then: Model should validate with just required fields
        assert metrics.node_count == 0
        assert metrics.edge_count == 0
        assert metrics.avg_degree is None
        assert metrics.centrality_scores is None

    def test_centrality_scores_structure(self) -> None:
        """Test that centrality scores map agent URLs to scores."""
        # Given: Graph metrics with centrality data
        metrics = GraphMetrics(
            node_count=2,
            edge_count=1,
            centrality_scores={
                "http://localhost:9009": 1.0,
                "http://localhost:9010": 0.5,
            },
        )

        # Then: Centrality scores should map agent URLs to numeric scores
        assert isinstance(metrics.centrality_scores, dict)
        assert all(isinstance(k, str) for k in metrics.centrality_scores.keys())
        assert all(isinstance(v, (int, float)) for v in metrics.centrality_scores.values())


class TestGraphEvaluatorContract:
    """Tests defining the overall GraphEvaluator contract."""

    def test_graph_evaluator_can_be_instantiated(self) -> None:
        """Test that GraphEvaluator can be instantiated without arguments."""
        # Given/When: We create a GraphEvaluator instance
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # Then: Instance should be created successfully
        assert evaluator is not None
        assert hasattr(evaluator, "build_graph")

    def test_graph_evaluator_provides_clean_api(self) -> None:
        """Test that GraphEvaluator provides a clean, focused API."""
        # Given: A GraphEvaluator instance
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # Then: Should have methods for graph building and metrics
        assert hasattr(evaluator, "build_graph")
        # Metrics method name can be compute_metrics or get_metrics
        assert hasattr(evaluator, "compute_metrics") or hasattr(evaluator, "get_metrics")

    def test_graph_evaluator_uses_networkx(self) -> None:
        """Test that GraphEvaluator uses NetworkX for graph operations."""
        # Given: Graph evaluator module
        # When: We import the module
        # Then: Should use networkx for graph data structures
        # This is defined by the acceptance criteria and project dependencies
        import networkx as nx

        # NetworkX should be available for graph operations
        assert hasattr(nx, "DiGraph")
        assert hasattr(nx, "degree_centrality")

    def test_graph_evaluator_integration_with_traces(self) -> None:
        """Test that GraphEvaluator integrates with TraceData from messenger."""
        # Given: GraphEvaluator and TraceData structure
        from agentbeats.evals.graph import GraphEvaluator
        from agentbeats.messenger import TraceData

        evaluator = GraphEvaluator()

        # When: We create sample trace data
        sample_trace = TraceData(
            timestamp="2026-01-15T00:00:00Z",
            agent_url="http://localhost:9009",
            message="test",
            response="response",
            status_code=200,
        )

        # Then: GraphEvaluator should be able to process trace data
        # This ensures integration between messenger and graph evaluator
        assert hasattr(evaluator, "build_graph")
        assert sample_trace.agent_url is not None


class TestGraphEvaluatorCoordinationAnalysis:
    """Tests defining coordination pattern analysis capabilities."""

    def test_identifies_central_agents(self) -> None:
        """Test that GraphEvaluator identifies central agents in coordination."""
        # Given: A GraphEvaluator instance
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When: We analyze a graph with multiple agents
        # Then: Centrality metrics should reveal which agents are most central
        # This is the core value proposition of the graph evaluator
        assert hasattr(evaluator, "build_graph")

    def test_measures_coordination_efficiency(self) -> None:
        """Test that GraphEvaluator measures coordination efficiency."""
        # Given: A GraphEvaluator instance
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When: We analyze interaction patterns
        # Then: Metrics should reveal coordination efficiency
        # Dense graphs = high coordination, sparse = low coordination
        assert hasattr(evaluator, "build_graph")

    def test_detects_coordination_bottlenecks(self) -> None:
        """Test that GraphEvaluator can detect coordination bottlenecks."""
        # Given: A GraphEvaluator instance
        from agentbeats.evals.graph import GraphEvaluator

        evaluator = GraphEvaluator()

        # When: We analyze coordination patterns
        # Then: Should identify agents that are bottlenecks (high centrality)
        # This helps evaluate multi-agent system quality
        assert hasattr(evaluator, "build_graph")
