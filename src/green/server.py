"""A2A HTTP server implementation.

Implements A2A-compliant HTTP server with AgentCard endpoint, health checks,
and task delegation to Executor -> Agent pipeline.
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from green.models import AgentBeatsOutputModel
from green.executor import Executor
from green.messenger import Messenger
from green.models import CallType, InteractionStep, get_agent_extensions

# Purple agent URL - configurable via environment
PURPLE_AGENT_URL = os.getenv("PURPLE_AGENT_URL", "http://localhost:8002")


def _build_traces_from_pattern(pattern: dict[str, Any]) -> list[InteractionStep]:
    """Build InteractionStep traces from an interaction pattern.

    Converts ground truth interaction patterns into traces for graph evaluation.
    Creates one InteractionStep per edge to properly represent multi-edge graphs.
    Isolated agents (with no edges) are added as standalone steps.

    Args:
        pattern: Interaction pattern with agents and edges

    Returns:
        List of InteractionStep traces representing the interaction pattern
    """
    agents = set(pattern.get("agents", []))
    edges = pattern.get("edges", [])

    if not agents:
        return []

    traces: list[InteractionStep] = []
    base_time = datetime.now()
    trace_id = "test-trace"
    agents_in_edges: set[str] = set()

    # Create one step per edge - graph.add_edge auto-adds nodes
    for i, edge in enumerate(edges):
        from_agent = edge.get("from")
        to_agent = edge.get("to")
        if from_agent and to_agent:
            agents_in_edges.add(from_agent)
            agents_in_edges.add(to_agent)
            step = InteractionStep(
                step_id=to_agent,  # Target agent becomes the step
                trace_id=trace_id,
                call_type=CallType.AGENT,
                start_time=base_time + timedelta(milliseconds=i * 100),
                end_time=base_time + timedelta(milliseconds=i * 100 + 50),
                latency=50,
                parent_step_id=from_agent,  # Source agent creates the edge
            )
            traces.append(step)

    # Add isolated agents (those not in any edge) as standalone steps
    isolated_agents = agents - agents_in_edges
    for i, agent in enumerate(isolated_agents):
        step = InteractionStep(
            step_id=agent,
            trace_id=trace_id,
            call_type=CallType.AGENT,
            start_time=base_time + timedelta(milliseconds=(len(edges) + i) * 100),
            end_time=base_time + timedelta(milliseconds=(len(edges) + i) * 100 + 50),
            latency=50,
            parent_step_id=None,  # No edges - isolated
        )
        traces.append(step)

    return traces


# TODO: Change to results/results.json (update prd.json STORY-006, STORY-011 first)
OUTPUT_FILE = Path("output/results.json")


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request model."""

    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any]
    id: str | int


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response model."""

    jsonrpc: str = "2.0"
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    id: str | int


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(title="Green Agent A2A Server")

    @app.get("/.well-known/agent-card.json")
    async def get_agent_card() -> dict[str, Any]:  # pyright: ignore[reportUnusedFunction]
        """Return AgentCard per A2A protocol specification.

        Returns:
            AgentCard with agent metadata and capabilities
        """
        return {
            "agentId": "green-agent",
            "name": "Green Agent (Assessor)",
            "description": (
                "Multi-agent coordination quality evaluator using graph analysis, "
                "LLM assessment, and latency metrics"
            ),
            "version": "1.0.0",
            "url": "http://localhost:9009",  # TODO: Make configurable
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
            "skills": [
                {
                    "id": "evaluate",
                    "name": "Evaluate Agent Coordination",
                    "description": "Evaluate multi-agent coordination quality",
                    "tags": ["evaluation", "coordination", "graph-analysis"],
                }
            ],
            "capabilities": {
                "protocols": ["a2a"],
                "extensions": get_agent_extensions(),
            },
            "endpoints": {
                "a2a": "/",
                "health": "/health",
            },
        }

    @app.get("/health")
    async def health_check() -> dict[str, str]:  # pyright: ignore[reportUnusedFunction]
        """Health check endpoint.

        Returns:
            Health status indicator
        """
        return {"status": "healthy"}

    @app.post("/")
    async def handle_jsonrpc(request: JSONRPCRequest) -> JSONRPCResponse:  # pyright: ignore[reportUnusedFunction]
        """Handle A2A JSON-RPC 2.0 protocol requests.

        Args:
            request: JSON-RPC request

        Returns:
            JSON-RPC response with evaluation results

        Raises:
            HTTPException: If request processing fails
        """
        try:
            if request.method != "tasks.send":
                return JSONRPCResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {request.method}"},
                )

            # Extract task description and optional interaction pattern
            task_params = request.params.get("task", {})
            task_description = task_params.get("description", "")
            interaction_pattern = task_params.get("interaction_pattern")

            if not task_description:
                return JSONRPCResponse(
                    id=request.id,
                    error={"code": -32602, "message": "Invalid params: task.description required"},
                )

            executor = Executor()

            # If interaction_pattern provided, build traces from it (for testing/evaluation)
            # Otherwise, execute real task via Purple agent
            if interaction_pattern:
                traces = _build_traces_from_pattern(interaction_pattern)
            else:
                messenger = Messenger()
                traces = await executor.execute_task(
                    task_description=task_description,
                    messenger=messenger,
                    agent_url=PURPLE_AGENT_URL,
                )

            # Create evaluator instances
            # Graph evaluator (Tier 1) - computes coordination quality metrics
            from green.evals.graph import GraphEvaluator

            graph_evaluator = GraphEvaluator()

            # LLM Judge (Tier 2) - use evaluator wrapper
            from green.evals.llm_judge import llm_evaluate

            class LLMJudgeEvaluator:
                async def evaluate(
                    self, traces: list[InteractionStep], graph_results: dict[str, Any] | None = None
                ) -> dict[str, Any]:
                    result = await llm_evaluate(traces, graph_metrics=graph_results)
                    return result.model_dump()

            llm_judge = LLMJudgeEvaluator()

            # Latency evaluator (Tier 2) - use evaluator wrapper
            from green.evals.system import evaluate_latency

            class LatencyEvaluator:
                async def evaluate(self, traces: list[InteractionStep]) -> dict[str, Any]:
                    metrics = evaluate_latency(traces)
                    return metrics.model_dump()

            latency_evaluator = LatencyEvaluator()

            # Evaluate all traces using executor pipeline
            evaluation_results = await executor.evaluate_all(
                traces=traces,
                graph_evaluator=graph_evaluator,
                llm_judge=llm_judge,
                latency_evaluator=latency_evaluator,
            )

            # Transform to AgentBeats leaderboard format using Pydantic model
            # agent_id defaults to AGENT_UUID env var or "green-agent"
            agentbeats_output = AgentBeatsOutputModel.from_evaluation_results(
                evaluation_results=evaluation_results,
                domain="r&d-assessment",
                max_score=100.0,
            )

            # Write results to output file in AgentBeats format
            # Using Pydantic ensures schema validation
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with OUTPUT_FILE.open("w") as f:
                f.write(agentbeats_output.to_json(indent=2))

            # Extract graph metrics for response (Tier 1 results)
            tier1_graph = evaluation_results.get("tier1_graph") or {}
            graph_metrics = tier1_graph.model_dump() if hasattr(tier1_graph, "model_dump") else {}

            # Return JSON-RPC success response with graph metrics in expected format
            return JSONRPCResponse(
                id=request.id,
                result={
                    "status": "completed",
                    "parts": [
                        {
                            "type": "data",
                            "data": {
                                "classification": graph_metrics.get("coordination_quality", "low"),
                                "overall_score": graph_metrics.get("graph_density", 0.0),
                                "graph_density": graph_metrics.get("graph_density", 0.0),
                                "has_bottleneck": graph_metrics.get("has_bottleneck", False),
                                "isolated_agents": graph_metrics.get("isolated_agents", []),
                                "bottlenecks": graph_metrics.get("bottlenecks", []),
                            },
                        }
                    ],
                    "evaluation": agentbeats_output.to_dict(),
                },
            )

        except Exception as e:
            return JSONRPCResponse(
                id=request.id,
                error={"code": -32000, "message": f"Server error: {e!s}"},
            )

    return app


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="Green Agent A2A HTTP Server")

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=9009,
        help="Port to bind to (default: 9009)",
    )

    parser.add_argument(
        "--card-url",
        type=str,
        default="http://localhost:9009",  # TODO: Make configurable via env var
        help="AgentCard URL (default: http://localhost:9009)",
    )

    return parser.parse_args(args)


def main() -> None:
    """Main entry point for server."""
    import uvicorn

    args = parse_args()

    app = create_app()

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
