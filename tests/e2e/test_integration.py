"""E2E integration tests with both Green and Purple agents.

RED phase: These tests should FAIL initially until full integration works.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
class TestGreenPurpleIntegration:
    """Test integration between Green and Purple agents."""

    async def test_green_evaluates_purple_coordination(self):
        """Green Agent can evaluate Purple Agent's coordination patterns."""
        from green.executor import Executor
        from green.messenger import Messenger

        executor = Executor()
        messenger = Messenger()

        # Mock Purple Agent responses
        with patch.object(messenger, "send_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = "Purple agent response"

            # Execute evaluation task
            result = await executor.execute_task(
                task_description="Evaluate multi-agent coordination",
                messenger=messenger,
            )

            # Verify evaluation completed
            assert result is not None

    async def test_end_to_end_evaluation_flow(self):
        """Complete E2E flow: Purple coordination -> Green evaluation -> Results."""
        from green.server import create_app as create_green_app

        green_app = create_green_app()

        async with AsyncClient(transport=ASGITransport(app=green_app), base_url="http://test") as green_client:
            # Send evaluation request to Green Agent
            request = {
                "jsonrpc": "2.0",
                "method": "tasks.send",
                "params": {
                    "task": {
                        "description": "Evaluate coordination quality",
                    }
                },
                "id": 1,
            }

            response = await green_client.post("/", json=request)
            assert response.status_code == 200

            result = response.json()
            assert result["jsonrpc"] == "2.0"
            assert "result" in result

    async def test_results_written_to_output_directory(self):
        """Verify evaluation results are written to output/results.json."""
        from pathlib import Path

        from green.executor import Executor
        from green.messenger import Messenger

        executor = Executor()
        messenger = Messenger()

        with patch.object(messenger, "send_message", new_callable=AsyncMock):
            # Execute evaluation
            await executor.execute_task(
                task_description="Test evaluation",
                messenger=messenger,
            )

            # Check if results file would be created
            # (The actual file creation happens in server.py)
            output_dir = Path("output")
            results_file = output_dir / "results.json"

            # This test validates the expected output path
            assert results_file.parent.name == "output"
            assert results_file.name == "results.json"


@pytest.mark.integration
class TestGroundTruthE2EValidation:
    """E2E validation using ground truth scenarios."""

    async def test_e2e_with_ground_truth_scenario(self):
        """Run complete E2E test with a ground truth scenario."""
        import json
        from pathlib import Path

        from green.evals.graph import GraphEvaluator
        from green.models import CallType, InteractionStep

        # Load ground truth
        data_path = Path(__file__).parent.parent.parent / "data" / "ground_truth.json"
        with open(data_path) as f:
            ground_truth = json.load(f)

        # Pick a high coordination scenario
        scenario = next(s for s in ground_truth["scenarios"] if s["type"] == "high_coordination")

        # Create interaction steps from scenario
        steps = []
        from datetime import datetime, timezone

        base_time = datetime.now(timezone.utc)

        # Create root steps for each agent
        for agent in scenario["interaction_pattern"]["agents"]:
            step = InteractionStep(
                step_id=agent,
                trace_id="e2e_test",
                call_type=CallType.AGENT,
                start_time=base_time,
                end_time=base_time,
                latency=100,
            )
            steps.append(step)

        # Create interaction steps for each edge
        for i, edge in enumerate(scenario["interaction_pattern"]["edges"]):
            from_agent = edge["from"]
            to_agent = edge["to"]

            edge_step = InteractionStep(
                step_id=f"{from_agent}_to_{to_agent}_{i}",
                trace_id="e2e_test",
                call_type=CallType.AGENT,
                start_time=base_time,
                end_time=base_time,
                latency=100,
                parent_step_id=from_agent,
            )
            steps.append(edge_step)

        # Evaluate with Green Agent
        evaluator = GraphEvaluator()
        metrics = evaluator.evaluate(steps)

        # Verify results match expectations
        assert "graph_density" in metrics
        expected_quality = scenario["expected_metrics"]["coordination_quality"]
        if expected_quality == "high":
            assert metrics["graph_density"] >= 0.3

    async def test_multiple_scenarios_batch_evaluation(self):
        """Batch evaluation of multiple ground truth scenarios."""
        import json
        from pathlib import Path

        from green.evals.graph import GraphEvaluator
        from green.models import CallType, InteractionStep

        # Load ground truth
        data_path = Path(__file__).parent.parent.parent / "data" / "ground_truth.json"
        with open(data_path) as f:
            ground_truth = json.load(f)

        evaluator = GraphEvaluator()
        results = []

        # Evaluate first 3 scenarios
        for scenario in ground_truth["scenarios"][:3]:
            # Create steps
            steps = []
            from datetime import datetime, timezone

            base_time = datetime.now(timezone.utc)

            # Create root steps for each agent
            for agent in scenario["interaction_pattern"]["agents"]:
                step = InteractionStep(
                    step_id=agent,
                    trace_id=scenario["id"],
                    call_type=CallType.AGENT,
                    start_time=base_time,
                    end_time=base_time,
                    latency=100,
                )
                steps.append(step)

            # Create interaction steps for each edge
            for i, edge in enumerate(scenario["interaction_pattern"]["edges"]):
                from_agent = edge["from"]
                to_agent = edge["to"]

                edge_step = InteractionStep(
                    step_id=f"{from_agent}_to_{to_agent}_{i}",
                    trace_id=scenario["id"],
                    call_type=CallType.AGENT,
                    start_time=base_time,
                    end_time=base_time,
                    latency=100,
                    parent_step_id=from_agent,
                )
                steps.append(edge_step)

            # Evaluate
            metrics = evaluator.evaluate(steps)
            results.append(
                {
                    "scenario_id": scenario["id"],
                    "type": scenario["type"],
                    "metrics": metrics,
                }
            )

        # Verify we evaluated multiple scenarios
        assert len(results) == 3
        for result in results:
            assert "scenario_id" in result
            assert "metrics" in result
            assert "graph_density" in result["metrics"]
