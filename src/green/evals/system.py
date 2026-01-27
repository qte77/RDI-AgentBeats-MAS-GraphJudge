"""System performance metrics evaluation.

Implements latency metrics evaluator for comparative analysis within same system
environment. Computes percentiles and identifies performance bottlenecks.
"""

from __future__ import annotations

import statistics

from pydantic import BaseModel

from green.models import InteractionStep


class LatencyMetrics(BaseModel):
    """Latency metrics for performance analysis.

    WARNING: Latency values are only comparable within the same system/run.
    Do not compare latency metrics across different environments, systems,
    or time periods.

    Attributes:
        avg: Average latency in milliseconds
        p50: 50th percentile (median) latency in milliseconds
        p95: 95th percentile latency in milliseconds
        p99: 99th percentile latency in milliseconds
        slowest_agent: URL of slowest agent (if identifiable)
        warning: Comparability warning message
    """

    avg: float
    p50: float
    p95: float
    p99: float
    slowest_agent: str | None
    warning: str = "Latency values only comparable within same system/run"


def _empty_metrics() -> LatencyMetrics:
    """Return empty latency metrics when no data is available."""
    return LatencyMetrics(
        avg=0,
        p50=0,
        p95=0,
        p99=0,
        slowest_agent=None,
    )


def evaluate_latency(steps: list[InteractionStep]) -> LatencyMetrics:
    """Evaluate latency metrics from interaction steps.

    Reads latency from InteractionStep.latency field (auto-calculated by A2A)
    and computes percentiles and identifies performance bottlenecks.

    Args:
        steps: List of InteractionStep traces to analyze

    Returns:
        LatencyMetrics with percentiles and slowest agent identification
    """
    # Handle empty steps
    if not steps:
        return _empty_metrics()

    # Extract latency values, filtering out None
    latencies = [step.latency for step in steps if step.latency is not None]

    # Handle case where all latencies are None
    if not latencies:
        return _empty_metrics()

    # Compute average
    avg = statistics.mean(latencies)

    # Compute percentiles
    sorted_latencies = sorted(latencies)
    p50 = statistics.median(sorted_latencies)
    p95 = statistics.quantiles(sorted_latencies, n=100)[94] if len(sorted_latencies) > 1 else sorted_latencies[0]
    p99 = statistics.quantiles(sorted_latencies, n=100)[98] if len(sorted_latencies) > 1 else sorted_latencies[0]

    # Identify slowest agent (agent with highest latency)
    slowest_agent = None
    if steps:
        # Find step with maximum latency
        steps_with_latency = [step for step in steps if step.latency is not None]
        if steps_with_latency:
            slowest_step = max(steps_with_latency, key=lambda s: s.latency or 0)
            # For now, use step_id as identifier (URL would be in metadata)
            # In real implementation, this would extract agent URL from trace metadata
            slowest_agent = slowest_step.step_id

    return LatencyMetrics(
        avg=avg,
        p50=p50,
        p95=p95,
        p99=p99,
        slowest_agent=slowest_agent,
    )
