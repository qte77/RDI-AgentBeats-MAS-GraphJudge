"""E2E tests for AgentCard endpoint accessibility.

RED phase: These tests should FAIL initially until agents properly expose AgentCards.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


class TestGreenAgentCard:
    """Test Green Agent AgentCard endpoint accessibility."""

    async def test_green_agentcard_endpoint_accessible(self):
        """Green Agent AgentCard accessible at /.well-known/agent-card.json."""
        from green.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            assert response.status_code == 200

    async def test_green_agentcard_has_required_fields(self):
        """Green Agent AgentCard contains required A2A fields."""
        from green.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            card = response.json()

            # Verify required A2A fields
            assert "agentId" in card
            assert card["agentId"] == "green-agent"
            assert "name" in card
            assert "description" in card
            assert "capabilities" in card

    async def test_green_agentcard_declares_protocol_support(self):
        """Green Agent AgentCard declares A2A protocol support."""
        from green.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            card = response.json()

            assert "capabilities" in card
            assert "protocols" in card["capabilities"]
            assert "a2a" in card["capabilities"]["protocols"]

    async def test_green_agentcard_declares_extensions(self):
        """Green Agent AgentCard declares traceability extension support."""
        from green.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            card = response.json()

            assert "extensions" in card["capabilities"]["protocols"]["a2a"]
            extensions = card["capabilities"]["protocols"]["a2a"]["extensions"]
            assert any("traceability" in ext for ext in extensions)


class TestPurpleAgentCard:
    """Test Purple Agent AgentCard endpoint accessibility."""

    async def test_purple_agentcard_endpoint_accessible(self):
        """Purple Agent AgentCard accessible at /.well-known/agent-card.json."""
        from purple.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            assert response.status_code == 200

    async def test_purple_agentcard_has_required_fields(self):
        """Purple Agent AgentCard contains required A2A fields."""
        from purple.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            card = response.json()

            # Verify required A2A fields
            assert "agentId" in card
            assert card["agentId"] == "purple-agent"
            assert "name" in card
            assert "description" in card
            assert "capabilities" in card

    async def test_purple_agentcard_declares_protocol_support(self):
        """Purple Agent AgentCard declares A2A protocol support."""
        from purple.server import create_app

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            card = response.json()

            assert "capabilities" in card
            assert "protocols" in card["capabilities"]
            assert "a2a" in card["capabilities"]["protocols"]
