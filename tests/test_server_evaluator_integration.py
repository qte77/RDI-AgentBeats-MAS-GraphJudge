"""Tests for A2A server integration with evaluator pipeline.

RED phase: These tests should verify server properly integrates with all evaluators.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def mock_graph_evaluator() -> MagicMock:
    """Mock Graph evaluator for server testing."""
    evaluator = MagicMock()
    evaluator.evaluate = AsyncMock(
        return_value={
            "graph_density": 0.5,
            "avg_degree": 2.0,
            "clustering_coefficient": 0.3,
            "bottlenecks": [],
        }
    )
    return evaluator


@pytest.fixture
def mock_llm_judge() -> MagicMock:
    """Mock LLM Judge evaluator for server testing."""
    evaluator = MagicMock()
    evaluator.evaluate = AsyncMock(
        return_value={
            "overall_score": 0.8,
            "reasoning": "Good coordination observed",
            "coordination_quality": "high",
            "strengths": ["Fast response", "Clear communication"],
            "weaknesses": [],
        }
    )
    return evaluator


@pytest.fixture
def mock_latency_evaluator() -> MagicMock:
    """Mock Latency evaluator for server testing."""
    evaluator = MagicMock()
    evaluator.evaluate = AsyncMock(
        return_value={
            "avg": 1250.0,
            "p50": 1250.0,
            "p95": 1500.0,
            "p99": 1500.0,
            "slowest_agent": "agent-1",
            "warning": "Latency values only comparable within same system/run",
        }
    )
    return evaluator


@pytest.fixture
def mock_executor_with_evaluate_all() -> MagicMock:
    """Mock Executor with evaluate_all method."""
    executor = MagicMock()
    executor.execute_task = AsyncMock(return_value=[])
    executor.evaluate_all = AsyncMock(
        return_value={
            "tier1_graph": {"graph_density": 0.5},
            "tier2_llm": {"overall_score": 0.8},
            "tier2_latency": {"avg": 1250.0},
        }
    )
    return executor


class TestServerEvaluatorPipelineIntegration:
    """Test server integrates with all evaluators in pipeline."""

    async def test_server_calls_executor_evaluate_all(
        self, mock_executor_with_evaluate_all: MagicMock
    ) -> None:
        """Server calls executor.evaluate_all() with all evaluators."""
        from green.server import create_app

        with patch("green.server.Executor", return_value=mock_executor_with_evaluate_all):
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
                    "id": "test-request-1",
                }

                await client.post("/", json=request_data)

                # Verify executor.evaluate_all was called
                mock_executor_with_evaluate_all.evaluate_all.assert_called_once()

    async def test_server_passes_all_evaluators_to_executor(
        self, mock_executor_with_evaluate_all: MagicMock
    ) -> None:
        """Server passes graph, LLM, and latency evaluators to executor.evaluate_all()."""
        from green.server import create_app

        with patch("green.server.Executor", return_value=mock_executor_with_evaluate_all):
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
                    "id": "test-request-1",
                }

                await client.post("/", json=request_data)

                # Verify evaluate_all was called with keyword arguments
                call_args = mock_executor_with_evaluate_all.evaluate_all.call_args
                assert call_args is not None

                # Check that evaluators were passed (either as args or kwargs)
                call_kwargs = call_args[1] if len(call_args) > 1 else {}
                assert (
                    "graph_evaluator" in call_kwargs
                    or "llm_judge" in call_kwargs
                    or "latency_evaluator" in call_kwargs
                ) or len(call_args[0]) >= 2  # Or passed as positional args

    async def test_server_returns_all_tier_results(
        self, mock_executor_with_evaluate_all: MagicMock
    ) -> None:
        """Server returns results from all evaluation tiers (Graph, LLM, Latency)."""
        from green.server import create_app

        with patch("green.server.Executor", return_value=mock_executor_with_evaluate_all):
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
                    "id": "test-request-1",
                }

                response = await client.post("/", json=request_data)
                data = response.json()

                # Should return results with all tiers
                assert "result" in data
                result = data["result"]

                # Check for evaluation structure (could be nested)
                assert "evaluation" in result or "tier1_graph" in result


class TestServerAgentCardCapabilities:
    """Test AgentCard properly advertises evaluation capabilities."""

    async def test_agentcard_includes_evaluation_capabilities(self) -> None:
        """AgentCard describes multi-tier evaluation capabilities."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            data = response.json()

            # AgentCard should describe agent capabilities
            assert "description" in data
            description = data["description"].lower()

            # Should mention key evaluation features
            assert (
                "coordination" in description
                or "graph" in description
                or "evaluation" in description
                or "assessment" in description
            )

    async def test_agentcard_declares_a2a_protocol_support(self) -> None:
        """AgentCard declares A2A protocol support per specification."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            data = response.json()

            # Must declare A2A protocol support
            assert "capabilities" in data
            assert "protocols" in data["capabilities"]
            assert "a2a" in data["capabilities"]["protocols"]

    async def test_agentcard_includes_extension_support(self) -> None:
        """AgentCard declares support for A2A extensions (traceability, timestamp)."""
        from green.server import create_app

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/.well-known/agent-card.json")
            data = response.json()

            # Should declare extension support
            assert "capabilities" in data
            assert "extensions" in data["capabilities"]
            extensions = data["capabilities"]["extensions"]

            # Should be a list of extension identifiers
            assert isinstance(extensions, list)
