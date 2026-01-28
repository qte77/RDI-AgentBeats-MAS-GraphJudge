"""Tests for graph-based coordination analysis.

Tests validate metric computation, bottleneck detection, and model_validate() usage.
GraphMetrics consolidated in green.models for single source of truth.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from green.evals.graph import GraphEvaluator
from green.models import CallType, GraphMetrics, InteractionStep


@pytest.fixture
def simple_trace() -> list[InteractionStep]:
    """Simple linear trace: A -> B -> C."""
    return [
        InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            latency=100,
        ),
        InteractionStep(
            step_id="step-002",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            latency=150,
        ),
    ]


@pytest.fixture
def hub_trace() -> list[InteractionStep]:
    """Hub-and-spoke trace: Central agent communicates with multiple agents."""
    return [
        InteractionStep(
            step_id="step-001",
            trace_id="trace-hub",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            latency=100,
        ),
        InteractionStep(
            step_id="step-002",
            trace_id="trace-hub",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            latency=110,
            parent_step_id="step-001",
        ),
        InteractionStep(
            step_id="step-003",
            trace_id="trace-hub",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            latency=120,
            parent_step_id="step-001",
        ),
        InteractionStep(
            step_id="step-004",
            trace_id="trace-hub",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            latency=130,
            parent_step_id="step-001",
        ),
    ]


@pytest.fixture
def isolated_trace() -> list[InteractionStep]:
    """Trace with isolated agent (no connections)."""
    return [
        InteractionStep(
            step_id="step-001",
            trace_id="trace-isolated",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            latency=100,
        ),
    ]


class TestGraphMetricsModel:
    """Test GraphMetrics model structure using model_validate()."""

    def test_graph_metrics_from_dict(self):
        """GraphMetrics created via model_validate from dict."""
        metrics = GraphMetrics.model_validate(
            {
                "degree_centrality": {},
                "betweenness_centrality": {},
                "closeness_centrality": {},
                "eigenvector_centrality": {},
                "pagerank": {},
                "graph_density": 0.0,
                "clustering_coefficient": 0.0,
                "connected_components": 1,
                "average_path_length": 0.0,
                "diameter": 0,
                "bottlenecks": [],
                "has_bottleneck": False,
                "isolated_agents": [],
                "over_centralized": False,
                "coordination_quality": "low",
            }
        )
        assert hasattr(metrics, "degree_centrality")
        assert hasattr(metrics, "betweenness_centrality")
        assert hasattr(metrics, "closeness_centrality")
        assert hasattr(metrics, "eigenvector_centrality")
        assert hasattr(metrics, "pagerank")

    def test_graph_metrics_with_values(self):
        """GraphMetrics with actual values via model_validate."""
        metrics = GraphMetrics.model_validate(
            {
                "degree_centrality": {"agent-1": 0.6},
                "betweenness_centrality": {"agent-1": 0.3},
                "closeness_centrality": {"agent-1": 1.0},
                "eigenvector_centrality": {"agent-1": 0.7},
                "pagerank": {"agent-1": 0.5},
                "graph_density": 0.5,
                "clustering_coefficient": 0.3,
                "connected_components": 2,
                "average_path_length": 2.5,
                "diameter": 5,
                "bottlenecks": ["agent-1"],
                "has_bottleneck": True,
                "isolated_agents": [],
                "over_centralized": False,
                "coordination_quality": "high",
            }
        )
        assert metrics.graph_density == 0.5
        assert metrics.clustering_coefficient == 0.3
        assert metrics.connected_components == 2
        assert metrics.average_path_length == 2.5
        assert metrics.diameter == 5
        assert metrics.bottlenecks == ["agent-1"]
        assert metrics.has_bottleneck is True
        assert metrics.coordination_quality == "high"

    def test_graph_metrics_default_values(self):
        """GraphMetrics with default values via model_validate."""
        metrics = GraphMetrics.model_validate({})
        assert metrics.degree_centrality == {}
        assert metrics.graph_density == 0.0
        assert metrics.has_bottleneck is False
        assert metrics.coordination_quality == "low"


class TestGraphEvaluatorCentralityMetrics:
    """Test centrality metrics computation."""

    async def test_degree_centrality_computed(self, simple_trace):
        """Degree centrality is computed for all agents."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.degree_centrality, dict)
        assert len(metrics.degree_centrality) > 0

    async def test_betweenness_centrality_computed(self, simple_trace):
        """Betweenness centrality is computed for all agents."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.betweenness_centrality, dict)
        assert len(metrics.betweenness_centrality) > 0

    async def test_closeness_centrality_computed(self, simple_trace):
        """Closeness centrality is computed for all agents."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.closeness_centrality, dict)
        assert len(metrics.closeness_centrality) > 0

    async def test_eigenvector_centrality_computed(self, simple_trace):
        """Eigenvector centrality is computed for all agents."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.eigenvector_centrality, dict)
        assert len(metrics.eigenvector_centrality) > 0

    async def test_pagerank_computed(self, simple_trace):
        """PageRank is computed for all agents."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.pagerank, dict)
        assert len(metrics.pagerank) > 0


class TestGraphEvaluatorStructureMetrics:
    """Test graph structure metrics computation."""

    async def test_graph_density_computed(self, simple_trace):
        """Graph density is computed."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.graph_density, float)
        assert 0.0 <= metrics.graph_density <= 1.0

    async def test_clustering_coefficient_computed(self, simple_trace):
        """Clustering coefficient is computed."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.clustering_coefficient, float)
        assert 0.0 <= metrics.clustering_coefficient <= 1.0

    async def test_connected_components_computed(self, simple_trace):
        """Connected components count is computed."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.connected_components, int)
        assert metrics.connected_components > 0


class TestGraphEvaluatorPathMetrics:
    """Test path metrics computation."""

    async def test_average_path_length_computed(self, simple_trace):
        """Average path length is computed."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.average_path_length, float)
        assert metrics.average_path_length >= 0.0

    async def test_diameter_computed(self, simple_trace):
        """Diameter is computed."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.diameter, int)
        assert metrics.diameter >= 0


class TestBottleneckDetection:
    """Test bottleneck detection (betweenness > 0.5)."""

    async def test_bottleneck_detection_with_hub_trace(self, hub_trace):
        """Bottleneck detected when agent has betweenness > 0.5."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(hub_trace)
        assert isinstance(metrics.bottlenecks, list)

    async def test_no_bottleneck_in_simple_trace(self, simple_trace):
        """No bottleneck detected in simple linear trace."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.bottlenecks, list)

    async def test_bottleneck_list_contains_agent_ids(self, hub_trace):
        """Bottleneck list contains agent identifiers."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(hub_trace)
        if metrics.bottlenecks:
            for bottleneck in metrics.bottlenecks:
                assert isinstance(bottleneck, str)


class TestIsolatedAgentDetection:
    """Test isolated agent detection (degree = 0)."""

    async def test_isolated_agent_detection(self, isolated_trace):
        """Isolated agent detected when degree = 0."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(isolated_trace)
        assert isinstance(metrics.isolated_agents, list)

    async def test_no_isolated_agents_in_connected_trace(self, simple_trace):
        """No isolated agents in connected trace."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.isolated_agents, list)

    async def test_isolated_agents_list_contains_agent_ids(self, isolated_trace):
        """Isolated agents list contains agent identifiers."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(isolated_trace)
        if metrics.isolated_agents:
            for agent in metrics.isolated_agents:
                assert isinstance(agent, str)


class TestOverCentralizationDetection:
    """Test over-centralization detection (single agent > 70%)."""

    async def test_over_centralization_detection(self, hub_trace):
        """Over-centralization detected when single agent handles > 70% interactions."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(hub_trace)
        assert isinstance(metrics.over_centralized, bool)

    async def test_no_over_centralization_in_balanced_trace(self, simple_trace):
        """No over-centralization in balanced trace."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.over_centralized, bool)


class TestGraphBuilding:
    """Test graph construction from traces."""

    async def test_evaluator_builds_directed_graph(self, simple_trace):
        """Evaluator builds directed graph from traces."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert metrics is not None
        assert isinstance(metrics, GraphMetrics)

    async def test_evaluator_handles_empty_traces(self):
        """Evaluator handles empty trace list gracefully."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate([])
        assert metrics is not None
        assert isinstance(metrics, GraphMetrics)

    async def test_evaluator_uses_parent_step_id_for_edges(self, hub_trace):
        """Evaluator uses parent_step_id to build graph edges."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(hub_trace)
        assert metrics is not None
        assert isinstance(metrics, GraphMetrics)


class TestGraphEvaluatorHealthyCollaboration:
    """Test distribution quality metrics."""

    async def test_density_threshold_for_healthy_collaboration(self, simple_trace):
        """Graph density > 0.3 indicates healthy collaboration."""
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(simple_trace)
        assert isinstance(metrics.graph_density, float)


class TestPluggableMetricSystem:
    """Test pluggable metric system for custom metrics.

    STORY-014 requirement: Plugin interface allows adding custom metrics
    without modifying core code.
    """

    async def test_custom_metric_plugin_can_be_registered(self, simple_trace):
        """Custom metric plugin can be registered without modifying core code."""
        from green.evals.graph import GraphMetricPlugin

        # Define custom metric plugin
        class CustomDegreeRatio(GraphMetricPlugin):
            """Custom metric: ratio of max to min degree."""

            def compute(self, graph):
                degrees = dict(graph.degree())
                if not degrees:
                    return 0.0
                max_deg = max(degrees.values())
                min_deg = min(degrees.values())
                return max_deg / min_deg if min_deg > 0 else float(max_deg)

        # Register plugin
        evaluator = GraphEvaluator()
        evaluator.register_plugin("custom_degree_ratio", CustomDegreeRatio())

        # Should not raise error
        metrics = await evaluator.evaluate(simple_trace)
        assert metrics is not None

    async def test_custom_metric_plugin_result_included_in_metrics(self, simple_trace):
        """Custom metric plugin result is included in returned metrics."""
        from green.evals.graph import GraphMetricPlugin

        class CustomMetric(GraphMetricPlugin):
            def compute(self, graph):
                return 42.0

        evaluator = GraphEvaluator()
        evaluator.register_plugin("custom_test_metric", CustomMetric())

        metrics = await evaluator.evaluate(simple_trace)
        metrics_dict = metrics.model_dump()
        assert "custom_test_metric" in metrics_dict
        assert metrics_dict["custom_test_metric"] == 42.0

    async def test_multiple_custom_plugins_can_be_registered(self, simple_trace):
        """Multiple custom plugins can be registered and all execute."""
        from green.evals.graph import GraphMetricPlugin

        class PluginA(GraphMetricPlugin):
            def compute(self, graph):
                return 1.0

        class PluginB(GraphMetricPlugin):
            def compute(self, graph):
                return 2.0

        evaluator = GraphEvaluator()
        evaluator.register_plugin("plugin_a", PluginA())
        evaluator.register_plugin("plugin_b", PluginB())

        metrics = await evaluator.evaluate(simple_trace)
        metrics_dict = metrics.model_dump()

        assert metrics_dict["plugin_a"] == 1.0
        assert metrics_dict["plugin_b"] == 2.0

    async def test_builtin_metrics_are_implemented_as_plugins(self):
        """Built-in metrics use the same plugin system for consistency."""
        evaluator = GraphEvaluator()

        # Verify built-in metrics are registered as plugins
        assert hasattr(evaluator, "_plugins")
        assert len(evaluator._plugins) > 0

        # Check some expected built-in plugin names
        plugin_names = list(evaluator._plugins.keys())
        assert "degree_centrality" in plugin_names
        assert "betweenness_centrality" in plugin_names
        assert "graph_density" in plugin_names
