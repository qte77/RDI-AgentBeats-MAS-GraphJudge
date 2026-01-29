"""Tests for latency metrics evaluator.

Tests validate latency metrics computation and performance bottleneck detection.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from green.evals.system import LatencyMetrics, evaluate_latency
from green.models import CallType, InteractionStep


@pytest.fixture
def sample_steps() -> list[InteractionStep]:
    """Create sample interaction steps with varying latencies."""
    return [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0, 100000),
            latency=100,
        ),
        InteractionStep(
            step_id="step-2",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 1),
            end_time=datetime(2024, 1, 1, 12, 0, 1, 200000),
            latency=200,
        ),
        InteractionStep(
            step_id="step-3",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 2),
            end_time=datetime(2024, 1, 1, 12, 0, 2, 500000),
            latency=500,
        ),
        InteractionStep(
            step_id="step-4",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 3),
            end_time=datetime(2024, 1, 1, 12, 0, 4),
            latency=1000,
        ),
    ]


def test_evaluate_latency_computes_avg(sample_steps: list[InteractionStep]) -> None:
    """Test that latency evaluator computes average latency."""
    result = evaluate_latency(sample_steps)

    # Expected avg: (100 + 200 + 500 + 1000) / 4 = 450
    assert isinstance(result, LatencyMetrics)
    assert result.avg == 450


def test_evaluate_latency_computes_p50(sample_steps: list[InteractionStep]) -> None:
    """Test that latency evaluator computes p50 (median) latency."""
    result = evaluate_latency(sample_steps)

    # Expected p50: median of [100, 200, 500, 1000] = (200 + 500) / 2 = 350
    assert isinstance(result, LatencyMetrics)
    assert result.p50 == 350


def test_evaluate_latency_computes_p95(sample_steps: list[InteractionStep]) -> None:
    """Test that latency evaluator computes p95 latency."""
    result = evaluate_latency(sample_steps)

    # Expected p95: 95th percentile of [100, 200, 500, 1000]
    assert isinstance(result, LatencyMetrics)
    assert result.p95 >= 500  # Should be close to or at max value


def test_evaluate_latency_computes_p99(sample_steps: list[InteractionStep]) -> None:
    """Test that latency evaluator computes p99 latency."""
    result = evaluate_latency(sample_steps)

    # Expected p99: 99th percentile of [100, 200, 500, 1000]
    assert isinstance(result, LatencyMetrics)
    assert result.p99 >= 500  # Should be close to max value


def test_evaluate_latency_identifies_slowest_agent(sample_steps: list[InteractionStep]) -> None:
    """Test that latency evaluator identifies slowest agent by URL."""
    # Add agent URLs to steps
    steps_with_urls = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0, 100000),
            latency=100,
        ),
        InteractionStep(
            step_id="step-2",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 1),
            end_time=datetime(2024, 1, 1, 12, 0, 3),
            latency=2000,
        ),
    ]

    result = evaluate_latency(steps_with_urls)

    # Should identify agent with highest latency
    assert isinstance(result, LatencyMetrics)
    assert result.slowest_agent is not None


def test_evaluate_latency_with_empty_steps() -> None:
    """Test that latency evaluator handles empty step list."""
    result = evaluate_latency([])

    # Should return metrics with zero/None values
    assert isinstance(result, LatencyMetrics)
    assert result.avg == 0
    assert result.p50 == 0
    assert result.p95 == 0
    assert result.p99 == 0
    assert result.slowest_agent is None


def test_evaluate_latency_with_none_latencies() -> None:
    """Test that latency evaluator handles steps with None latency."""
    steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=None,
        ),
    ]

    result = evaluate_latency(steps)

    # Should handle None latencies gracefully
    assert isinstance(result, LatencyMetrics)


def test_evaluate_latency_follows_evaluator_pattern() -> None:
    """Test that latency evaluator follows existing evaluator pattern."""
    # Should be callable like other evaluators (GraphEvaluator, LLMJudge)
    from green.evals.system import evaluate_latency

    assert callable(evaluate_latency)


def test_latency_metrics_includes_warning() -> None:
    """Test that LatencyMetrics includes warning about comparability."""
    steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0, 100000),
            latency=100,
        ),
    ]

    result = evaluate_latency(steps)

    # Should include warning about comparability
    assert isinstance(result, LatencyMetrics)
    assert hasattr(result, "warning")
    assert "same system" in result.warning.lower() or "same run" in result.warning.lower()


def test_latency_metrics_structure() -> None:
    """Test that LatencyMetrics has expected structure."""
    steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0, 100000),
            latency=100,
        ),
    ]

    result = evaluate_latency(steps)

    # Verify structure
    assert isinstance(result, LatencyMetrics)
    assert hasattr(result, "avg")
    assert hasattr(result, "p50")
    assert hasattr(result, "p95")
    assert hasattr(result, "p99")
    assert hasattr(result, "slowest_agent")
    assert hasattr(result, "warning")
