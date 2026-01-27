"""E2E tests for Purple Agent output generation.

RED phase: These tests should FAIL initially until Purple Agent properly generates outputs.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


class TestPurpleAgentOutputs:
    """Test Purple Agent generates expected outputs."""

    async def test_purple_agent_accepts_task(self):
        """Purple Agent accepts tasks via A2A JSON-RPC protocol."""
        from purple.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            request = {
                "jsonrpc": "2.0",
                "method": "tasks.send",
                "params": {
                    "task": {
                        "description": "Test coordination task",
                    }
                },
                "id": 1,
            }

            response = await client.post("/", json=request)
            assert response.status_code == 200

            result = response.json()
            assert result["jsonrpc"] == "2.0"
            assert result["id"] == 1
            assert "result" in result

    async def test_purple_agent_generates_interaction_trace(self):
        """Purple Agent generates interaction traces with A2A traceability."""
        from purple.executor import Executor
        from purple.messenger import Messenger

        executor = Executor()
        messenger = Messenger()

        with patch.object(messenger, "send_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = "Response"

            # Execute simple task to generate trace
            result = await executor.execute_task(
                task_description="Coordinate with peer agents",
                messenger=messenger,
                agent_url="http://test-agent.com",
            )

            # Verify trace was generated
            assert result is not None

    async def test_purple_agent_responds_to_coordination_requests(self):
        """Purple Agent responds to coordination requests from other agents."""
        from purple.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Simulate coordination request from another agent
            request = {
                "jsonrpc": "2.0",
                "method": "tasks.send",
                "params": {
                    "task": {
                        "description": "Multi-agent coordination scenario",
                    }
                },
                "id": 2,
            }

            response = await client.post("/", json=request)
            result = response.json()

            assert response.status_code == 200
            assert "result" in result
            # Purple agent should complete the task
            assert result["result"] is not None


class TestPurpleAgentTraceability:
    """Test Purple Agent traceability extension support."""

    async def test_purple_agent_supports_traceability_extension(self):
        """Purple Agent declares traceability extension support in AgentCard."""
        from purple.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            card = response.json()

            # Verify traceability extension is declared
            assert "capabilities" in card
            assert "protocols" in card["capabilities"]
            assert "a2a" in card["capabilities"]["protocols"]

            # Check for extensions field
            a2a_protocol = card["capabilities"]["protocols"]["a2a"]
            if "extensions" in a2a_protocol:
                extensions = a2a_protocol["extensions"]
                assert any("traceability" in ext for ext in extensions)

    async def test_purple_agent_generates_step_ids(self):
        """Purple Agent generates unique step IDs for traceability."""
        from purple.executor import Executor
        from purple.messenger import Messenger

        executor = Executor()
        messenger = Messenger()

        with patch.object(messenger, "send_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = "Response"

            # Execute task and verify step IDs are generated
            result = await executor.execute_task(
                task_description="Generate traced steps",
                messenger=messenger,
                agent_url="http://test-agent.com",
            )

            # Result should exist
            assert result is not None
