"""Tests for Base Purple Agent A2A-compliant implementation.

RED phase: These tests should FAIL initially since Purple Agent doesn't exist yet.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from purple.models import JSONRPCRequest, JSONRPCResponse
from purple.server import create_app


class TestPurpleAgentModels:
    """Test Purple Agent Pydantic models."""

    def test_jsonrpc_request_model_validate(self):
        """JSONRPCRequest validates from dict using model_validate()."""
        data = {
            "jsonrpc": "2.0",
            "method": "tasks.send",
            "params": {"task": {"description": "Test"}},
            "id": 1,
        }
        request = JSONRPCRequest.model_validate(data)
        assert request.jsonrpc == "2.0"
        assert request.method == "tasks.send"
        assert request.id == 1

    def test_jsonrpc_response_model_validate(self):
        """JSONRPCResponse validates from dict using model_validate()."""
        data = {
            "jsonrpc": "2.0",
            "result": {"status": "completed"},
            "id": 1,
        }
        response = JSONRPCResponse.model_validate(data)
        assert response.jsonrpc == "2.0"
        assert response.result == {"status": "completed"}
        assert response.error is None
        assert response.id == 1

    def test_jsonrpc_response_with_error(self):
        """JSONRPCResponse validates error responses."""
        data = {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": 2,
        }
        response = JSONRPCResponse.model_validate(data)
        assert response.error is not None
        assert response.error["code"] == -32601
        assert response.result is None

    def test_models_located_in_purple_models(self):
        """Pydantic models are centralized in purple.models module."""
        from purple import models

        assert hasattr(models, "JSONRPCRequest")
        assert hasattr(models, "JSONRPCResponse")


class TestPurpleAgentCard:
    """Test Purple Agent AgentCard endpoint."""

    async def test_agent_card_endpoint_exists(self):
        """AgentCard accessible at /.well-known/agent-card.json."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            assert response.status_code == 200

    async def test_agent_card_has_required_fields(self):
        """AgentCard contains required A2A fields."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            card = response.json()

            # Verify required fields
            assert "agentId" in card
            assert card["agentId"] == "purple-agent"
            assert "name" in card
            assert "description" in card
            assert "capabilities" in card
            assert "protocols" in card["capabilities"]
            assert "a2a" in card["capabilities"]["protocols"]


class TestPurpleAgentJSONRPC:
    """Test Purple Agent A2A JSON-RPC 2.0 protocol support."""

    async def test_supports_jsonrpc_tasks_send(self):
        """Supports A2A JSON-RPC 2.0 protocol with tasks.send method."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            request = {
                "jsonrpc": "2.0",
                "method": "tasks.send",
                "params": {
                    "task": {
                        "description": "Test task",
                    }
                },
                "id": 1,
            }

            response = await client.post("/", json=request)
            assert response.status_code == 200

            result = response.json()
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "result" in result or "error" in result

    async def test_jsonrpc_method_not_found(self):
        """Returns error for unsupported JSON-RPC methods."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            request = {
                "jsonrpc": "2.0",
                "method": "unsupported.method",
                "params": {},
                "id": 2,
            }

            response = await client.post("/", json=request)
            result = response.json()

            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 2
            assert "error" in result
            assert result["error"]["code"] == -32601  # Method not found


class TestPurpleAgentMessenger:
    """Test Purple Agent messenger functionality."""

    async def test_messenger_uses_a2a_sdk(self):
        """Messenger uses ClientFactory.connect() from a2a-sdk."""
        from purple.messenger import Messenger

        with patch("purple.messenger.ClientFactory") as factory:
            mock_client = MagicMock()
            mock_client.close = AsyncMock()
            factory.connect = AsyncMock(return_value=mock_client)

            messenger = Messenger()
            await messenger.send_message("http://test.com", "Test message")

            factory.connect.assert_called_once()


class TestPurpleAgentExecutor:
    """Test Purple Agent executor functionality."""

    async def test_executor_executes_simple_task(self):
        """Executor can execute simple tasks."""
        from purple.executor import Executor
        from purple.messenger import Messenger

        executor = Executor()
        messenger = Messenger()

        with patch.object(messenger, "send_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = "Task completed"

            result = await executor.execute_task(
                task_description="Simple test task",
                messenger=messenger,
                agent_url="http://test.com",
            )

            assert result is not None


class TestPurpleAgentHealthCheck:
    """Test Purple Agent health check endpoint."""

    async def test_health_check_endpoint(self):
        """Health check endpoint returns healthy status."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "healthy"
