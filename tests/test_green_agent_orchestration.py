"""Tests for Agent evaluation orchestration."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from green.models import CallType, InteractionStep


@pytest.fixture
def sample_traces() -> list[InteractionStep]:
    """Provide sample interaction traces for testing."""
    return [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2026, 1, 27, 10, 0, 0),
            end_time=datetime(2026, 1, 27, 10, 0, 1),
            latency=1000,
        ),
        InteractionStep(
            step_id="step-2",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2026, 1, 27, 10, 0, 1),
            end_time=datetime(2026, 1, 27, 10, 0, 2),
            latency=1000,
        ),
    ]


@pytest.fixture
def mock_graph_evaluator() -> MagicMock:
    """Mock graph evaluator that returns Tier 1 metrics."""
    evaluator = MagicMock()
    evaluator.evaluate = AsyncMock(
        return_value={
            "graph_density": 0.5,
            "avg_centrality": 0.3,
            "bottlenecks": [],
            "isolated_agents": [],
        }
    )
    return evaluator


@pytest.fixture
def mock_llm_judge() -> MagicMock:
    """Mock LLM judge that returns Tier 2 semantic assessment."""
    judge = MagicMock()
    judge.evaluate = AsyncMock(
        return_value={
            "overall_score": 0.8,
            "reasoning": "Good coordination observed",
            "coordination_quality": "high",
            "strengths": ["efficient communication"],
            "weaknesses": [],
        }
    )
    return judge


@pytest.fixture
def mock_latency_evaluator() -> MagicMock:
    """Mock latency evaluator that returns Tier 2 performance metrics."""
    evaluator = MagicMock()
    evaluator.evaluate = AsyncMock(
        return_value={
            "avg_latency": 1000,
            "p50_latency": 1000,
            "p95_latency": 1000,
            "p99_latency": 1000,
            "slowest_agent": None,
        }
    )
    return evaluator


async def test_agent_orchestrates_all_evaluators(
    sample_traces: list[InteractionStep],
    mock_graph_evaluator: MagicMock,
    mock_llm_judge: MagicMock,
    mock_latency_evaluator: MagicMock,
) -> None:
    """Test that Agent coordinates calls to all three evaluators."""
    from green.agent import Agent

    agent = Agent(
        graph_evaluator=mock_graph_evaluator,
        llm_judge=mock_llm_judge,
        latency_evaluator=mock_latency_evaluator,
    )

    result = await agent.evaluate(sample_traces)

    # Verify all evaluators were called
    mock_graph_evaluator.evaluate.assert_called_once_with(sample_traces)
    mock_llm_judge.evaluate.assert_called_once()
    mock_latency_evaluator.evaluate.assert_called_once_with(sample_traces)

    # Verify result structure contains all tiers
    assert "tier1_graph" in result
    assert "tier2_llm" in result
    assert "tier2_latency" in result


async def test_agent_aggregates_results_into_structured_response(
    sample_traces: list[InteractionStep],
    mock_graph_evaluator: MagicMock,
    mock_llm_judge: MagicMock,
    mock_latency_evaluator: MagicMock,
) -> None:
    """Test that Agent aggregates evaluation results into structured response."""
    from green.agent import Agent

    agent = Agent(
        graph_evaluator=mock_graph_evaluator,
        llm_judge=mock_llm_judge,
        latency_evaluator=mock_latency_evaluator,
    )

    result = await agent.evaluate(sample_traces)

    # Verify structured response format
    assert isinstance(result, dict)
    assert result["tier1_graph"]["graph_density"] == 0.5
    assert result["tier2_llm"]["overall_score"] == 0.8
    assert result["tier2_latency"]["avg_latency"] == 1000


async def test_agent_passes_graph_results_to_llm_judge(
    sample_traces: list[InteractionStep],
    mock_graph_evaluator: MagicMock,
    mock_llm_judge: MagicMock,
    mock_latency_evaluator: MagicMock,
) -> None:
    """Test that Agent passes Tier 1 graph results to LLM judge for enriched context."""
    from green.agent import Agent

    agent = Agent(
        graph_evaluator=mock_graph_evaluator,
        llm_judge=mock_llm_judge,
        latency_evaluator=mock_latency_evaluator,
    )

    await agent.evaluate(sample_traces)

    # Verify LLM judge received graph results as context
    call_args = mock_llm_judge.evaluate.call_args
    assert call_args is not None
    assert "graph_results" in call_args.kwargs or len(call_args.args) > 1


async def test_agent_handles_evaluator_errors_gracefully(
    sample_traces: list[InteractionStep],
    mock_graph_evaluator: MagicMock,
    mock_llm_judge: MagicMock,
    mock_latency_evaluator: MagicMock,
) -> None:
    """Test that Agent handles evaluator errors without crashing."""
    from green.agent import Agent

    # Make graph evaluator fail
    mock_graph_evaluator.evaluate.side_effect = Exception("Graph evaluation failed")

    agent = Agent(
        graph_evaluator=mock_graph_evaluator,
        llm_judge=mock_llm_judge,
        latency_evaluator=mock_latency_evaluator,
    )

    result = await agent.evaluate(sample_traces)

    # Should still return a result with error information
    assert isinstance(result, dict)
    assert "tier1_graph" in result
    # Error should be captured in result
    assert "error" in result["tier1_graph"] or result["tier1_graph"] is None


async def test_agent_coordination_assessment_logic(
    sample_traces: list[InteractionStep],
    mock_graph_evaluator: MagicMock,
    mock_llm_judge: MagicMock,
    mock_latency_evaluator: MagicMock,
) -> None:
    """Test that Agent implements domain-specific coordination assessment logic."""
    from green.agent import Agent

    agent = Agent(
        graph_evaluator=mock_graph_evaluator,
        llm_judge=mock_llm_judge,
        latency_evaluator=mock_latency_evaluator,
    )

    result = await agent.evaluate(sample_traces)

    # Should include coordination assessment summary
    assert "coordination_summary" in result or "overall_assessment" in result


async def test_agent_evaluates_empty_traces(
    mock_graph_evaluator: MagicMock,
    mock_llm_judge: MagicMock,
    mock_latency_evaluator: MagicMock,
) -> None:
    """Test that Agent handles empty trace list gracefully."""
    from green.agent import Agent

    agent = Agent(
        graph_evaluator=mock_graph_evaluator,
        llm_judge=mock_llm_judge,
        latency_evaluator=mock_latency_evaluator,
    )

    result = await agent.evaluate([])

    # Should return a valid result structure even for empty traces
    assert isinstance(result, dict)
