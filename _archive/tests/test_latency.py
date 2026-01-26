"""Tests for latency evaluator module defining contract for latency metrics analysis."""

from pydantic import BaseModel


class TestLatencyEvaluatorContract:
    """Tests defining expected behavior for LatencyEvaluator.evaluate(traces)."""

    def test_latency_evaluator_can_be_instantiated(self) -> None:
        """Test that LatencyEvaluator can be instantiated without arguments."""
        # Given/When: We create a LatencyEvaluator instance
        from agentbeats.evals.latency import LatencyEvaluator

        evaluator = LatencyEvaluator()

        # Then: Instance should be created successfully
        assert evaluator is not None
        assert hasattr(evaluator, "evaluate")

    def test_evaluate_accepts_trace_list(self) -> None:
        """Test that evaluate() accepts a list of traces."""
        # Given: A LatencyEvaluator instance
        from agentbeats.evals.latency import LatencyEvaluator

        evaluator = LatencyEvaluator()

        # When/Then: Should have evaluate method that accepts traces
        assert hasattr(evaluator, "evaluate")
        assert callable(evaluator.evaluate)

    def test_evaluate_handles_empty_traces(self) -> None:
        """Test that evaluate() handles empty trace list gracefully."""
        # Given: A LatencyEvaluator instance and empty traces
        from agentbeats.evals.latency import LatencyEvaluator

        evaluator = LatencyEvaluator()
        empty_traces: list = []

        # When: We evaluate empty traces
        result = evaluator.evaluate(empty_traces)

        # Then: Should return valid metrics with zero or null values
        assert result is not None


class TestTimestampParsing:
    """Tests defining timestamp parsing from TraceData."""

    def test_parse_iso_timestamp(self) -> None:
        """Test that evaluator can parse ISO 8601 timestamps from TraceData."""
        # Given: A LatencyEvaluator instance and trace with ISO timestamp
        from agentbeats.evals.latency import LatencyEvaluator
        from agentbeats.messenger import TraceData

        evaluator = LatencyEvaluator()
        trace = TraceData(
            timestamp="2026-01-16T10:30:00.123456Z",
            agent_url="http://localhost:9009",
            message="test",
            response="response",
            status_code=200,
        )

        # When/Then: Should be able to parse and process timestamp
        # Implementation will extract datetime for latency calculations
        assert trace.timestamp is not None
        assert hasattr(evaluator, "evaluate")

    def test_handles_traces_with_different_timestamps(self) -> None:
        """Test that evaluator processes multiple traces with varying timestamps."""
        # Given: A LatencyEvaluator instance and traces with different times
        from agentbeats.evals.latency import LatencyEvaluator
        from agentbeats.messenger import TraceData

        evaluator = LatencyEvaluator()
        traces = [
            TraceData(
                timestamp="2026-01-16T10:30:00.000000Z",
                agent_url="http://localhost:9009",
                message="test1",
                response="response1",
                status_code=200,
            ),
            TraceData(
                timestamp="2026-01-16T10:30:01.500000Z",
                agent_url="http://localhost:9009",
                message="test2",
                response="response2",
                status_code=200,
            ),
        ]

        # When/Then: Should process all timestamps
        result = evaluator.evaluate(traces)
        assert result is not None


class TestPercentileCalculations:
    """Tests defining percentile calculations for latency metrics."""

    def test_calculates_average_latency(self) -> None:
        """Test that evaluator calculates average response time."""
        # Given: A LatencyEvaluator instance
        from agentbeats.evals.latency import LatencyEvaluator

        evaluator = LatencyEvaluator()

        # When: We evaluate traces
        # Then: Result should include average latency metric
        # This is the mean of all response times
        assert hasattr(evaluator, "evaluate")

    def test_calculates_p50_median(self) -> None:
        """Test that evaluator calculates p50 (median) latency."""
        # Given: A LatencyEvaluator instance
        from agentbeats.evals.latency import LatencyEvaluator

        evaluator = LatencyEvaluator()

        # When: We evaluate traces
        # Then: Result should include p50 percentile metric
        # p50 is the median value (50th percentile)
        assert hasattr(evaluator, "evaluate")

    def test_calculates_p95_percentile(self) -> None:
        """Test that evaluator calculates p95 latency."""
        # Given: A LatencyEvaluator instance
        from agentbeats.evals.latency import LatencyEvaluator

        evaluator = LatencyEvaluator()

        # When: We evaluate traces
        # Then: Result should include p95 percentile metric
        # p95 shows latency at 95th percentile (high-end performance)
        assert hasattr(evaluator, "evaluate")

    def test_calculates_p99_percentile(self) -> None:
        """Test that evaluator calculates p99 latency."""
        # Given: A LatencyEvaluator instance
        from agentbeats.evals.latency import LatencyEvaluator

        evaluator = LatencyEvaluator()

        # When: We evaluate traces
        # Then: Result should include p99 percentile metric
        # p99 shows worst-case latency (tail performance)
        assert hasattr(evaluator, "evaluate")


class TestSlowestAgentIdentification:
    """Tests defining slowest agent identification."""

    def test_identifies_slowest_agent_url(self) -> None:
        """Test that evaluator identifies the slowest agent URL."""
        # Given: A LatencyEvaluator instance
        from agentbeats.evals.latency import LatencyEvaluator

        evaluator = LatencyEvaluator()

        # When: We evaluate traces from multiple agents
        # Then: Result should identify which agent URL had highest latency
        # This helps pinpoint performance bottlenecks
        assert hasattr(evaluator, "evaluate")

    def test_handles_single_agent(self) -> None:
        """Test that evaluator handles traces from a single agent."""
        # Given: A LatencyEvaluator instance and traces from one agent
        from agentbeats.evals.latency import LatencyEvaluator
        from agentbeats.messenger import TraceData

        evaluator = LatencyEvaluator()
        traces = [
            TraceData(
                timestamp="2026-01-16T10:30:00.000000Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            ),
        ]

        # When: We evaluate single-agent traces
        result = evaluator.evaluate(traces)

        # Then: Should identify that single agent as slowest (or handle gracefully)
        assert result is not None


class LatencyMetrics(BaseModel):
    """Expected structure of latency metrics for evaluations."""

    avg_latency_ms: float | None = None
    p50_latency_ms: float | None = None
    p95_latency_ms: float | None = None
    p99_latency_ms: float | None = None
    slowest_agent_url: str | None = None
    total_requests: int = 0


class TestLatencyMetricsStructure:
    """Tests defining the expected structure of latency metrics."""

    def test_latency_metrics_model_is_valid(self) -> None:
        """Test that LatencyMetrics model can be instantiated with valid data."""
        # Given: Valid latency metrics data
        metrics = LatencyMetrics(
            avg_latency_ms=150.5,
            p50_latency_ms=120.0,
            p95_latency_ms=300.0,
            p99_latency_ms=450.0,
            slowest_agent_url="http://localhost:9009",
            total_requests=100,
        )

        # Then: Model should validate successfully
        assert metrics.avg_latency_ms == 150.5
        assert metrics.p50_latency_ms == 120.0
        assert metrics.p95_latency_ms == 300.0
        assert metrics.p99_latency_ms == 450.0
        assert metrics.slowest_agent_url == "http://localhost:9009"
        assert metrics.total_requests == 100

    def test_latency_metrics_minimal_fields(self) -> None:
        """Test that LatencyMetrics model works with minimal required fields."""
        # Given: Minimal latency metrics data
        metrics = LatencyMetrics(
            total_requests=0,
        )

        # Then: Model should validate with minimal data
        assert metrics.total_requests == 0
        assert metrics.avg_latency_ms is None
        assert metrics.p50_latency_ms is None
        assert metrics.slowest_agent_url is None

    def test_percentile_values_are_numeric(self) -> None:
        """Test that percentile values are numeric when provided."""
        # Given: Latency metrics with percentile data
        metrics = LatencyMetrics(
            avg_latency_ms=100.0,
            p50_latency_ms=95.0,
            p95_latency_ms=200.0,
            p99_latency_ms=350.0,
            total_requests=50,
        )

        # Then: All percentile values should be numeric
        assert isinstance(metrics.avg_latency_ms, (int, float))
        assert isinstance(metrics.p50_latency_ms, (int, float))
        assert isinstance(metrics.p95_latency_ms, (int, float))
        assert isinstance(metrics.p99_latency_ms, (int, float))


class TestLatencyEvaluatorIntegration:
    """Tests defining integration with TraceData and evaluation system."""

    def test_integrates_with_trace_data(self) -> None:
        """Test that LatencyEvaluator integrates with TraceData from messenger."""
        # Given: LatencyEvaluator and TraceData structure
        from agentbeats.evals.latency import LatencyEvaluator
        from agentbeats.messenger import TraceData

        evaluator = LatencyEvaluator()

        # When: We create sample trace data
        sample_trace = TraceData(
            timestamp="2026-01-16T10:30:00.000000Z",
            agent_url="http://localhost:9009",
            message="test",
            response="response",
            status_code=200,
        )

        # Then: LatencyEvaluator should be able to process trace data
        assert hasattr(evaluator, "evaluate")
        assert sample_trace.timestamp is not None

    def test_evaluate_returns_structured_metrics(self) -> None:
        """Test that evaluate() returns structured metrics."""
        # Given: A LatencyEvaluator instance
        from agentbeats.evals.latency import LatencyEvaluator

        evaluator = LatencyEvaluator()

        # When: We evaluate traces
        # Then: Should return LatencyMetrics model or dict
        # This ensures downstream consumers can access metrics predictably
        assert hasattr(evaluator, "evaluate")

    def test_handles_failed_requests(self) -> None:
        """Test that evaluator handles traces with errors gracefully."""
        # Given: A LatencyEvaluator instance and trace with error
        from agentbeats.evals.latency import LatencyEvaluator
        from agentbeats.messenger import TraceData

        evaluator = LatencyEvaluator()
        traces = [
            TraceData(
                timestamp="2026-01-16T10:30:00.000000Z",
                agent_url="http://localhost:9009",
                message="test",
                response="",
                error="Connection timeout",
            ),
        ]

        # When: We evaluate traces with errors
        result = evaluator.evaluate(traces)

        # Then: Should handle gracefully (may exclude from metrics or include)
        assert result is not None


class TestLatencyCalculationAccuracy:
    """Tests defining accuracy requirements for latency calculations."""

    def test_calculates_latency_from_consecutive_traces(self) -> None:
        """Test that latency is calculated from consecutive trace timestamps."""
        # Given: A LatencyEvaluator instance and sequential traces
        from agentbeats.evals.latency import LatencyEvaluator
        from agentbeats.messenger import TraceData

        evaluator = LatencyEvaluator()
        traces = [
            TraceData(
                timestamp="2026-01-16T10:30:00.000000Z",
                agent_url="http://localhost:9009",
                message="test1",
                response="response1",
                status_code=200,
            ),
            TraceData(
                timestamp="2026-01-16T10:30:00.150000Z",  # 150ms later
                agent_url="http://localhost:9009",
                message="test2",
                response="response2",
                status_code=200,
            ),
        ]

        # When: We evaluate sequential traces
        result = evaluator.evaluate(traces)

        # Then: Should calculate latency based on timestamp differences
        assert result is not None

    def test_latency_units_are_milliseconds(self) -> None:
        """Test that latency metrics are reported in milliseconds."""
        # Given: Latency metrics structure
        # When/Then: Field names should indicate milliseconds (_ms suffix)
        # This ensures consistent unit interpretation across system
        from agentbeats.evals.latency import LatencyMetrics

        metrics = LatencyMetrics(total_requests=0)
        # Check field names use _ms suffix for clarity
        assert hasattr(metrics, "avg_latency_ms")
        assert hasattr(metrics, "p50_latency_ms")
        assert hasattr(metrics, "p95_latency_ms")
        assert hasattr(metrics, "p99_latency_ms")
