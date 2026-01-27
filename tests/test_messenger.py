"""Tests for Messenger with A2A SDK integration.

RED phase: These tests should FAIL initially since Messenger doesn't exist yet.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from green.messenger import Messenger


@pytest.fixture
def mock_client():
    """Mock A2A Client."""
    client = MagicMock()
    client.close = AsyncMock()
    client.send_message = MagicMock()
    return client


@pytest.fixture
def mock_client_factory():
    """Mock ClientFactory.connect."""
    with patch("green.messenger.ClientFactory") as factory:
        # Make connect an AsyncMock since ClientFactory.connect is async
        factory.connect = AsyncMock()
        yield factory


class TestMessengerInitialization:
    """Test Messenger initialization and client management."""

    async def test_messenger_uses_client_factory_connect(self, mock_client_factory, mock_client):
        """Messenger uses ClientFactory.connect() from a2a-sdk (not custom REST)."""
        mock_client_factory.connect.return_value = mock_client

        messenger = Messenger()
        await messenger.send_message("http://agent.example.com:9009", "Hello")

        # Verify ClientFactory.connect was called with correct URL
        mock_client_factory.connect.assert_called_once()
        call_args = mock_client_factory.connect.call_args
        assert call_args[0][0] == "http://agent.example.com:9009"

    async def test_messenger_caches_clients_per_url(self, mock_client_factory, mock_client):
        """Client caching per agent URL implemented."""
        mock_client_factory.connect.return_value = mock_client

        messenger = Messenger()
        # Send two messages to same URL
        await messenger.send_message("http://agent1.example.com:9009", "Hello 1")
        await messenger.send_message("http://agent1.example.com:9009", "Hello 2")

        # Should only connect once for same URL
        assert mock_client_factory.connect.call_count == 1

    async def test_messenger_creates_separate_clients_for_different_urls(self, mock_client_factory, mock_client):
        """Different URLs get different clients."""
        mock_client_factory.connect.return_value = mock_client

        messenger = Messenger()
        await messenger.send_message("http://agent1.example.com:9009", "Hello")
        await messenger.send_message("http://agent2.example.com:9009", "Hello")

        # Should connect twice for different URLs
        assert mock_client_factory.connect.call_count == 2


class TestMessengerMessageSending:
    """Test message sending with A2A SDK."""

    async def test_messenger_creates_messages_via_create_text_message_object(self, mock_client_factory, mock_client):
        """Messages created via create_text_message_object()."""
        mock_client_factory.connect.return_value = mock_client

        with patch("green.messenger.create_text_message_object") as mock_create:
            mock_message = MagicMock()
            mock_create.return_value = mock_message

            messenger = Messenger()
            await messenger.send_message("http://agent.example.com:9009", "Test message")

            # Verify create_text_message_object was called with correct text
            mock_create.assert_called_once_with(content="Test message")
            # Verify message was sent via client
            mock_client.send_message.assert_called_once_with(mock_message, extensions=None)

    async def test_messenger_extracts_response_from_completed_events(self, mock_client_factory, mock_client):
        """Response extracted from TaskState.completed events."""
        from a2a.types import Task, TaskState

        mock_client_factory.connect.return_value = mock_client

        # Create mock completed task
        completed_task = MagicMock(spec=Task)
        completed_task.status = MagicMock()
        completed_task.status.state = TaskState.completed
        mock_text_part = MagicMock()
        mock_text_part.text = "Response from agent"
        mock_part = MagicMock()
        mock_part.root = mock_text_part
        mock_artifact = MagicMock()
        mock_artifact.parts = [mock_part]
        completed_task.artifacts = [mock_artifact]

        # Mock send_message to return async iterator with completed task
        async def mock_send_iter(*args, **kwargs):
            yield (completed_task, None)

        mock_client.send_message.return_value = mock_send_iter()

        messenger = Messenger()
        response = await messenger.send_message("http://agent.example.com:9009", "Hello")

        assert response == "Response from agent"

    async def test_messenger_sends_extensions_header(self, mock_client_factory, mock_client):
        """Messenger sends X-A2A-Extensions activation headers."""
        mock_client_factory.connect.return_value = mock_client

        async def mock_send_iter(*args, **kwargs):
            from a2a.types import Task, TaskState

            task = MagicMock(spec=Task)
            task.status = MagicMock()
            task.status.state = TaskState.completed
            mock_text_part = MagicMock()
            mock_text_part.text = "Done"
            mock_part = MagicMock()
            mock_part.root = mock_text_part
            mock_artifact = MagicMock()
            mock_artifact.parts = [mock_part]
            task.artifacts = [mock_artifact]
            yield (task, None)

        mock_client.send_message.return_value = mock_send_iter()

        messenger = Messenger()
        await messenger.send_message("http://agent.example.com:9009", "Test")

        # Verify extensions parameter was passed
        call_kwargs = mock_client.send_message.call_args.kwargs
        assert "extensions" in call_kwargs


class TestMessengerCleanup:
    """Test Messenger cleanup functionality."""

    async def test_messenger_has_close_method(self):
        """Messenger.close() cleanup method for cached clients."""
        messenger = Messenger()
        # Should not raise - close method exists
        await messenger.close()

    async def test_messenger_close_closes_all_cached_clients(self, mock_client_factory, mock_client):
        """Executor calls await messenger.close() after trace collection."""
        mock_client_factory.connect.return_value = mock_client

        async def mock_send_iter(*args, **kwargs):
            from a2a.types import Task, TaskState

            task = MagicMock(spec=Task)
            task.status = MagicMock()
            task.status.state = TaskState.completed
            mock_text_part = MagicMock()
            mock_text_part.text = "Done"
            mock_part = MagicMock()
            mock_part.root = mock_text_part
            mock_artifact = MagicMock()
            mock_artifact.parts = [mock_part]
            task.artifacts = [mock_artifact]
            yield (task, None)

        mock_client.send_message.return_value = mock_send_iter()

        messenger = Messenger()
        # Create connections to two agents
        await messenger.send_message("http://agent1.example.com:9009", "Hello")
        await messenger.send_message("http://agent2.example.com:9009", "Hello")

        # Close should close all clients
        await messenger.close()

        # Both clients should have been closed
        assert mock_client.close.call_count == 2


class TestMessengerErrorHandling:
    """Test error handling in Messenger."""

    async def test_messenger_handles_a2a_protocol_errors(self, mock_client_factory, mock_client):
        """Proper error handling for A2A protocol errors."""
        from a2a.client.errors import A2AClientError

        mock_client_factory.connect.return_value = mock_client

        # Mock send_message to raise A2A error
        async def mock_send_error(*args, **kwargs):
            raise A2AClientError("Connection failed")
            yield  # Make it a generator

        mock_client.send_message.return_value = mock_send_error()

        messenger = Messenger()

        with pytest.raises(A2AClientError):
            await messenger.send_message("http://agent.example.com:9009", "Hello")
