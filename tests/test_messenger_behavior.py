"""Behavioral tests for Messenger A2A communication.

Tests focus on OBSERVABLE BEHAVIOR, not implementation details:
1. Send message → receive response (the core contract)
2. Connection reuse for same URL (observable via mock call counts)
3. Connection isolation for different URLs
4. Cleanup releases resources
5. Errors propagate correctly

We mock at the network boundary (httpx + A2A SDK) to avoid actual HTTP calls,
but test the Messenger's behavior, not its internal implementation.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from a2a.client.errors import A2AClientError
from a2a.types import TaskState

from common.messenger import Messenger
from common.settings import A2ASettings


@pytest.fixture(autouse=True)
def mock_httpx():
    """Mock httpx to avoid actual HTTP connections in all tests."""
    with (
        patch("common.messenger.httpx.AsyncClient") as mock_client,
        patch("common.messenger.httpx.Timeout") as mock_timeout,
    ):
        mock_timeout.return_value = MagicMock()
        mock_client.return_value = MagicMock()
        yield {"client": mock_client, "timeout": mock_timeout}


def _create_mock_a2a_client(response_text: str = "agent response") -> MagicMock:
    """Create a mock A2A client that returns a completed task with given response."""
    client = MagicMock()
    client.close = AsyncMock()

    async def send_message_generator(*args, **kwargs):
        task = MagicMock()
        task.status.state = TaskState.completed
        task.artifacts = [MagicMock(parts=[MagicMock(root=MagicMock(text=response_text))])]
        yield (task, "completed")

    client.send_message = MagicMock(side_effect=lambda *a, **kw: send_message_generator())
    return client


class TestMessengerContract:
    """Test the core Messenger contract: send message, get response."""

    @pytest.mark.asyncio
    async def test_send_message_returns_agent_response(self):
        """GIVEN a connected agent, WHEN sending a message, THEN receive response text."""
        expected_response = "Hello from the agent!"

        with patch("common.messenger.ClientFactory") as mock_factory:
            mock_factory.connect = AsyncMock(
                return_value=_create_mock_a2a_client(expected_response)
            )

            messenger = Messenger()
            result = await messenger.send_message("http://agent:9010", "Hello")

            assert result == expected_response

    @pytest.mark.asyncio
    async def test_send_message_with_empty_artifacts_returns_empty_string(self):
        """GIVEN a task with no artifacts, WHEN completed, THEN return empty string."""
        with patch("common.messenger.ClientFactory") as mock_factory:
            client = MagicMock()
            client.close = AsyncMock()

            async def send_empty_response(*args, **kwargs):
                task = MagicMock()
                task.status.state = TaskState.completed
                task.artifacts = []  # No artifacts
                yield (task, "completed")

            client.send_message = MagicMock(side_effect=lambda *a, **kw: send_empty_response())
            mock_factory.connect = AsyncMock(return_value=client)

            messenger = Messenger()
            result = await messenger.send_message("http://agent:9010", "Hello")

            assert result == ""

    @pytest.mark.asyncio
    async def test_extensions_passed_to_agent(self):
        """GIVEN extensions list, WHEN sending message, THEN extensions forwarded to client."""
        with patch("common.messenger.ClientFactory") as mock_factory:
            mock_client = _create_mock_a2a_client()
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger()
            await messenger.send_message(
                "http://agent:9010", "Hello", extensions=["tracing", "metrics"]
            )

            # Verify extensions were passed through
            call_kwargs = mock_client.send_message.call_args.kwargs
            assert call_kwargs["extensions"] == ["tracing", "metrics"]


class TestConnectionManagement:
    """Test connection caching and isolation behavior."""

    @pytest.mark.asyncio
    async def test_same_url_reuses_connection(self):
        """GIVEN multiple messages to same URL, WHEN sending, THEN reuse single connection."""
        with patch("common.messenger.ClientFactory") as mock_factory:
            mock_factory.connect = AsyncMock(return_value=_create_mock_a2a_client())

            messenger = Messenger()
            for i in range(5):
                await messenger.send_message("http://agent:9010", f"message {i}")

            # Observable behavior: only 1 connection established
            assert mock_factory.connect.call_count == 1

    @pytest.mark.asyncio
    async def test_different_urls_get_separate_connections(self):
        """GIVEN messages to different URLs, WHEN sending, THEN each URL gets own connection."""
        with patch("common.messenger.ClientFactory") as mock_factory:
            mock_factory.connect = AsyncMock(return_value=_create_mock_a2a_client())

            messenger = Messenger()
            await messenger.send_message("http://agent-a:9010", "Hello A")
            await messenger.send_message("http://agent-b:9010", "Hello B")
            await messenger.send_message("http://agent-c:9010", "Hello C")

            # Observable behavior: 3 separate connections
            assert mock_factory.connect.call_count == 3
            connected_urls = [call[0][0] for call in mock_factory.connect.call_args_list]
            assert set(connected_urls) == {
                "http://agent-a:9010",
                "http://agent-b:9010",
                "http://agent-c:9010",
            }

    @pytest.mark.asyncio
    async def test_close_releases_all_connections(self):
        """GIVEN cached connections, WHEN close() called, THEN all connections released."""
        with patch("common.messenger.ClientFactory") as mock_factory:
            mock_client = _create_mock_a2a_client()
            mock_factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger()
            await messenger.send_message("http://agent-a:9010", "Hello")
            await messenger.send_message("http://agent-b:9010", "Hello")

            await messenger.close()

            # Observable behavior: both connections closed
            assert mock_client.close.call_count == 2


class TestTimeoutConfiguration:
    """Test that timeout settings are properly configured."""

    @pytest.mark.asyncio
    async def test_custom_timeout_settings_are_used(self):
        """GIVEN custom timeout settings, WHEN connecting, THEN settings are applied."""
        custom_settings = A2ASettings(timeout=99.0, connect_timeout=42.0)

        with patch("common.messenger.ClientFactory") as mock_factory:
            mock_factory.connect = AsyncMock(return_value=_create_mock_a2a_client())

            messenger = Messenger(a2a_settings=custom_settings)
            await messenger.send_message("http://agent:9010", "Hello")

            # Verify ClientConfig was passed (contains httpx client with timeout)
            call_kwargs = mock_factory.connect.call_args.kwargs
            assert "client_config" in call_kwargs
            assert call_kwargs["client_config"] is not None

    @pytest.mark.asyncio
    async def test_default_settings_work_without_configuration(self):
        """GIVEN no custom settings, WHEN sending message, THEN defaults work."""
        with patch("common.messenger.ClientFactory") as mock_factory:
            mock_factory.connect = AsyncMock(return_value=_create_mock_a2a_client())

            # No settings provided - should use defaults
            messenger = Messenger()
            result = await messenger.send_message("http://agent:9010", "Hello")

            assert result == "agent response"


class TestErrorHandling:
    """Test error propagation behavior."""

    @pytest.mark.asyncio
    async def test_a2a_client_error_propagates(self):
        """GIVEN A2A client error, WHEN sending message, THEN error propagates to caller."""
        with patch("common.messenger.ClientFactory") as mock_factory:
            mock_factory.connect = AsyncMock(side_effect=A2AClientError("Connection refused"))

            messenger = Messenger()

            with pytest.raises(A2AClientError, match="Connection refused"):
                await messenger.send_message("http://agent:9010", "Hello")

    @pytest.mark.asyncio
    async def test_send_error_propagates(self):
        """GIVEN error during send, WHEN iterating response, THEN error propagates."""
        with patch("common.messenger.ClientFactory") as mock_factory:
            client = MagicMock()
            client.close = AsyncMock()

            async def send_with_error(*args, **kwargs):
                raise A2AClientError("Send failed")
                yield  # Make it a generator

            client.send_message = MagicMock(side_effect=lambda *a, **kw: send_with_error())
            mock_factory.connect = AsyncMock(return_value=client)

            messenger = Messenger()

            with pytest.raises(A2AClientError, match="Send failed"):
                await messenger.send_message("http://agent:9010", "Hello")


class TestCleanupBehavior:
    """Test resource cleanup behavior."""

    @pytest.mark.asyncio
    async def test_close_is_idempotent(self):
        """GIVEN already closed messenger, WHEN close() called again, THEN no error."""
        messenger = Messenger()
        await messenger.close()
        await messenger.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_close_with_no_connections_succeeds(self):
        """GIVEN messenger with no connections, WHEN close() called, THEN succeeds."""
        messenger = Messenger()
        await messenger.close()  # Should not raise
