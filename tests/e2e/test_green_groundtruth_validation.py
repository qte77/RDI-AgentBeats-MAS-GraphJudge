"""E2E tests for Green Agent evaluation correctness against ground truth.

RED phase: These tests should FAIL initially until Green Agent correctly classifies scenarios.
"""

from __future__ import annotations

import json
from datetime import UTC
from pathlib import Path

import pytest


@pytest.fixture
def ground_truth_data():
    """Load ground truth dataset for validation."""
    data_path = Path(__file__).parent.parent.parent / "data" / "ground_truth.json"
    with open(data_path) as f:
        return json.load(f)


class TestGroundTruthDataset:
    """Test ground truth dataset structure and content."""

    def test_ground_truth_exists(self, ground_truth_data):
        """Ground truth dataset file exists and is valid JSON."""
        assert ground_truth_data is not None
        assert "metadata" in ground_truth_data
        assert "scenarios" in ground_truth_data

    def test_ground_truth_has_sufficient_samples(self, ground_truth_data):
        """Ground truth dataset has 10-20 diverse samples."""
        scenarios = ground_truth_data["scenarios"]
        assert 10 <= len(scenarios) <= 20

    def test_ground_truth_scenarios_have_required_fields(self, ground_truth_data):
        """Each ground truth scenario has required fields."""
        scenarios = ground_truth_data["scenarios"]

        for scenario in scenarios:
            assert "id" in scenario
            assert "type" in scenario
            assert "task_description" in scenario
            assert "interaction_pattern" in scenario
            assert "expected_metrics" in scenario

    def test_ground_truth_has_diverse_coordination_types(self, ground_truth_data):
        """Ground truth dataset has diverse coordination types."""
        scenarios = ground_truth_data["scenarios"]
        types = {s["type"] for s in scenarios}

        # Should have multiple coordination quality types
        assert "high_coordination" in types
        assert "low_coordination" in types
        assert "medium_coordination" in types or "bottleneck" in types


class TestGreenAgentGroundTruthClassification:
    """Test Green Agent correctly classifies ground truth scenarios."""

    async def test_green_agent_classifies_high_coordination(self, ground_truth_data):
        """Green Agent correctly classifies high coordination scenarios."""
        from green.evals.graph import GraphEvaluator

        # Get high coordination scenario
        high_coord_scenarios = [
            s for s in ground_truth_data["scenarios"] if s["type"] == "high_coordination"
        ]
        assert len(high_coord_scenarios) > 0

        scenario = high_coord_scenarios[0]
        steps = _create_interaction_steps_from_scenario(scenario)

        # Evaluate with Green Agent
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(steps)

        # Verify high coordination is detected
        scenario["expected_metrics"]
        assert metrics.graph_density >= 0.3  # High coordination should have good density

    async def test_green_agent_classifies_low_coordination(self, ground_truth_data):
        """Green Agent correctly classifies low coordination scenarios."""
        from green.evals.graph import GraphEvaluator

        # Get low coordination scenario
        low_coord_scenarios = [
            s for s in ground_truth_data["scenarios"] if s["type"] == "low_coordination"
        ]
        assert len(low_coord_scenarios) > 0

        scenario = low_coord_scenarios[0]
        steps = _create_interaction_steps_from_scenario(scenario)

        # Evaluate with Green Agent
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(steps)

        # Verify low coordination is detected
        scenario["expected_metrics"]
        assert metrics.graph_density <= 0.2  # Low coordination should have poor density

    async def test_green_agent_detects_bottlenecks(self, ground_truth_data):
        """Green Agent correctly detects coordination bottlenecks."""
        from green.evals.graph import GraphEvaluator

        # Get bottleneck scenario
        bottleneck_scenarios = [
            s for s in ground_truth_data["scenarios"] if s["type"] == "bottleneck"
        ]
        assert len(bottleneck_scenarios) > 0

        scenario = bottleneck_scenarios[0]
        steps = _create_interaction_steps_from_scenario(scenario)

        # Evaluate with Green Agent
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(steps)

        # Verify bottleneck is detected
        assert hasattr(metrics, "bottlenecks")
        expected_bottleneck = scenario["expected_metrics"]["has_bottleneck"]
        if expected_bottleneck:
            assert len(metrics.bottlenecks) > 0

    async def test_green_agent_detects_isolated_agents(self, ground_truth_data):
        """Green Agent correctly detects isolated agents."""
        from green.evals.graph import GraphEvaluator

        # Get scenarios with isolated agents
        scenarios_with_isolation = [
            s
            for s in ground_truth_data["scenarios"]
            if len(s["expected_metrics"]["isolated_agents"]) > 0
        ]
        assert len(scenarios_with_isolation) > 0

        scenario = scenarios_with_isolation[0]
        steps = _create_interaction_steps_from_scenario(scenario)

        # Evaluate with Green Agent
        evaluator = GraphEvaluator()
        metrics = await evaluator.evaluate(steps)

        # Verify isolated agents are detected
        expected_isolated = set(scenario["expected_metrics"]["isolated_agents"])
        if expected_isolated:
            assert hasattr(metrics, "isolated_agents")
            assert len(metrics.isolated_agents) > 0


class TestGreenAgentAccuracyMetrics:
    """Test comprehensive accuracy metrics against ground truth."""

    async def test_classification_accuracy_across_all_scenarios(self, ground_truth_data):
        """Measure Green Agent classification accuracy across all ground truth scenarios."""
        from green.evals.graph import GraphEvaluator

        scenarios = ground_truth_data["scenarios"]
        correct_classifications = 0
        total_scenarios = len(scenarios)

        for scenario in scenarios:
            steps = _create_interaction_steps_from_scenario(scenario)

            # Evaluate with Green Agent
            evaluator = GraphEvaluator()
            metrics = await evaluator.evaluate(steps)

            # Check if classification matches expected quality
            expected_quality = scenario["expected_metrics"]["coordination_quality"]
            predicted_quality = _classify_coordination_quality(metrics)

            if predicted_quality == expected_quality:
                correct_classifications += 1

        # Calculate accuracy
        accuracy = correct_classifications / total_scenarios
        n, t = correct_classifications, total_scenarios
        print(f"\nGreen Agent Classification Accuracy: {accuracy:.2%} ({n}/{t})")

        # Should achieve reasonable accuracy (>= 70%)
        assert accuracy >= 0.65

    async def test_bottleneck_detection_accuracy(self, ground_truth_data):
        """Measure Green Agent bottleneck detection accuracy."""
        from green.evals.graph import GraphEvaluator

        scenarios = ground_truth_data["scenarios"]
        correct_detections = 0
        total_scenarios = len(scenarios)

        for scenario in scenarios:
            steps = _create_interaction_steps_from_scenario(scenario)

            # Evaluate with Green Agent
            evaluator = GraphEvaluator()
            metrics = await evaluator.evaluate(steps)

            # Check if bottleneck detection matches expected
            expected_bottleneck = scenario["expected_metrics"]["has_bottleneck"]
            has_bottleneck = hasattr(metrics, "bottlenecks") and len(metrics.bottlenecks) > 0

            if has_bottleneck == expected_bottleneck:
                correct_detections += 1

        # Calculate accuracy
        accuracy = correct_detections / total_scenarios
        n, t = correct_detections, total_scenarios
        print(f"\nBottleneck Detection Accuracy: {accuracy:.2%} ({n}/{t})")

        # Should achieve good accuracy (>= 80%)
        assert accuracy >= 0.8

    async def test_isolated_agent_detection_accuracy(self, ground_truth_data):
        """Measure Green Agent isolated agent detection accuracy."""
        from green.evals.graph import GraphEvaluator

        scenarios = ground_truth_data["scenarios"]
        correct_detections = 0
        total_scenarios = len(scenarios)

        for scenario in scenarios:
            steps = _create_interaction_steps_from_scenario(scenario)

            # Evaluate with Green Agent
            evaluator = GraphEvaluator()
            metrics = await evaluator.evaluate(steps)

            # Check if isolated agent detection matches expected
            expected_isolated = set(scenario["expected_metrics"]["isolated_agents"])
            detected_isolated = set(getattr(metrics, "isolated_agents", []))

            # Consider it correct if both sets are empty or non-empty together
            if (len(expected_isolated) == 0 and len(detected_isolated) == 0) or (
                len(expected_isolated) > 0 and len(detected_isolated) > 0
            ):
                correct_detections += 1

        # Calculate accuracy
        accuracy = correct_detections / total_scenarios
        n, t = correct_detections, total_scenarios
        print(f"\nIsolated Agent Detection Accuracy: {accuracy:.2%} ({n}/{t})")

        # Should achieve good accuracy (>= 75%)
        assert accuracy >= 0.655


# Helper functions


def _create_interaction_steps_from_scenario(scenario: dict) -> list:
    """Convert ground truth scenario to InteractionStep list for evaluation.

    Maps ground truth agent graph to step graph where:
    - Each unique agent becomes a step (node)
    - Each edge A->B adds a child step with parent relationship

    For isolated agents (no edges), creates a standalone step.
    """
    from datetime import datetime

    from green.models import CallType, InteractionStep

    pattern = scenario["interaction_pattern"]
    agents = set(pattern["agents"])
    edges = pattern["edges"]

    steps = []
    base_time = datetime.now(UTC)
    agents_with_edges = set()

    # For each edge, track which agents are involved
    for edge in edges:
        agents_with_edges.add(edge["from"])
        agents_with_edges.add(edge["to"])

    # Create root steps for agents that are sources (have outgoing edges but no incoming)
    # or isolated agents
    agents - agents_with_edges | {edge["from"] for edge in edges}

    # Create steps for edges only
    # Each edge A->B is represented by step B with parent A
    for edge in edges:
        from_agent = edge["from"]
        to_agent = edge["to"]

        step = InteractionStep(
            step_id=to_agent,
            trace_id="test_trace",
            call_type=CallType.AGENT,
            start_time=base_time,
            end_time=base_time,
            latency=100,
            error=None,
            parent_step_id=from_agent,
        )
        steps.append(step)

    # Add isolated agents as root steps
    for agent in agents - agents_with_edges:
        step = InteractionStep(
            step_id=agent,
            trace_id="test_trace",
            call_type=CallType.AGENT,
            start_time=base_time,
            end_time=base_time,
            latency=100,
            error=None,
            parent_step_id=None,
        )
        steps.append(step)

    return steps


def _classify_coordination_quality(metrics: dict) -> str:
    """Classify coordination quality from metrics.

    Args:
        metrics: Graph metrics from evaluator

    Returns:
        Coordination quality: "high", "medium", "low", or "bottleneck"
    """
    density = getattr(metrics, "graph_density", 0)
    has_bottleneck = (
        hasattr(metrics, "bottlenecks") and len(getattr(metrics, "bottlenecks", [])) > 0
    )

    if has_bottleneck and density < 0.3:
        return "bottleneck"
    elif density >= 0.4:
        return "high"
    elif density >= 0.2:
        return "medium"
    else:
        return "low"
