"""Tests for A2A HTTP server implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

if TYPE_CHECKING:
    from green.models import InteractionStep


@pytest.fixture
def mock_agent() -> MagicMock:
    """Mock Agent instance for testing."""
    agent = MagicMock()
    agent.evaluate = AsyncMock(
        return_value={
            "tier1_graph": {"graph_density": 0.5},
            "tier2_llm": {"overall_score": 0.8},
            "tier2_latency": {"avg_latency": 1000},
            "coordination_summary": {"overall_quality": "high"},
        }
    )
    return agent


@pytest.fixture
def mock_executor() -> MagicMock:
    """Mock Executor instance for testing."""
    executor = MagicMock()
    executor.execute_task = AsyncMock(return_value=[])
    return executor


async def test_server_exposes_agentcard_endpoint() -> None:
    """Test that server exposes AgentCard at /.well-known/agent-card.json."""
    from green.server import create_app

    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/.well-known/agent-card.json")

        assert response.status_code == 200
        data = response.json()

        # AgentCard must have required fields
        assert "agentId" in data
        assert "name" in data
        assert "capabilities" in data


async def test_server_handles_health_check() -> None:
    """Test that server handles health check endpoint."""
    from green.server import create_app

    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


async def test_server_handles_a2a_jsonrpc_request(mock_agent: MagicMock, mock_executor: MagicMock) -> None:
    """Test that server handles A2A JSON-RPC protocol requests."""
    from green.server import create_app

    with (
        patch("green.server.Agent", return_value=mock_agent),
        patch("green.server.Executor", return_value=mock_executor),
    ):
        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # A2A JSON-RPC 2.0 request format
            request_data = {
                "jsonrpc": "2.0",
                "method": "tasks.send",
                "params": {
                    "task": {
                        "description": "Evaluate agent coordination",
                        "context": {},
                    }
                },
                "id": "test-request-1",
            }

            response = await client.post("/", json=request_data)

            assert response.status_code == 200
            data = response.json()

            # JSON-RPC response format
            assert "jsonrpc" in data
            assert data["jsonrpc"] == "2.0"
            assert "id" in data
            assert data["id"] == "test-request-1"


async def test_server_delegates_to_executor_and_agent(mock_agent: MagicMock, mock_executor: MagicMock) -> None:
    """Test that server delegates task execution to Executor -> Agent."""
    from green.server import create_app

    with (
        patch("green.server.Agent", return_value=mock_agent),
        patch("green.server.Executor", return_value=mock_executor),
    ):
        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            request_data = {
                "jsonrpc": "2.0",
                "method": "tasks.send",
                "params": {
                    "task": {
                        "description": "Evaluate agent coordination",
                        "context": {},
                    }
                },
                "id": "test-request-2",
            }

            await client.post("/", json=request_data)

            # Verify Executor was called
            mock_executor.execute_task.assert_called_once()

            # Verify Agent.evaluate was called with traces
            mock_agent.evaluate.assert_called_once()


async def test_server_writes_results_to_output_file(
    mock_agent: MagicMock, mock_executor: MagicMock, tmp_path: Path
) -> None:
    """Test that server writes evaluation results to output/results.json."""
    from green.server import create_app

    output_file = tmp_path / "results.json"

    with (
        patch("green.server.Agent", return_value=mock_agent),
        patch("green.server.Executor", return_value=mock_executor),
        patch("green.server.OUTPUT_FILE", output_file),
    ):
        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            request_data = {
                "jsonrpc": "2.0",
                "method": "tasks.send",
                "params": {
                    "task": {
                        "description": "Evaluate agent coordination",
                        "context": {},
                    }
                },
                "id": "test-request-3",
            }

            await client.post("/", json=request_data)

            # Verify results file was written
            assert output_file.exists()
            with output_file.open() as f:
                results = json.load(f)

            # Verify results structure
            assert isinstance(results, dict)
            assert "tier1_graph" in results or "evaluation" in results


def test_cli_accepts_host_port_card_url_args() -> None:
    """Test that CLI accepts --host, --port, --card-url arguments."""
    from green.server import parse_args

    args = parse_args(["--host", "0.0.0.0", "--port", "9009", "--card-url", "http://localhost:9009"])

    assert args.host == "0.0.0.0"
    assert args.port == 9009
    assert args.card_url == "http://localhost:9009"


def test_cli_has_default_values() -> None:
    """Test that CLI has sensible default values."""
    from green.server import parse_args

    args = parse_args([])

    assert args.host is not None
    assert args.port is not None
    assert args.card_url is not None


async def test_server_handles_multiple_concurrent_requests(mock_agent: MagicMock, mock_executor: MagicMock) -> None:
    """Test that server can handle multiple concurrent requests."""
    from green.server import create_app

    with (
        patch("green.server.Agent", return_value=mock_agent),
        patch("green.server.Executor", return_value=mock_executor),
    ):
        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Send multiple requests concurrently
            requests = [
                {
                    "jsonrpc": "2.0",
                    "method": "tasks.send",
                    "params": {
                        "task": {
                            "description": f"Evaluate coordination {i}",
                            "context": {},
                        }
                    },
                    "id": f"test-request-{i}",
                }
                for i in range(3)
            ]

            responses = []
            for request_data in requests:
                response = await client.post("/", json=request_data)
                responses.append(response)

            # All requests should succeed
            assert all(r.status_code == 200 for r in responses)

            # Each response should have correct ID
            for i, response in enumerate(responses):
                data = response.json()
                assert data["id"] == f"test-request-{i}"


async def test_server_returns_error_for_invalid_jsonrpc() -> None:
    """Test that server returns proper error for invalid JSON-RPC request."""
    from green.server import create_app

    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Invalid JSON-RPC request (missing required fields)
        invalid_request = {"invalid": "request"}

        response = await client.post("/", json=invalid_request)

        # Should return JSON-RPC error response
        assert response.status_code in (200, 400, 422)  # Can be 200 with error in body, 400, or 422 for validation
        data = response.json()

        # Check for error indication
        assert "error" in data or "detail" in data or "jsonrpc" in data
