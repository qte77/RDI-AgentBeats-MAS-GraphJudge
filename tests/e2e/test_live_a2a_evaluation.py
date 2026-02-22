"""Live A2A E2E integration tests.

Tests validate real A2A communication between Green and Purple agents using
ASGI transport for in-process testing (no Docker or live network required).

Skip in standard CI:
    uv run pytest tests/ -m "not network and not integration"

Run locally or in dedicated integration pipelines:
    uv run pytest tests/e2e/test_live_a2a_evaluation.py -m integration -v
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
class TestLiveA2AEvaluation:
    """Live A2A integration tests using ASGI transport (no Docker required)."""

    async def test_purple_responds_to_message_send(self) -> None:
        """Purple agent processes A2A message/send requests via ASGI transport."""
        from purple.server import create_app

        purple_app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=purple_app), base_url="http://test-purple"
        ) as client:
            response = await client.post(
                "/",
                json={
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "parts": [{"kind": "text", "text": "Hello from integration test"}]
                        }
                    },
                    "id": "1",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data
        assert data["result"]["status"]["state"] == "completed"

    async def test_executor_captures_interaction_traces(self) -> None:
        """Executor captures InteractionStep traces via real A2A exchange (no mocks)."""
        from green.executor import Executor
        from green.messenger import Messenger
        from green.models import InteractionStep
        from purple.server import create_app as create_purple_app

        purple_transport = ASGITransport(app=create_purple_app())
        # Requires httpx_transport param added to Messenger (GREEN phase)
        messenger = Messenger(httpx_transport=purple_transport)
        executor = Executor(coordination_rounds=1)

        traces = await executor.execute_task(
            task_description="Evaluate A2A coordination patterns",
            messenger=messenger,
            agent_url="http://test-purple",
        )

        assert len(traces) >= 1
        for step in traces:
            assert isinstance(step, InteractionStep)
            assert step.trace_id is not None
            assert step.step_id is not None
            assert step.latency >= 0

    async def test_results_json_written_with_agentbeats_schema(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """output/results.json written with valid AgentBeatsOutputModel schema."""
        from green.evals.graph import GraphEvaluator
        from green.executor import Executor
        from green.messenger import Messenger
        from green.models import AgentBeatsOutputModel
        from purple.server import create_app as create_purple_app

        purple_transport = ASGITransport(app=create_purple_app())
        # Requires httpx_transport param added to Messenger (GREEN phase)
        messenger = Messenger(httpx_transport=purple_transport)
        executor = Executor(coordination_rounds=1)

        traces = await executor.execute_task(
            task_description="Evaluate A2A coordination patterns",
            messenger=messenger,
            agent_url="http://test-purple",
        )

        eval_results = await executor.evaluate_all(
            traces=traces,
            graph_evaluator=GraphEvaluator(),
            llm_judge=None,
            latency_evaluator=None,
        )

        output_file = tmp_path / "results.json"  # type: ignore[operator]
        agentbeats_output = AgentBeatsOutputModel.from_evaluation_results(eval_results)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(agentbeats_output.to_json(indent=2))

        loaded = AgentBeatsOutputModel.model_validate_json(output_file.read_text())
        assert loaded.participants is not None
        assert len(loaded.results) >= 1
        assert loaded.results[0].max_score > 0

    async def test_green_evaluates_purple_full_e2e(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Green server evaluates Purple via real A2A exchange using ASGI transport."""
        from green.messenger import Messenger
        from green.models import AgentBeatsOutputModel
        from green.server import create_app as create_green_app
        from green.settings import GreenSettings
        from purple.server import create_app as create_purple_app

        purple_transport = ASGITransport(app=create_purple_app())

        # Route Green's outbound A2A calls to Purple via ASGI transport (no real network)
        # Requires httpx_transport param added to Messenger (GREEN phase)
        monkeypatch.setattr(
            "green.server.Messenger",
            lambda a2a_settings=None: Messenger(
                a2a_settings=a2a_settings, httpx_transport=purple_transport
            ),
        )

        # purple_agent_url has validation_alias so must be set via env var
        monkeypatch.setenv("PURPLE_AGENT_URL", "http://test-purple")
        output_file = tmp_path / "results.json"  # type: ignore[operator]
        settings = GreenSettings(output_file=output_file, coordination_rounds=1)
        green_app = create_green_app(settings=settings)

        async with AsyncClient(
            transport=ASGITransport(app=green_app), base_url="http://test-green"
        ) as client:
            response = await client.post(
                "/",
                json={
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "params": {"task": {"description": "Evaluate A2A coordination quality"}},
                    "id": "1",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data

        assert output_file.exists()
        loaded = AgentBeatsOutputModel.model_validate_json(output_file.read_text())
        assert len(loaded.results) >= 1
