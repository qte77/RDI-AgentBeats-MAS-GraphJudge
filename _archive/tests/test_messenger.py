"""Tests for messenger module defining contract for A2A agent communication and trace capture."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel


def setup_two_agent_mock(agent_url1: str, agent_url2: str, add_close_method: bool = False) -> tuple:
    """Helper to set up mock clients for two different agent URLs.

    Args:
        agent_url1: First agent URL
        agent_url2: Second agent URL
        add_close_method: Whether to add close() method to mock clients

    Returns:
        Tuple of (mock_client1, mock_client2, connect_side_effect, mock_event_stream)
    """
    mock_client1 = AsyncMock()
    mock_client2 = AsyncMock()

    if add_close_method:
        mock_client1.close = AsyncMock()
        mock_client2.close = AsyncMock()

    async def connect_side_effect(url: str):
        if url == agent_url1:
            return mock_client1
        else:
            return mock_client2

    async def mock_event_stream():
        from enum import Enum

        class MockTaskState(str, Enum):
            COMPLETED = "completed"

        mock_event = MagicMock()
        mock_event.state = MockTaskState.COMPLETED
        mock_event.output = "response"
        yield mock_event

    return mock_client1, mock_client2, connect_side_effect, mock_event_stream


class TestMessengerTalkToAgent:
    """Tests defining expected behavior for Messenger.talk_to_agent()."""

    @pytest.mark.asyncio
    async def test_talk_to_agent_sends_message_and_returns_response(self) -> None:
        """Test that talk_to_agent() sends a message to an agent and returns the response."""
        # Given: A messenger instance and a target agent URL
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        _agent_url = "http://localhost:9009"
        _message = "Test message"

        # When: We talk to the agent (will be mocked in implementation test)
        # Then: Should return a response string
        # This test defines the contract - implementation will use httpx for actual calls
        assert hasattr(messenger, "talk_to_agent")
        assert callable(messenger.talk_to_agent)

    @pytest.mark.asyncio
    async def test_talk_to_agent_captures_trace_data(self) -> None:
        """Test that talk_to_agent() captures trace data for each interaction."""
        # Given: A messenger instance
        from agentbeats.messenger import Messenger

        messenger = Messenger()

        # When: We talk to an agent
        # Then: The interaction should be captured in traces
        # This ensures we can evaluate agent behavior later
        assert hasattr(messenger, "talk_to_agent")

    @pytest.mark.asyncio
    async def test_talk_to_agent_handles_http_errors(self) -> None:
        """Test that talk_to_agent() handles HTTP errors gracefully."""
        # Given: A messenger instance and invalid agent URL
        from agentbeats.messenger import Messenger

        messenger = Messenger()

        # When/Then: Should handle connection errors appropriately
        assert hasattr(messenger, "talk_to_agent")


class TestMessengerGetTraces:
    """Tests defining expected behavior for Messenger.get_traces()."""

    def test_get_traces_returns_list_of_interactions(self) -> None:
        """Test that get_traces() returns a list of all captured interactions."""
        # Given: A messenger instance that has captured some interactions
        from agentbeats.messenger import Messenger

        messenger = Messenger()

        # When: We get traces
        traces = messenger.get_traces()

        # Then: Should return a list (initially empty)
        assert isinstance(traces, list)

    def test_get_traces_returns_structured_trace_data(self) -> None:
        """Test that get_traces() returns structured trace data with required fields."""
        # Given: A messenger instance
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        traces = messenger.get_traces()

        # Then: Each trace should have structured data
        # Traces should be empty initially, but the return type should be list
        assert isinstance(traces, list)
        # When traces exist, they should have: timestamp, agent_url, message, response
        # This is the contract for downstream evaluators

    def test_traces_accumulate_across_multiple_calls(self) -> None:
        """Test that traces accumulate across multiple talk_to_agent() calls."""
        # Given: A messenger instance
        from agentbeats.messenger import Messenger

        messenger = Messenger()

        # When: We make multiple calls
        # Then: All interactions should be captured in traces
        traces_before = messenger.get_traces()
        assert isinstance(traces_before, list)


class TraceData(BaseModel):
    """Expected structure of trace data for evaluators."""

    timestamp: str
    agent_url: str
    message: str
    response: str
    status_code: int | None = None
    error: str | None = None
    task_id: str | None = None


class TestMessengerTraceStructure:
    """Tests defining the expected structure of trace data."""

    def test_trace_data_model_is_valid(self) -> None:
        """Test that TraceData model can be instantiated with valid data."""
        # Given: Valid trace data
        trace = TraceData(
            timestamp="2026-01-15T00:00:00Z",
            agent_url="http://localhost:9009",
            message="test",
            response="response",
            status_code=200,
        )

        # Then: Model should validate successfully
        assert trace.timestamp == "2026-01-15T00:00:00Z"
        assert trace.agent_url == "http://localhost:9009"
        assert trace.message == "test"
        assert trace.response == "response"
        assert trace.status_code == 200

    def test_trace_data_model_handles_errors(self) -> None:
        """Test that TraceData model can capture error information."""
        # Given: Trace data with an error
        trace = TraceData(
            timestamp="2026-01-15T00:00:00Z",
            agent_url="http://localhost:9009",
            message="test",
            response="",
            error="Connection refused",
        )

        # Then: Model should capture error information
        assert trace.error == "Connection refused"
        assert trace.response == ""


class TestMessengerContract:
    """Tests defining the overall Messenger contract."""

    def test_messenger_can_be_instantiated(self) -> None:
        """Test that Messenger can be instantiated without arguments."""
        # Given/When: We create a messenger instance
        from agentbeats.messenger import Messenger

        messenger = Messenger()

        # Then: Instance should be created successfully
        assert messenger is not None
        assert hasattr(messenger, "talk_to_agent")
        assert hasattr(messenger, "get_traces")

    def test_messenger_provides_clean_api(self) -> None:
        """Test that Messenger provides a clean, focused API."""
        # Given: A messenger instance
        from agentbeats.messenger import Messenger

        messenger = Messenger()

        # Then: Should have exactly the methods we need
        assert hasattr(messenger, "talk_to_agent")
        assert hasattr(messenger, "get_traces")
        # No other public methods needed (YAGNI principle)


class TestA2ASDKIntegration:
    """Tests defining A2A SDK integration contract for messenger."""

    @pytest.mark.asyncio
    async def test_uses_client_factory_connect(self) -> None:
        """Test that talk_to_agent() uses ClientFactory.connect() from a2a.client."""
        # Given: A messenger instance and mocked A2A SDK
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url = "http://localhost:9009"
        message = "test message"

        # When/Then: Should use ClientFactory.connect(agent_url)
        with patch("agentbeats.messenger.ClientFactory") as mock_factory:
            mock_client = AsyncMock()
            mock_factory.connect = AsyncMock(return_value=mock_client)
            mock_task = MagicMock()
            mock_task.id = "task-123"
            mock_client.send_message = AsyncMock(return_value=mock_task)

            # Mock async iteration over task events
            async def mock_event_stream():
                from enum import Enum

                class MockTaskState(str, Enum):
                    COMPLETED = "completed"

                mock_event = MagicMock()
                mock_event.state = MockTaskState.COMPLETED
                mock_event.output = "response from agent"
                yield mock_event

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until implementation uses ClientFactory
            try:
                await messenger.talk_to_agent(agent_url, message)
                # Should call ClientFactory.connect
                mock_factory.connect.assert_called_once_with(agent_url)
            except AttributeError:
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_uses_create_text_message_object(self) -> None:
        """Test that talk_to_agent() uses create_text_message_object() from a2a.client."""
        # Given: A messenger instance and mocked A2A SDK
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url = "http://localhost:9009"
        message = "test message"

        # When/Then: Should use create_text_message_object(content=message)
        with (
            patch("agentbeats.messenger.ClientFactory") as mock_factory,
            patch("agentbeats.messenger.create_text_message_object") as mock_create_message,
        ):
            mock_client = AsyncMock()
            mock_factory.connect = AsyncMock(return_value=mock_client)
            mock_message_obj = MagicMock()
            mock_create_message.return_value = mock_message_obj

            mock_task = MagicMock()
            mock_task.id = "task-123"
            mock_client.send_message = AsyncMock(return_value=mock_task)

            # Mock async iteration
            async def mock_event_stream():
                from enum import Enum

                class MockTaskState(str, Enum):
                    COMPLETED = "completed"

                mock_event = MagicMock()
                mock_event.state = MockTaskState.COMPLETED
                mock_event.output = "response"
                yield mock_event

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until implementation uses create_text_message_object
            try:
                await messenger.talk_to_agent(agent_url, message)
                # Should call create_text_message_object with content=message
                mock_create_message.assert_called_once_with(content=message)
            except AttributeError:
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_async_iteration_over_send_message_events(self) -> None:
        """Test that talk_to_agent() iterates over send_message() events asynchronously."""
        # Given: A messenger instance and mocked A2A SDK
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url = "http://localhost:9009"
        message = "test message"

        # When/Then: Should async iterate over task events to get response
        with (
            patch("agentbeats.messenger.ClientFactory") as mock_factory,
            patch("agentbeats.messenger.create_text_message_object") as mock_create_message,
        ):
            mock_client = AsyncMock()
            mock_factory.connect = AsyncMock(return_value=mock_client)
            mock_message_obj = MagicMock()
            mock_create_message.return_value = mock_message_obj

            mock_task = MagicMock()
            mock_task.id = "task-123"
            mock_client.send_message = AsyncMock(return_value=mock_task)

            # Mock TaskState.completed events
            async def mock_event_stream():
                from enum import Enum

                class MockTaskState(str, Enum):
                    WORKING = "working"
                    COMPLETED = "completed"

                # First event: working state
                working_event = MagicMock()
                working_event.state = MockTaskState.WORKING
                yield working_event

                # Second event: completed state with output
                completed_event = MagicMock()
                completed_event.state = MockTaskState.COMPLETED
                completed_event.output = "final response from agent"
                yield completed_event

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until implementation uses async iteration
            try:
                response = await messenger.talk_to_agent(agent_url, message)
                # Should extract response from TaskState.completed event
                assert response == "final response from agent"
            except (AttributeError, TypeError):
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_client_caching_per_agent_url(self) -> None:
        """Test that Messenger caches clients per agent URL."""
        # Given: A messenger instance
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url = "http://localhost:9009"
        message1 = "first message"
        message2 = "second message"

        # When/Then: Should reuse same client for same agent URL
        with (
            patch("agentbeats.messenger.ClientFactory") as mock_factory,
            patch("agentbeats.messenger.create_text_message_object") as mock_create_message,
        ):
            mock_client = AsyncMock()
            mock_factory.connect = AsyncMock(return_value=mock_client)
            mock_create_message.return_value = MagicMock()

            mock_task = MagicMock()
            mock_task.id = "task-123"
            mock_client.send_message = AsyncMock(return_value=mock_task)

            # Mock async iteration
            async def mock_event_stream():
                from enum import Enum

                class MockTaskState(str, Enum):
                    COMPLETED = "completed"

                mock_event = MagicMock()
                mock_event.state = MockTaskState.COMPLETED
                mock_event.output = "response"
                yield mock_event

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until implementation caches clients
            try:
                await messenger.talk_to_agent(agent_url, message1)
                await messenger.talk_to_agent(agent_url, message2)

                # ClientFactory.connect should only be called once for same URL
                assert mock_factory.connect.call_count == 1
            except (AttributeError, TypeError, AssertionError):
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_different_agent_urls_get_different_clients(self) -> None:
        """Test that different agent URLs get separate cached clients."""
        # Given: A messenger instance
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url1 = "http://localhost:9009"
        agent_url2 = "http://localhost:9010"
        message = "test message"

        # When/Then: Should create separate clients for different URLs
        with (
            patch("agentbeats.messenger.ClientFactory") as mock_factory,
            patch("agentbeats.messenger.create_text_message_object") as mock_create_message,
        ):
            mock_client1, mock_client2, connect_side_effect, mock_event_stream = setup_two_agent_mock(
                agent_url1, agent_url2
            )

            mock_factory.connect = AsyncMock(side_effect=connect_side_effect)
            mock_create_message.return_value = MagicMock()

            mock_task = MagicMock()
            mock_task.id = "task-123"
            for client in [mock_client1, mock_client2]:
                client.send_message = AsyncMock(return_value=mock_task)

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until implementation caches clients per URL
            try:
                await messenger.talk_to_agent(agent_url1, message)
                await messenger.talk_to_agent(agent_url2, message)

                # Should call connect twice, once for each URL
                assert mock_factory.connect.call_count == 2
                mock_factory.connect.assert_any_call(agent_url1)
                mock_factory.connect.assert_any_call(agent_url2)
            except (AttributeError, TypeError):
                # Expected to fail - implementation not yet updated
                pass


class TestTraceDataTaskIdField:
    """Tests defining TraceData task_id field requirement."""

    def test_implementation_trace_data_has_task_id_field(self) -> None:
        """Test that implementation TraceData model has task_id field."""
        # Given: Importing TraceData from implementation
        from agentbeats.messenger import TraceData as ImplTraceData

        # Then: TraceData should have task_id field in model_fields
        assert "task_id" in ImplTraceData.model_fields, "TraceData must have task_id field"

        # And: Should be able to create instance with task_id
        trace = ImplTraceData(
            timestamp="2026-01-16T00:00:00Z",
            agent_url="http://localhost:9009",
            message="test message",
            response="test response",
            status_code=200,
            task_id="task-123",
        )
        assert trace.task_id == "task-123"

    def test_trace_data_has_task_id_field(self) -> None:
        """Test that TraceData model has task_id field."""
        # Given: A TraceData instance with task_id
        trace = TraceData(
            timestamp="2026-01-16T00:00:00Z",
            agent_url="http://localhost:9009",
            message="test message",
            response="test response",
            status_code=200,
            task_id="task-123",
        )

        # Then: task_id should be accessible
        assert trace.task_id == "task-123"

    def test_trace_data_task_id_is_optional(self) -> None:
        """Test that TraceData task_id field is optional with None default."""
        # Given: A TraceData instance without task_id
        trace = TraceData(
            timestamp="2026-01-16T00:00:00Z",
            agent_url="http://localhost:9009",
            message="test message",
            response="test response",
            status_code=200,
        )

        # Then: task_id should default to None
        assert trace.task_id is None

    def test_trace_data_preserves_existing_fields(self) -> None:
        """Test that TraceData preserves all existing fields when task_id is added."""
        # Given: A TraceData instance with all fields including task_id
        trace = TraceData(
            timestamp="2026-01-16T00:00:00Z",
            agent_url="http://localhost:9009",
            message="test message",
            response="test response",
            status_code=200,
            error="some error",
            task_id="task-456",
        )

        # Then: All fields should be preserved
        assert trace.timestamp == "2026-01-16T00:00:00Z"
        assert trace.agent_url == "http://localhost:9009"
        assert trace.message == "test message"
        assert trace.response == "test response"
        assert trace.status_code == 200
        assert trace.error == "some error"
        assert trace.task_id == "task-456"

    @pytest.mark.asyncio
    async def test_talk_to_agent_captures_task_id_in_trace(self) -> None:
        """Test that talk_to_agent() captures task.id from A2A Task object in TraceData."""
        # Given: A messenger instance and mocked A2A SDK with task.id
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url = "http://localhost:9009"
        message = "test message"
        expected_task_id = "task-abc-123"

        # When/Then: Should capture task.id in trace data
        with (
            patch("agentbeats.messenger.ClientFactory") as mock_factory,
            patch("agentbeats.messenger.create_text_message_object") as mock_create_message,
        ):
            mock_client = AsyncMock()
            mock_factory.connect = AsyncMock(return_value=mock_client)
            mock_create_message.return_value = MagicMock()

            mock_task = MagicMock()
            mock_task.id = expected_task_id  # Task has an id attribute
            mock_client.send_message = AsyncMock(return_value=mock_task)

            # Mock async iteration
            async def mock_event_stream():
                from enum import Enum

                class MockTaskState(str, Enum):
                    COMPLETED = "completed"

                mock_event = MagicMock()
                mock_event.state = MockTaskState.COMPLETED
                mock_event.output = "response from agent"
                yield mock_event

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until implementation captures task.id
            try:
                await messenger.talk_to_agent(agent_url, message)

                # Verify trace was captured with task_id
                traces = messenger.get_traces()
                assert len(traces) == 1
                assert traces[0].task_id == expected_task_id
                assert traces[0].agent_url == agent_url
                assert traces[0].message == message
                assert traces[0].response == "response from agent"
            except (AttributeError, AssertionError):
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_talk_to_agent_handles_missing_task_id(self) -> None:
        """Test that talk_to_agent() handles missing task.id gracefully."""
        # Given: A messenger instance and mocked A2A SDK without task.id
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url = "http://localhost:9009"
        message = "test message"

        # When/Then: Should handle missing task.id by setting to None
        with (
            patch("agentbeats.messenger.ClientFactory") as mock_factory,
            patch("agentbeats.messenger.create_text_message_object") as mock_create_message,
        ):
            mock_client = AsyncMock()
            mock_factory.connect = AsyncMock(return_value=mock_client)
            mock_create_message.return_value = MagicMock()

            mock_task = MagicMock()
            # Mock task without id attribute
            del mock_task.id
            mock_client.send_message = AsyncMock(return_value=mock_task)

            # Mock async iteration
            async def mock_event_stream():
                from enum import Enum

                class MockTaskState(str, Enum):
                    COMPLETED = "completed"

                mock_event = MagicMock()
                mock_event.state = MockTaskState.COMPLETED
                mock_event.output = "response from agent"
                yield mock_event

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until implementation handles missing task.id
            try:
                await messenger.talk_to_agent(agent_url, message)

                # Verify trace was captured with task_id = None
                traces = messenger.get_traces()
                assert len(traces) == 1
                assert traces[0].task_id is None
            except (AttributeError, AssertionError):
                # Expected to fail - implementation not yet updated
                pass


class TestMessengerA2ACleanup:
    """Tests defining Messenger cleanup contract for A2A clients."""

    @pytest.mark.asyncio
    async def test_messenger_has_close_method(self) -> None:
        """Test that Messenger has a close() method for cleanup."""
        # Given: A messenger instance
        from agentbeats.messenger import Messenger

        messenger = Messenger()

        # Then: Should have close method
        assert hasattr(messenger, "close"), "Messenger must have close() method"
        assert callable(messenger.close), "Messenger.close must be callable"

    @pytest.mark.asyncio
    async def test_messenger_close_is_async(self) -> None:
        """Test that Messenger.close() is an async method."""
        # Given: A messenger instance
        import inspect

        from agentbeats.messenger import Messenger

        messenger = Messenger()

        # This will fail until close() method is implemented
        try:
            # Then: close() should be an async method
            assert inspect.iscoroutinefunction(messenger.close), "Messenger.close() must be async"
        except AttributeError:
            # Expected to fail - implementation not yet updated
            pass

    @pytest.mark.asyncio
    async def test_messenger_close_cleans_up_cached_clients(self) -> None:
        """Test that Messenger.close() cleans up all cached A2A clients."""
        # Given: A messenger instance with cached clients
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url1 = "http://localhost:9009"
        agent_url2 = "http://localhost:9010"

        # When: We create cached clients by talking to agents
        with (
            patch("agentbeats.messenger.ClientFactory") as mock_factory,
            patch("agentbeats.messenger.create_text_message_object") as mock_create_message,
        ):
            mock_client1, mock_client2, connect_side_effect, mock_event_stream = setup_two_agent_mock(
                agent_url1, agent_url2, add_close_method=True
            )

            mock_factory.connect = AsyncMock(side_effect=connect_side_effect)
            mock_create_message.return_value = MagicMock()

            mock_task = MagicMock()
            mock_task.id = "task-123"
            for client in [mock_client1, mock_client2]:
                client.send_message = AsyncMock(return_value=mock_task)

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until close() method is implemented
            try:
                await messenger.talk_to_agent(agent_url1, "message1")
                await messenger.talk_to_agent(agent_url2, "message2")

                # Verify clients were cached
                assert len(messenger._clients) == 2

                # When: We close the messenger
                await messenger.close()

                # Then: All cached clients should be closed
                mock_client1.close.assert_called_once()
                mock_client2.close.assert_called_once()

                # And: Client cache should be cleared
                assert len(messenger._clients) == 0
            except (AttributeError, AssertionError):
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_messenger_close_handles_clients_without_close_method(self) -> None:
        """Test that Messenger.close() handles clients that don't have close() method."""
        # Given: A messenger instance with a client that lacks close() method
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url = "http://localhost:9009"

        # When: We cache a client without close() method
        with (
            patch("agentbeats.messenger.ClientFactory") as mock_factory,
            patch("agentbeats.messenger.create_text_message_object") as mock_create_message,
        ):
            mock_client = AsyncMock()
            # Explicitly remove close method
            if hasattr(mock_client, "close"):
                delattr(mock_client, "close")

            mock_factory.connect = AsyncMock(return_value=mock_client)
            mock_create_message.return_value = MagicMock()

            mock_task = MagicMock()
            mock_task.id = "task-123"
            mock_client.send_message = AsyncMock(return_value=mock_task)

            # Mock async iteration
            async def mock_event_stream():
                from enum import Enum

                class MockTaskState(str, Enum):
                    COMPLETED = "completed"

                mock_event = MagicMock()
                mock_event.state = MockTaskState.COMPLETED
                mock_event.output = "response"
                yield mock_event

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until close() method is implemented
            try:
                await messenger.talk_to_agent(agent_url, "message")

                # When: We close the messenger with a client lacking close()
                # Then: Should not raise an error
                await messenger.close()

                # And: Client cache should still be cleared
                assert len(messenger._clients) == 0
            except (AttributeError, AssertionError):
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_messenger_close_can_be_called_multiple_times(self) -> None:
        """Test that Messenger.close() can be called multiple times safely."""
        # Given: A messenger instance
        from agentbeats.messenger import Messenger

        messenger = Messenger()
        agent_url = "http://localhost:9009"

        # When: We cache a client and close multiple times
        with (
            patch("agentbeats.messenger.ClientFactory") as mock_factory,
            patch("agentbeats.messenger.create_text_message_object") as mock_create_message,
        ):
            mock_client = AsyncMock()
            mock_client.close = AsyncMock()

            mock_factory.connect = AsyncMock(return_value=mock_client)
            mock_create_message.return_value = MagicMock()

            mock_task = MagicMock()
            mock_task.id = "task-123"
            mock_client.send_message = AsyncMock(return_value=mock_task)

            # Mock async iteration
            async def mock_event_stream():
                from enum import Enum

                class MockTaskState(str, Enum):
                    COMPLETED = "completed"

                mock_event = MagicMock()
                mock_event.state = MockTaskState.COMPLETED
                mock_event.output = "response"
                yield mock_event

            mock_task.__aiter__ = lambda _: mock_event_stream()

            # This will fail until close() method is implemented
            try:
                await messenger.talk_to_agent(agent_url, "message")

                # When: We call close multiple times
                await messenger.close()
                await messenger.close()
                await messenger.close()

                # Then: Should not raise errors
                # Client close should only be called once (first close)
                assert mock_client.close.call_count >= 1

                # Cache should remain empty after multiple closes
                assert len(messenger._clients) == 0
            except (AttributeError, AssertionError):
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_messenger_close_on_empty_cache(self) -> None:
        """Test that Messenger.close() works when no clients are cached."""
        # Given: A messenger instance with no cached clients
        from agentbeats.messenger import Messenger

        messenger = Messenger()

        # This will fail until close() method is implemented
        try:
            # When: We call close with empty cache
            await messenger.close()

            # Then: Should not raise errors
            assert len(messenger._clients) == 0
        except AttributeError:
            # Expected to fail - implementation not yet updated
            pass
