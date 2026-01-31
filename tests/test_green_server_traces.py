"""Tests for Green Agent trace collection server endpoints.

RED phase: These tests should FAIL initially since endpoints don't exist yet.
Tests for POST /traces, POST /register, and GET /peers endpoints.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from common.models import CallType, InteractionStep


@pytest.fixture
def sample_traces_payload():
    """Sample trace payload for testing."""
    return {
        "traces": [
            {
                "step_id": "step-1",
                "trace_id": "trace-123",
                "call_type": "AGENT",
                "start_time": "2026-01-31T10:00:00",
                "end_time": "2026-01-31T10:00:01",
                "latency": 1000,
                "error": None,
                "parent_step_id": None,
            },
            {
                "step_id": "step-2",
                "trace_id": "trace-123",
                "call_type": "TOOL",
                "start_time": "2026-01-31T10:00:01",
                "end_time": "2026-01-31T10:00:02",
                "latency": 1000,
                "error": None,
                "parent_step_id": "step-1",
            },
        ]
    }


class TestTracesEndpoint:
    """Test POST /traces endpoint."""

    @pytest.mark.asyncio
    async def test_traces_endpoint_exists(self):
        """POST /traces endpoint exists."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/traces", json={"traces": []})

            # Should accept POST requests (not 404)
            assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_traces_endpoint_accepts_trace_payload(self, sample_traces_payload):
        """POST /traces accepts trace payload."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/traces", json=sample_traces_payload)

            # Should accept valid trace payload
            assert response.status_code in (200, 201, 204)

    @pytest.mark.asyncio
    async def test_traces_endpoint_stores_traces(self, sample_traces_payload):
        """POST /traces stores traces in trace store."""
        from green.server import create_app
        from green.trace_store import TraceStore

        # Create app with shared trace store
        store = TraceStore()
        app = create_app()
        # Inject trace store (this will be handled in implementation)
        app.state.trace_store = store

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/traces", json=sample_traces_payload)

            assert response.status_code in (200, 201, 204)

            # Verify traces were stored
            all_traces = store.get_all_traces()
            assert len(all_traces) == 2

    @pytest.mark.asyncio
    async def test_traces_endpoint_is_async_fire_and_forget(self, sample_traces_payload):
        """POST /traces is async fire-and-forget (returns immediately)."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Should return quickly without waiting for processing
            response = await client.post("/traces", json=sample_traces_payload)

            # Should return success immediately
            assert response.status_code in (200, 201, 204)

    @pytest.mark.asyncio
    async def test_traces_endpoint_handles_multiple_trace_batches(self, sample_traces_payload):
        """POST /traces accumulates traces from multiple requests."""
        from green.server import create_app
        from green.trace_store import TraceStore

        store = TraceStore()
        app = create_app()
        app.state.trace_store = store

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Send first batch
            await client.post("/traces", json=sample_traces_payload)

            # Send second batch
            second_payload = {
                "traces": [
                    {
                        "step_id": "step-3",
                        "trace_id": "trace-456",
                        "call_type": "AGENT",
                        "start_time": "2026-01-31T10:00:02",
                        "end_time": "2026-01-31T10:00:03",
                        "latency": 1000,
                        "error": None,
                        "parent_step_id": None,
                    }
                ]
            }
            await client.post("/traces", json=second_payload)

            # Should have all traces
            all_traces = store.get_all_traces()
            assert len(all_traces) == 3

    @pytest.mark.asyncio
    async def test_traces_endpoint_handles_empty_traces(self):
        """POST /traces handles empty trace list."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/traces", json={"traces": []})

            # Should accept empty trace list
            assert response.status_code in (200, 201, 204)


class TestRegisterEndpoint:
    """Test POST /register endpoint."""

    @pytest.mark.asyncio
    async def test_register_endpoint_exists(self):
        """POST /register endpoint exists."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/register", json={"agent_url": "http://agent1:8000"})

            # Should accept POST requests (not 404)
            assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_register_endpoint_accepts_agent_url(self):
        """POST /register accepts agent_url payload."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/register", json={"agent_url": "http://agent1:8000"})

            # Should accept valid agent_url
            assert response.status_code in (200, 201, 204)

    @pytest.mark.asyncio
    async def test_register_endpoint_stores_agent_url(self):
        """POST /register stores agent URL in registry."""
        from green.server import create_app
        from green.trace_store import TraceStore

        store = TraceStore()
        app = create_app()
        app.state.trace_store = store

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/register", json={"agent_url": "http://agent1:8000"})

            assert response.status_code in (200, 201, 204)

            # Verify agent was registered
            agents = store.get_registered_agents()
            assert "http://agent1:8000" in agents

    @pytest.mark.asyncio
    async def test_register_endpoint_handles_multiple_agents(self):
        """POST /register handles multiple agent registrations."""
        from green.server import create_app
        from green.trace_store import TraceStore

        store = TraceStore()
        app = create_app()
        app.state.trace_store = store

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/register", json={"agent_url": "http://agent1:8000"})
            await client.post("/register", json={"agent_url": "http://agent2:8000"})
            await client.post("/register", json={"agent_url": "http://agent3:8000"})

            # Verify all agents registered
            agents = store.get_registered_agents()
            assert len(agents) == 3
            assert "http://agent1:8000" in agents
            assert "http://agent2:8000" in agents
            assert "http://agent3:8000" in agents

    @pytest.mark.asyncio
    async def test_register_endpoint_deduplicates_agents(self):
        """POST /register deduplicates agent URLs."""
        from green.server import create_app
        from green.trace_store import TraceStore

        store = TraceStore()
        app = create_app()
        app.state.trace_store = store

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/register", json={"agent_url": "http://agent1:8000"})
            await client.post("/register", json={"agent_url": "http://agent1:8000"})  # Duplicate

            # Should have only one agent
            agents = store.get_registered_agents()
            assert len(agents) == 1

    @pytest.mark.asyncio
    async def test_register_endpoint_validates_agent_url(self):
        """POST /register validates agent_url parameter."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Missing agent_url
            response = await client.post("/register", json={})

            # Should return error (400 or 422)
            assert response.status_code in (400, 422)


class TestPeersEndpoint:
    """Test GET /peers endpoint."""

    @pytest.mark.asyncio
    async def test_peers_endpoint_exists(self):
        """GET /peers endpoint exists."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/peers")

            # Should accept GET requests (not 404)
            assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_peers_endpoint_returns_json(self):
        """GET /peers returns JSON response."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/peers")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_peers_endpoint_returns_peers_list(self):
        """GET /peers returns peers list."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/peers")

            assert response.status_code == 200
            data = response.json()
            assert "peers" in data
            assert isinstance(data["peers"], list)

    @pytest.mark.asyncio
    async def test_peers_endpoint_returns_empty_list_initially(self):
        """GET /peers returns empty list when no agents registered."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/peers")

            assert response.status_code == 200
            data = response.json()
            assert data["peers"] == []

    @pytest.mark.asyncio
    async def test_peers_endpoint_returns_registered_agents(self):
        """GET /peers returns registered agent URLs."""
        from green.server import create_app
        from green.trace_store import TraceStore

        store = TraceStore()
        app = create_app()
        app.state.trace_store = store

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Register some agents
            await client.post("/register", json={"agent_url": "http://agent1:8000"})
            await client.post("/register", json={"agent_url": "http://agent2:8000"})

            # Get peers
            response = await client.get("/peers")

            assert response.status_code == 200
            data = response.json()
            assert len(data["peers"]) == 2
            assert "http://agent1:8000" in data["peers"]
            assert "http://agent2:8000" in data["peers"]


class TestTracesEndpointsIntegration:
    """Test integration between trace endpoints."""

    @pytest.mark.asyncio
    async def test_traces_and_registry_are_independent(self):
        """Traces and agent registry are independent."""
        from green.server import create_app
        from green.trace_store import TraceStore

        store = TraceStore()
        app = create_app()
        app.state.trace_store = store

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Add traces
            await client.post(
                "/traces",
                json={
                    "traces": [
                        {
                            "step_id": "step-1",
                            "trace_id": "trace-123",
                            "call_type": "AGENT",
                            "start_time": "2026-01-31T10:00:00",
                            "end_time": "2026-01-31T10:00:01",
                            "latency": 1000,
                            "error": None,
                            "parent_step_id": None,
                        }
                    ]
                },
            )

            # Register agent
            await client.post("/register", json={"agent_url": "http://agent1:8000"})

            # Verify traces stored
            all_traces = store.get_all_traces()
            assert len(all_traces) == 1

            # Verify agent registered
            agents = store.get_registered_agents()
            assert len(agents) == 1

    @pytest.mark.asyncio
    async def test_full_trace_collection_workflow(self):
        """Test full trace collection workflow."""
        from green.server import create_app
        from green.trace_store import TraceStore

        store = TraceStore()
        app = create_app()
        app.state.trace_store = store

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Purple agent registers
            await client.post("/register", json={"agent_url": "http://purple:8001"})

            # 2. Purple agent sends traces
            await client.post(
                "/traces",
                json={
                    "traces": [
                        {
                            "step_id": "step-1",
                            "trace_id": "trace-123",
                            "call_type": "AGENT",
                            "start_time": "2026-01-31T10:00:00",
                            "end_time": "2026-01-31T10:00:01",
                            "latency": 1000,
                            "error": None,
                            "parent_step_id": None,
                        }
                    ]
                },
            )

            # 3. Another agent discovers peers
            peers_response = await client.get("/peers")
            peers_data = peers_response.json()

            # Verify workflow
            assert len(peers_data["peers"]) == 1
            assert "http://purple:8001" in peers_data["peers"]
            assert len(store.get_all_traces()) == 1
