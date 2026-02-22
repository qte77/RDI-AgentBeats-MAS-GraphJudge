"""Tests for common TraceReporter for async trace collection.

RED phase: These tests should FAIL initially since common.trace_reporter doesn't exist yet.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.models import CallType, InteractionStep
from common.trace_reporter import TraceReporter


@pytest.fixture
def sample_trace_data():
    """Sample trace data for testing."""
    return [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime(2026, 1, 31, 10, 0, 0),
            end_time=datetime(2026, 1, 31, 10, 0, 1),
            latency=1000,
        ),
        InteractionStep(
            step_id="step-2",
            trace_id="trace-123",
            call_type=CallType.TOOL,
            start_time=datetime(2026, 1, 31, 10, 0, 1),
            end_time=datetime(2026, 1, 31, 10, 0, 2),
            latency=1000,
        ),
    ]


class TestTraceReporterInitialization:
    """Test TraceReporter initialization."""

    def test_trace_reporter_accepts_green_url(self):
        """TraceReporter initializes with Green agent URL."""
        reporter = TraceReporter(green_url="http://green:8000")
        assert reporter is not None

    def test_trace_reporter_has_default_timeout(self):
        """TraceReporter has default timeout for HTTP requests."""
        reporter = TraceReporter(green_url="http://green:8000")
        # Default timeout should be reasonable (e.g., 5 seconds)
        assert reporter._timeout >= 1.0


class TestTraceReporterSendTraces:
    """Test trace sending functionality."""

    @pytest.mark.asyncio
    async def test_trace_reporter_sends_to_green_traces_endpoint(self, sample_trace_data):
        """TraceReporter sends traces to Green's /traces endpoint."""
        with patch("common.trace_reporter.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            reporter = TraceReporter(green_url="http://green:8000")
            await reporter.send_traces(sample_trace_data)

            # Verify POST was called to /traces endpoint
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "http://green:8000/traces"

    @pytest.mark.asyncio
    async def test_trace_reporter_sends_traces_as_json(self, sample_trace_data):
        """TraceReporter sends traces as JSON payload."""
        with patch("common.trace_reporter.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            reporter = TraceReporter(green_url="http://green:8000")
            await reporter.send_traces(sample_trace_data)

            # Verify JSON payload
            call_kwargs = mock_client.post.call_args.kwargs
            assert "json" in call_kwargs
            json_data = call_kwargs["json"]
            assert "traces" in json_data
            assert len(json_data["traces"]) == 2

    @pytest.mark.asyncio
    async def test_trace_reporter_is_fire_and_forget(self, sample_trace_data):
        """Fire-and-forget pattern (non-blocking)."""
        with patch("common.trace_reporter.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            # Simulate slow network - should not block
            mock_client.post = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            reporter = TraceReporter(green_url="http://green:8000")

            # Should complete without waiting for response
            await reporter.send_traces(sample_trace_data)

            # Verify request was made
            mock_client.post.assert_called_once()


class TestTraceReporterErrorHandling:
    """Test graceful error handling."""

    @pytest.mark.asyncio
    async def test_trace_reporter_handles_green_unavailable(self, sample_trace_data):
        """Graceful handling of Green unavailability."""
        with patch("common.trace_reporter.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            # Simulate connection error
            mock_client.post = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            reporter = TraceReporter(green_url="http://green:8000")

            # Should not raise - graceful degradation
            try:
                await reporter.send_traces(sample_trace_data)
            except Exception as e:
                pytest.fail(f"send_traces should not raise on Green unavailability: {e}")

    @pytest.mark.asyncio
    async def test_trace_reporter_handles_timeout(self, sample_trace_data):
        """Graceful handling of timeout."""
        import httpx

        with patch("common.trace_reporter.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            # Simulate timeout
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            reporter = TraceReporter(green_url="http://green:8000")

            # Should not raise - graceful degradation
            try:
                await reporter.send_traces(sample_trace_data)
            except Exception as e:
                pytest.fail(f"send_traces should not raise on timeout: {e}")

    @pytest.mark.asyncio
    async def test_trace_reporter_handles_http_error(self, sample_trace_data):
        """Graceful handling of HTTP errors (4xx, 5xx)."""
        import httpx

        with patch("common.trace_reporter.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            # Simulate HTTP error response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.post = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Server error", request=MagicMock(), response=mock_response
                )
            )
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            reporter = TraceReporter(green_url="http://green:8000")

            # Should not raise - graceful degradation
            try:
                await reporter.send_traces(sample_trace_data)
            except Exception as e:
                pytest.fail(f"send_traces should not raise on HTTP error: {e}")


class TestTraceReporterEdgeCases:
    """Test edge cases."""

    @pytest.mark.asyncio
    async def test_trace_reporter_handles_empty_traces(self):
        """TraceReporter handles empty trace list."""
        with patch("common.trace_reporter.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            reporter = TraceReporter(green_url="http://green:8000")
            await reporter.send_traces([])

            # Should still make request with empty array
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_trace_reporter_serializes_datetime_to_iso(self, sample_trace_data):
        """TraceReporter serializes datetime fields to ISO format."""
        with patch("common.trace_reporter.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            reporter = TraceReporter(green_url="http://green:8000")
            await reporter.send_traces(sample_trace_data)

            # Verify datetime is serialized (should not raise)
            call_kwargs = mock_client.post.call_args.kwargs
            json_data = call_kwargs["json"]
            # Pydantic should serialize datetime to string
            assert isinstance(json_data["traces"][0]["start_time"], str)
