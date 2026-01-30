"""A2A HTTP server implementation.

Implements A2A-compliant HTTP server with AgentCard endpoint, health checks,
and task delegation to Executor -> Agent pipeline.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from typing import Any

from fastapi import FastAPI

from green.executor import Executor
from green.messenger import Messenger
from green.models import (
    AgentBeatsOutputModel,
    CallType,
    InteractionStep,
    JSONRPCRequest,
    JSONRPCResponse,
    get_agent_extensions,
)
from green.settings import GreenSettings


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


class _LLMJudgeEvaluator:
    """Wrapper for LLM judge evaluation."""

    async def evaluate(
        self, traces: list[InteractionStep], graph_results: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        from green.evals.llm_judge import llm_evaluate

        result = await llm_evaluate(traces, graph_metrics=graph_results)
        return result.model_dump()


class _LatencyEvaluator:
    """Wrapper for latency evaluation."""

    async def evaluate(self, traces: list[InteractionStep]) -> dict[str, Any]:
        from green.evals.system import evaluate_latency

        metrics = evaluate_latency(traces)
        return metrics.model_dump()


async def _process_evaluation_request(
    task_description: str,
    interaction_pattern: dict[str, Any] | None,
    settings: GreenSettings,
) -> dict[str, Any]:
    """Process evaluation request and return results."""
    from green.evals.graph import GraphEvaluator

    executor = Executor(
        coordination_rounds=settings.coordination_rounds,
        round_delay_seconds=settings.round_delay_seconds,
    )

    if interaction_pattern:
        traces = _build_traces_from_pattern(interaction_pattern)
    else:
        messenger = Messenger()
        traces = await executor.execute_task(
            task_description=task_description,
            messenger=messenger,
            agent_url=settings.purple_agent_url,
        )

    evaluation_results = await executor.evaluate_all(
        traces=traces,
        graph_evaluator=GraphEvaluator(),
        llm_judge=_LLMJudgeEvaluator(),
        latency_evaluator=_LatencyEvaluator(),
    )

    agentbeats_output = AgentBeatsOutputModel.from_evaluation_results(
        evaluation_results=evaluation_results,
        domain=settings.domain,
        max_score=settings.max_score,
    )

    settings.output_file.parent.mkdir(parents=True, exist_ok=True)
    with settings.output_file.open("w") as f:
        f.write(agentbeats_output.to_json(indent=2))

    tier1_graph: Any = evaluation_results.get("tier1_graph") or {}
    graph_metrics: dict[str, Any] = (
        tier1_graph.model_dump() if hasattr(tier1_graph, "model_dump") else {}
    )

    return {
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
    }


def create_app(settings: GreenSettings | None = None) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        settings: Optional GreenSettings instance (defaults to new instance)

    Returns:
        Configured FastAPI application instance
    """
    if settings is None:
        settings = GreenSettings()

    app = FastAPI(title="Green Agent A2A Server")

    @app.get("/.well-known/agent-card.json")
    async def get_agent_card() -> dict[str, Any]:  # pyright: ignore[reportUnusedFunction]
        """Return AgentCard per A2A protocol specification.

        Returns:
            AgentCard with agent metadata and capabilities
        """
        return {
            "agentId": settings.agent_uuid,
            "name": "Green Agent (Assessor)",
            "description": (
                "Multi-agent coordination quality evaluator using graph analysis, "
                "LLM assessment, and latency metrics"
            ),
            "version": settings.agent_version,
            "url": settings.get_card_url(),
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
        """Handle A2A JSON-RPC 2.0 protocol requests."""
        try:
            if request.method != "message/send":
                return JSONRPCResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {request.method}"},
                )

            task_params = request.params.get("task", {})
            task_description = task_params.get("description", "")
            interaction_pattern = task_params.get("interaction_pattern")

            if not task_description:
                return JSONRPCResponse(
                    id=request.id,
                    error={"code": -32602, "message": "Invalid params: task.description required"},
                )

            result = await _process_evaluation_request(
                task_description, interaction_pattern, settings
            )
            return JSONRPCResponse(id=request.id, result=result)

        except Exception as e:
            return JSONRPCResponse(
                id=request.id,
                error={"code": -32000, "message": f"Server error: {e!s}"},
            )

    return app


def parse_args(
    args: list[str] | None = None, settings: GreenSettings | None = None
) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Optional list of arguments (for testing)
        settings: Optional GreenSettings for defaults (defaults to new instance)

    Returns:
        Parsed arguments namespace
    """
    if settings is None:
        settings = GreenSettings()

    parser = argparse.ArgumentParser(description="Green Agent A2A HTTP Server")

    parser.add_argument(
        "--host",
        type=str,
        default=settings.host,
        help=f"Host to bind to (default: {settings.host})",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port to bind to (default: {settings.port})",
    )

    parser.add_argument(
        "--card-url",
        type=str,
        default=settings.get_card_url(),
        help=f"AgentCard URL (default: {settings.get_card_url()}, override via GREEN_CARD_URL)",
    )

    return parser.parse_args(args)


def main() -> None:
    """Main entry point for server."""
    import uvicorn

    settings = GreenSettings()
    args = parse_args(settings=settings)

    app = create_app(settings=settings)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
