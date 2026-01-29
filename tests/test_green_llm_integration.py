"""Integration tests for LLM API integration with fallback to rule-based evaluation."""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from green.evals.llm_judge import LLMJudgment
from green.models import CallType, InteractionStep


@pytest.fixture
def sample_steps() -> list[InteractionStep]:
    """Create sample interaction steps for testing."""
    return [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=1000,
        ),
        InteractionStep(
            step_id="step-2",
            trace_id="trace-1",
            call_type=CallType.TOOL,
            start_time=datetime(2024, 1, 1, 12, 0, 1),
            end_time=datetime(2024, 1, 1, 12, 0, 2),
            latency=1000,
        ),
    ]


@pytest.mark.asyncio
async def test_llm_evaluate_uses_temperature_zero(sample_steps: list[InteractionStep]) -> None:
    """Test that LLM evaluation uses temperature=0 for consistency."""
    from green.evals.llm_judge import llm_evaluate

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "overall_score": 0.8,
                        "reasoning": "Good coordination",
                        "coordination_quality": "high",
                        "strengths": ["Fast response"],
                        "weaknesses": [],
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("green.evals.llm_judge.get_llm_client", return_value=mock_client):
        await llm_evaluate(sample_steps)

    # Verify temperature=0 was used
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["temperature"] == 0


@pytest.mark.asyncio
async def test_llm_evaluate_fallback_when_api_unavailable(
    sample_steps: list[InteractionStep],
) -> None:
    """Test that evaluation falls back to rule-based when API is unavailable."""
    from green.evals.llm_judge import llm_evaluate

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=ConnectionError("API unavailable"))

    with patch("green.evals.llm_judge.get_llm_client", return_value=mock_client):
        result = await llm_evaluate(sample_steps)

    # Should return rule-based judgment
    assert isinstance(result, LLMJudgment)
    assert 0.0 <= result.overall_score <= 1.0
    assert result.reasoning != ""


@pytest.mark.asyncio
async def test_llm_evaluate_logs_warning_on_fallback(
    sample_steps: list[InteractionStep], caplog: pytest.LogCaptureFixture
) -> None:
    """Test that fallback logs warning, not error."""
    from green.evals.llm_judge import llm_evaluate

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=ConnectionError("API unavailable"))

    with patch("green.evals.llm_judge.get_llm_client", return_value=mock_client):
        await llm_evaluate(sample_steps)

    # Should log warning (not error)
    assert any(record.levelname == "WARNING" for record in caplog.records)
    assert not any(record.levelname == "ERROR" for record in caplog.records)


@pytest.mark.asyncio
async def test_llm_evaluate_handles_timeout_error(sample_steps: list[InteractionStep]) -> None:
    """Test that evaluation handles API timeout gracefully."""
    from green.evals.llm_judge import llm_evaluate

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=TimeoutError("Request timeout"))

    with patch("green.evals.llm_judge.get_llm_client", return_value=mock_client):
        result = await llm_evaluate(sample_steps)

    # Should return rule-based judgment instead of crashing
    assert isinstance(result, LLMJudgment)
    assert 0.0 <= result.overall_score <= 1.0


@pytest.mark.asyncio
async def test_llm_evaluate_handles_invalid_json(sample_steps: list[InteractionStep]) -> None:
    """Test that evaluation handles invalid JSON response gracefully."""
    from green.evals.llm_judge import llm_evaluate

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Not a valid JSON response"))]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("green.evals.llm_judge.get_llm_client", return_value=mock_client):
        result = await llm_evaluate(sample_steps)

    # Should return rule-based judgment instead of crashing
    assert isinstance(result, LLMJudgment)
    assert 0.0 <= result.overall_score <= 1.0


@pytest.mark.asyncio
async def test_llm_evaluate_with_additional_context(sample_steps: list[InteractionStep]) -> None:
    """Test that LLM evaluation accepts multi-plugin data (graph, text, latency outputs)."""
    from green.evals.llm_judge import llm_evaluate

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "overall_score": 0.75,
                        "reasoning": "Good coordination with minor issues",
                        "coordination_quality": "medium",
                        "strengths": ["Fast", "Accurate"],
                        "weaknesses": ["Minor delays"],
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Additional context from other evaluators
    graph_output = {"density": 0.7, "bottlenecks": []}
    latency_output = {"p50": 100, "p95": 200, "p99": 300}
    text_output = {"similarity_score": 0.85}

    with patch("green.evals.llm_judge.get_llm_client", return_value=mock_client):
        result = await llm_evaluate(
            sample_steps,
            graph_metrics=graph_output,
            latency_metrics=latency_output,
            text_metrics=text_output,
        )

    # Should successfully incorporate multi-plugin data
    assert isinstance(result, LLMJudgment)
    assert result.overall_score == 0.75


@pytest.mark.asyncio
async def test_llm_evaluate_task_outcome_assessment(sample_steps: list[InteractionStep]) -> None:
    """Test that LLM evaluation assesses whether coordination led to successful task completion."""
    from green.evals.llm_judge import llm_evaluate

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "overall_score": 0.9,
                        "reasoning": "Task completed successfully with efficient coordination",
                        "coordination_quality": "high",
                        "strengths": ["Task success", "Efficient"],
                        "weaknesses": [],
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Steps with successful outcome (no errors)
    successful_steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=1000,
            error=None,
        ),
    ]

    with patch("green.evals.llm_judge.get_llm_client", return_value=mock_client):
        result = await llm_evaluate(successful_steps, task_outcome="success")

    # Should assess task outcome
    assert isinstance(result, LLMJudgment)
    assert result.overall_score >= 0.7  # High score for successful task


@pytest.mark.asyncio
async def test_llm_evaluate_failed_task_outcome(sample_steps: list[InteractionStep]) -> None:
    """Test that LLM evaluation assesses failed task completion."""
    from green.evals.llm_judge import llm_evaluate

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "overall_score": 0.2,
                        "reasoning": "Task failed due to coordination issues",
                        "coordination_quality": "low",
                        "strengths": [],
                        "weaknesses": ["Task failure", "Errors"],
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Steps with errors
    failed_steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=1000,
            error="Connection failed",
        ),
    ]

    with patch("green.evals.llm_judge.get_llm_client", return_value=mock_client):
        result = await llm_evaluate(failed_steps, task_outcome="failure")

    # Should assess task failure
    assert isinstance(result, LLMJudgment)
    assert result.overall_score <= 0.3  # Low score for failed task


@pytest.mark.asyncio
async def test_rule_based_fallback_calculation() -> None:
    """Test that rule-based fallback provides reasonable assessment."""
    from green.evals.llm_judge import rule_based_evaluate

    # Test with good coordination (no errors, low latency)
    good_steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0, 100000),
            latency=100,
        ),
    ]

    result = rule_based_evaluate(good_steps)
    assert isinstance(result, LLMJudgment)
    assert result.overall_score >= 0.7  # Good coordination should score high

    # Test with poor coordination (errors, high latency)
    poor_steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 5),
            latency=5000,
            error="Connection timeout",
        ),
    ]

    result = rule_based_evaluate(poor_steps)
    assert isinstance(result, LLMJudgment)
    assert result.overall_score <= 0.4  # Poor coordination should score low
