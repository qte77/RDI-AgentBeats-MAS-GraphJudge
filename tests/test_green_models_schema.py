"""Tests for AgentBeats Pydantic schema models.

All models consolidated in green.models for single source of truth.
Tests validate Pydantic model_validate() is used consistently.
"""

import pytest
from pydantic import ValidationError

from green.models import (
    AgentBeatsOutputModel,
    GraphMetrics,
    GreenAgentOutput,
    ParticipantsModel,
    ResultModel,
)


class TestParticipantsModel:
    """Tests for ParticipantsModel."""

    def test_valid_agent_uuid(self):
        """Test creating participant with valid agent UUID."""
        p = ParticipantsModel.model_validate({"agent": "019b4d08-d84c-7a00-b2ec-4905ef7afc96"})
        assert str(p.agent) == "019b4d08-d84c-7a00-b2ec-4905ef7afc96"

    def test_valid_agent_uuid_v4(self):
        """Test creating participant with valid UUID v4 format."""
        p = ParticipantsModel.model_validate({"agent": "550e8400-e29b-41d4-a716-446655440000"})
        assert str(p.agent) == "550e8400-e29b-41d4-a716-446655440000"

    def test_invalid_agent_non_uuid_rejected(self):
        """Test validation fails for non-UUID identifier (A2A compliance)."""
        with pytest.raises(ValidationError):
            ParticipantsModel.model_validate({"agent": "green-agent"})

    def test_invalid_agent_malformed_uuid_rejected(self):
        """Test validation fails for malformed UUID."""
        with pytest.raises(ValidationError):
            ParticipantsModel.model_validate({"agent": "not-a-valid-uuid-format"})

    def test_missing_agent(self):
        """Test validation fails when agent is missing."""
        with pytest.raises(ValidationError):
            ParticipantsModel.model_validate({})


class TestGraphMetrics:
    """Tests for GraphMetrics."""

    def test_default_values(self):
        """Test creating graph metrics with defaults via model_validate."""
        metrics = GraphMetrics.model_validate({})
        assert metrics.graph_density == 0.0
        assert metrics.has_bottleneck is False
        assert metrics.bottlenecks == []
        assert metrics.coordination_quality == "low"

    def test_with_values(self):
        """Test creating graph metrics with values via model_validate."""
        metrics = GraphMetrics.model_validate(
            {
                "graph_density": 0.45,
                "has_bottleneck": True,
                "bottlenecks": ["agent-1"],
                "coordination_quality": "high",
            }
        )
        assert metrics.graph_density == 0.45
        assert metrics.has_bottleneck is True
        assert metrics.bottlenecks == ["agent-1"]
        assert metrics.coordination_quality == "high"

    def test_full_metrics_from_dict(self):
        """Test full graph metrics from dict using model_validate."""
        data = {
            "degree_centrality": {"agent-1": 0.6, "agent-2": 0.4},
            "betweenness_centrality": {"agent-1": 0.3, "agent-2": 0.2},
            "closeness_centrality": {"agent-1": 1.0, "agent-2": 0.67},
            "eigenvector_centrality": {"agent-1": 0.71, "agent-2": 0.5},
            "pagerank": {"agent-1": 0.45, "agent-2": 0.28},
            "graph_density": 0.45,
            "clustering_coefficient": 0.3,
            "connected_components": 1,
            "average_path_length": 1.5,
            "diameter": 2,
            "bottlenecks": [],
            "has_bottleneck": False,
            "isolated_agents": [],
            "over_centralized": False,
            "coordination_quality": "high",
        }
        metrics = GraphMetrics.model_validate(data)
        assert metrics.degree_centrality == {"agent-1": 0.6, "agent-2": 0.4}
        assert metrics.graph_density == 0.45


class TestResultModel:
    """Tests for ResultModel."""

    def test_valid_minimal(self):
        """Test creating minimal valid result via model_validate."""
        r = ResultModel.model_validate(
            {
                "pass_rate": 66.67,
                "time_used": 55.67,
                "max_score": 3,
            }
        )
        assert r.pass_rate == 66.67
        assert r.time_used == 55.67
        assert r.max_score == 3

    def test_valid_complete(self):
        """Test creating complete result with all fields via model_validate."""
        r = ResultModel.model_validate(
            {
                "pass_rate": 85.0,
                "time_used": 350.0,
                "max_score": 100,
                "score": 85.0,
                "domain": "coordination",
                "task_rewards": {"overall_score": 0.85, "graph_density": 0.45},
            }
        )
        assert r.domain == "coordination"
        assert r.score == 85.0
        assert r.task_rewards["overall_score"] == 0.85

    def test_missing_required_field(self):
        """Test validation fails when required field is missing."""
        with pytest.raises(ValidationError):
            ResultModel.model_validate({"pass_rate": 66.67, "time_used": 55.67})


class TestGreenAgentOutput:
    """Tests for GreenAgentOutput (coordination evaluation)."""

    def test_valid_output(self):
        """Test creating valid Green Agent coordination output via model_validate."""
        output = GreenAgentOutput.model_validate(
            {
                "overall_score": 0.85,
                "reasoning": "Agents demonstrated efficient task delegation.",
                "coordination_quality": "high",
                "strengths": ["Fast response times", "Clear delegation"],
                "weaknesses": ["Could optimize parallel execution"],
            }
        )
        assert output.overall_score == 0.85
        assert output.coordination_quality == "high"
        assert len(output.strengths) == 2
        assert len(output.weaknesses) == 1

    def test_with_nested_graph_metrics(self):
        """Test output with embedded graph metrics via model_validate."""
        output = GreenAgentOutput.model_validate(
            {
                "overall_score": 0.85,
                "reasoning": "Good coordination observed.",
                "coordination_quality": "high",
                "graph_metrics": {"graph_density": 0.45, "has_bottleneck": False},
            }
        )
        assert output.graph_metrics["graph_density"] == 0.45

    def test_with_nested_latency_metrics(self):
        """Test output with embedded latency metrics via model_validate."""
        output = GreenAgentOutput.model_validate(
            {
                "overall_score": 0.85,
                "reasoning": "Good coordination observed.",
                "coordination_quality": "high",
                "latency_metrics": {"avg_latency": 150.0, "p99_latency": 350.0},
            }
        )
        assert output.latency_metrics["avg_latency"] == 150.0

    def test_invalid_coordination_quality(self):
        """Test validation fails for invalid coordination_quality."""
        with pytest.raises(ValidationError):
            GreenAgentOutput.model_validate(
                {
                    "overall_score": 0.85,
                    "reasoning": "Test",
                    "coordination_quality": "invalid",
                }
            )

    def test_invalid_score_range(self):
        """Test validation fails for score outside 0-1 range."""
        with pytest.raises(ValidationError):
            GreenAgentOutput.model_validate(
                {
                    "overall_score": 1.5,
                    "reasoning": "Test",
                    "coordination_quality": "high",
                }
            )

    def test_model_validate_from_dict(self):
        """Test creating GreenAgentOutput via model_validate() from dict."""
        data = {
            "overall_score": 0.85,
            "reasoning": "Agents demonstrated efficient coordination.",
            "coordination_quality": "high",
            "strengths": ["Fast response times", "Clear delegation"],
            "weaknesses": ["Could optimize parallel execution"],
            "graph_metrics": {
                "graph_density": 0.45,
                "has_bottleneck": False,
                "bottlenecks": [],
            },
            "latency_metrics": {
                "avg_latency": 150.0,
                "p99_latency": 350.0,
            },
        }

        output = GreenAgentOutput.model_validate(data)

        assert output.overall_score == 0.85
        assert output.reasoning == "Agents demonstrated efficient coordination."
        assert output.coordination_quality == "high"
        assert output.strengths == ["Fast response times", "Clear delegation"]
        assert output.graph_metrics["graph_density"] == 0.45
        assert output.latency_metrics["avg_latency"] == 150.0

    def test_model_validate_json(self):
        """Test creating GreenAgentOutput via model_validate_json()."""
        json_str = """
        {
            "overall_score": 0.75,
            "reasoning": "Good coordination with minor issues.",
            "coordination_quality": "medium",
            "strengths": ["Task completion"],
            "weaknesses": ["High latency"]
        }
        """

        output = GreenAgentOutput.model_validate_json(json_str)

        assert output.overall_score == 0.75
        assert output.coordination_quality == "medium"


class TestAgentBeatsOutputModel:
    """Tests for AgentBeatsOutputModel."""

    def test_valid_minimal(self):
        """Test creating minimal valid output via model_validate."""
        output = AgentBeatsOutputModel.model_validate(
            {
                "participants": {"agent": "019b4d08-d84c-7a00-b2ec-4905ef7afc96"},
                "results": [{"pass_rate": 66.67, "time_used": 55.67, "max_score": 3}],
            }
        )
        assert output.participants.agent == "019b4d08-d84c-7a00-b2ec-4905ef7afc96"
        assert output.results[0].pass_rate == 66.67

    def test_model_validate_dict(self):
        """Test validating from dictionary using model_validate."""
        data = {
            "participants": {"agent": "019b4d08-d84c-7a00-b2ec-4905ef7afc96"},
            "results": [
                {
                    "domain": "coordination",
                    "score": 85.0,
                    "max_score": 100,
                    "pass_rate": 85.0,
                    "task_rewards": {"overall_score": 0.85, "graph_density": 0.45},
                    "time_used": 350.0,
                }
            ],
        }
        output = AgentBeatsOutputModel.model_validate(data)
        assert output.results[0].domain == "coordination"
        assert output.results[0].score == 85.0

    def test_empty_results_array_rejected(self):
        """Test validation fails for empty results array (min_length=1)."""
        with pytest.raises(ValidationError):
            AgentBeatsOutputModel.model_validate(
                {
                    "participants": {"agent": "019b4d08-d84c-7a00-b2ec-4905ef7afc96"},
                    "results": [],
                }
            )

    def test_to_json(self):
        """Test JSON serialization."""
        output = AgentBeatsOutputModel.model_validate(
            {
                "participants": {"agent": "019b4d08-d84c-7a00-b2ec-4905ef7afc96"},
                "results": [{"pass_rate": 66.67, "time_used": 55.67, "max_score": 3}],
            }
        )
        json_str = output.to_json()
        assert "participants" in json_str
        assert "019b4d08-d84c-7a00-b2ec-4905ef7afc96" in json_str

    def test_to_dict(self):
        """Test dictionary export."""
        output = AgentBeatsOutputModel.model_validate(
            {
                "participants": {"agent": "019b4d08-d84c-7a00-b2ec-4905ef7afc96"},
                "results": [{"pass_rate": 66.67, "time_used": 55.67, "max_score": 3}],
            }
        )
        data = output.to_dict()
        assert isinstance(data, dict)
        assert data["participants"]["agent"] == "019b4d08-d84c-7a00-b2ec-4905ef7afc96"


class TestFromGreenOutput:
    """Tests for from_green_output factory method."""

    def test_high_coordination(self):
        """Test creating output from high coordination Green output."""
        green_output = GreenAgentOutput.model_validate(
            {
                "overall_score": 0.85,
                "reasoning": "Agents demonstrated efficient task delegation.",
                "coordination_quality": "high",
                "strengths": ["Fast response times", "Clear delegation"],
                "weaknesses": ["Could optimize parallel execution"],
                "graph_metrics": {"graph_density": 0.45},
            }
        )

        output = AgentBeatsOutputModel.from_green_output(
            green_output=green_output,
            agent_id="019b4d08-d84c-7a00-b2ec-4905ef7afc96",
            time_used=350.0,
        )

        assert output.participants.agent == "019b4d08-d84c-7a00-b2ec-4905ef7afc96"
        assert output.results[0].pass_rate == 85.0
        assert output.results[0].score == 85.0
        assert output.results[0].task_rewards["overall_score"] == 0.85
        assert output.results[0].task_rewards["graph_density"] == 0.45
        assert output.results[0].task_rewards["coordination_quality"] == 1.0

    def test_from_dict_input(self):
        """Test from_green_output handles dict input with model_validate."""
        green_dict = {
            "overall_score": 0.85,
            "reasoning": "Test",
            "coordination_quality": "high",
        }

        output = AgentBeatsOutputModel.from_green_output(
            green_output=green_dict,
            agent_id="test-agent",
        )

        assert output.results[0].pass_rate == 85.0

    def test_low_coordination(self):
        """Test creating output from low coordination Green output."""
        green_output = GreenAgentOutput.model_validate(
            {
                "overall_score": 0.25,
                "reasoning": "Significant coordination issues observed.",
                "coordination_quality": "low",
                "strengths": ["Agents attempted communication"],
                "weaknesses": ["Multiple errors", "High latency"],
            }
        )

        output = AgentBeatsOutputModel.from_green_output(
            green_output=green_output,
            agent_id="019b4d08-d84c-7a00-b2ec-4905ef7afc96",
            time_used=500.0,
        )

        assert output.results[0].pass_rate == 25.0
        assert output.results[0].score == 25.0
        assert output.results[0].task_rewards["coordination_quality"] == 0.33


class TestFromEvaluationResults:
    """Tests for from_evaluation_results factory method."""

    def test_with_tiered_results(self):
        """Test creating output from tiered evaluation results."""
        evaluation_results = {
            "tier1_graph": {
                "graph_density": 0.45,
                "has_bottleneck": False,
                "bottlenecks": [],
                "coordination_quality": "high",
            },
            "tier2_llm": {
                "overall_score": 0.85,
                "reasoning": "Excellent coordination observed.",
                "coordination_quality": "high",
                "strengths": ["Fast response times", "Clear delegation"],
                "weaknesses": ["Could optimize parallel execution"],
            },
            "tier2_latency": {
                "avg_latency": 150.0,
                "p50_latency": 120.0,
                "p95_latency": 280.0,
                "p99_latency": 350.0,
            },
        }

        output = AgentBeatsOutputModel.from_evaluation_results(
            evaluation_results=evaluation_results,
            agent_id="green-agent",
        )

        assert output.participants.agent == "green-agent"
        assert output.results[0].pass_rate == 85.0
        assert output.results[0].time_used == 350.0
        assert output.results[0].task_rewards["overall_score"] == 0.85
        assert output.results[0].task_rewards["graph_density"] == 0.45

        detail = output.results[0].detail
        if hasattr(detail, "model_dump"):
            detail = detail.model_dump()
        assert detail["reasoning"] == "Excellent coordination observed."
        assert detail["strengths"] == ["Fast response times", "Clear delegation"]

    def test_low_coordination_results(self):
        """Test with low coordination classification."""
        evaluation_results = {
            "tier2_llm": {
                "overall_score": 0.25,
                "reasoning": "Poor coordination observed.",
                "coordination_quality": "low",
                "strengths": [],
                "weaknesses": ["Multiple errors", "High latency"],
            },
            "tier2_latency": {"p99_latency": 500.0},
        }

        output = AgentBeatsOutputModel.from_evaluation_results(
            evaluation_results=evaluation_results,
        )

        assert output.results[0].pass_rate == 25.0
        assert output.results[0].task_rewards["coordination_quality"] == 0.33

    def test_missing_optional_tiers(self):
        """Test with missing optional tier results."""
        evaluation_results = {
            "tier2_llm": {
                "overall_score": 0.5,
                "reasoning": "Moderate coordination.",
                "coordination_quality": "medium",
            },
        }

        output = AgentBeatsOutputModel.from_evaluation_results(
            evaluation_results=evaluation_results,
        )

        assert output.results[0].pass_rate == 50.0
        detail = output.results[0].detail
        if hasattr(detail, "model_dump"):
            detail = detail.model_dump()
        assert detail["graph_metrics"] is None
        assert detail["latency_metrics"] is None
