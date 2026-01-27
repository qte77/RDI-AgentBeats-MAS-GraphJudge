"""A2A HTTP server implementation for Purple Agent.

Implements A2A-compliant HTTP server with AgentCard endpoint, health checks,
and task delegation following green-agent-template pattern.
"""

from __future__ import annotations

import argparse
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from purple.executor import Executor
from purple.messenger import Messenger


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
    app = FastAPI(title="Purple Agent A2A Server")

    @app.get("/.well-known/agent-card.json")
    async def get_agent_card() -> dict[str, Any]:  # pyright: ignore[reportUnusedFunction]
        """Return AgentCard per A2A protocol specification.

        Returns:
            AgentCard with agent metadata and capabilities
        """
        return {
            "agentId": "purple-agent",
            "name": "Purple Agent (Test Fixture)",
            "description": "Simple A2A-compliant agent for E2E testing and validation",
            "capabilities": {
                "protocols": ["a2a"],
                "extensions": [],
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
            JSON-RPC response with task results

        Raises:
            HTTPException: If request processing fails
        """
        try:
            if request.method != "tasks.send":
                return JSONRPCResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {request.method}"},
                )

            # Extract task description
            task_params = request.params.get("task", {})
            task_description = task_params.get("description", "")

            if not task_description:
                return JSONRPCResponse(
                    id=request.id,
                    error={"code": -32602, "message": "Invalid params: task.description required"},
                )

            # Execute task via Executor
            executor = Executor()
            messenger = Messenger()

            result = await executor.execute_task(
                task_description=task_description,
                messenger=messenger,
                agent_url="http://localhost:9010",  # Purple agent URL
            )

            # Return JSON-RPC success response
            return JSONRPCResponse(
                id=request.id,
                result={
                    "status": "completed",
                    "response": result,
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
    parser = argparse.ArgumentParser(description="Purple Agent A2A HTTP Server")

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=9010,
        help="Port to bind to (default: 9010)",
    )

    parser.add_argument(
        "--card-url",
        type=str,
        default="http://localhost:9010",
        help="AgentCard URL (default: http://localhost:9010)",
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
