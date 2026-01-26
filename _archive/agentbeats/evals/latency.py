"""Latency metrics evaluator for performance analysis."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from agentbeats.messenger import TraceData


class LatencyMetrics(BaseModel):
    """Expected structure of latency metrics for evaluations."""

    avg_latency_ms: float | None = None
    p50_latency_ms: float | None = None
    p95_latency_ms: float | None = None
    p99_latency_ms: float | None = None
    slowest_agent_url: str | None = None
    total_requests: int = 0


class LatencyEvaluator:
    """Evaluates latency metrics from agent interaction traces."""

    def evaluate(self, traces: list[TraceData]) -> LatencyMetrics:
        """Evaluate latency metrics from traces.

        Args:
            traces: List of TraceData objects representing agent interactions

        Returns:
            LatencyMetrics object with performance metrics
        """
        # Handle empty traces
        if not traces:
            return LatencyMetrics(total_requests=0)

        # Parse timestamps and calculate latencies
        latencies: list[float] = []
        agent_latencies: dict[str, list[float]] = {}

        for i in range(len(traces) - 1):
            try:
                # Parse timestamps
                t1 = datetime.fromisoformat(traces[i].timestamp.replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(traces[i + 1].timestamp.replace("Z", "+00:00"))

                # Calculate latency in milliseconds
                latency_ms = (t2 - t1).total_seconds() * 1000

                latencies.append(latency_ms)

                # Track per-agent latencies
                agent_url = traces[i].agent_url
                if agent_url not in agent_latencies:
                    agent_latencies[agent_url] = []
                agent_latencies[agent_url].append(latency_ms)

            except (ValueError, AttributeError):
                # Skip traces with invalid timestamps
                continue

        # If no valid latencies calculated, return minimal metrics
        if not latencies:
            return LatencyMetrics(total_requests=len(traces))

        # Sort latencies for percentile calculations
        sorted_latencies = sorted(latencies)

        # Calculate average
        avg_latency = sum(sorted_latencies) / len(sorted_latencies)

        # Calculate percentiles
        p50 = self._percentile(sorted_latencies, 50)
        p95 = self._percentile(sorted_latencies, 95)
        p99 = self._percentile(sorted_latencies, 99)

        # Identify slowest agent
        slowest_agent = None
        if agent_latencies:
            slowest_agent = max(
                agent_latencies.items(),
                key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            )[0]

        return LatencyMetrics(
            avg_latency_ms=avg_latency,
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            slowest_agent_url=slowest_agent,
            total_requests=len(traces),
        )

    def _percentile(self, sorted_values: list[float], percentile: int) -> float:
        """Calculate percentile from sorted values.

        Args:
            sorted_values: List of values sorted in ascending order
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        if not sorted_values:
            return 0.0

        index = (percentile / 100) * (len(sorted_values) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)

        # Linear interpolation between values
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
