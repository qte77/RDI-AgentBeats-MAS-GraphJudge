"""A2A HTTP server implementation for Purple Agent.

Implements A2A-compliant HTTP server with AgentCard endpoint, health checks,
and task delegation following green-agent-template pattern.
"""

from __future__ import annotations

import argparse
import uuid
from typing import Any

from fastapi import FastAPI

from purple.executor import Executor
from purple.messenger import Messenger
from purple.models import JSONRPCRequest, JSONRPCResponse
from purple.settings import PurpleSettings


def _extract_text_from_part(part: Any) -> str:
    """Extract text from an A2A message part."""
    if not isinstance(part, dict):
        return ""
    # Try direct text field first, then nested root.text
    text = part.get("text", "")
    if not text:
        root = part.get("root")
        if isinstance(root, dict):
            text = root.get("text", "")
    return str(text) if text else ""  # type: ignore[arg-type]


def _extract_task_description(params: dict[str, Any]) -> str:
    """Extract task description from A2A message or legacy task format.

    Args:
        params: JSON-RPC request params

    Returns:
        Task description string, empty if not found
    """
    # Try A2A standard message format: params.message.parts[0].text
    message = params.get("message")
    if isinstance(message, dict):
        parts = message.get("parts")
        if isinstance(parts, list) and parts:
            text = _extract_text_from_part(parts[0])
            if text:
                return text

    # Fall back to legacy: params.task.description
    task = params.get("task")
    if isinstance(task, dict):
        desc = task.get("description", "")
        if desc:
            return str(desc)  # type: ignore[arg-type]

    return ""


def create_app(settings: PurpleSettings | None = None) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        settings: Optional PurpleSettings instance (defaults to new instance)

    Returns:
        Configured FastAPI application instance
    """
    if settings is None:
        settings = PurpleSettings()

    app = FastAPI(title="Purple Agent A2A Server")

    @app.get("/.well-known/agent-card.json")
    async def get_agent_card() -> dict[str, Any]:  # pyright: ignore[reportUnusedFunction]
        """Return AgentCard per A2A protocol specification.

        Returns:
            AgentCard with agent metadata and capabilities
        """
        return {
            "agentId": str(settings.agent_uuid),
            "name": "Purple Agent (Test Fixture)",
            "description": "Simple A2A-compliant agent for E2E testing and validation",
            "version": "1.0.0",
            "url": settings.get_card_url(),
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
            "skills": [
                {
                    "id": "process",
                    "name": "Process Task",
                    "description": "Process simple test tasks",
                    "tags": ["testing", "validation"],
                }
            ],
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
            if request.method != "message/send":
                return JSONRPCResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {request.method}"},
                )

            task_description = _extract_task_description(request.params)

            if not task_description:
                return JSONRPCResponse(
                    id=request.id,
                    error={
                        "code": -32602,
                        "message": "Invalid params: message.parts or task.description required",
                    },
                )

            # Execute task via Executor
            executor = Executor()
            messenger = Messenger(a2a_settings=settings.a2a)

            result = await executor.execute_task(
                task_description=task_description,
                messenger=messenger,
                agent_url=settings.get_card_url(),
            )

            # Return A2A-compliant JSON-RPC success response
            return JSONRPCResponse(
                id=request.id,
                result={
                    "id": str(uuid.uuid4()),
                    "contextId": str(uuid.uuid4()),
                    "status": {"state": "completed"},
                    "artifacts": [
                        {
                            "artifactId": str(uuid.uuid4()),
                            "parts": [
                                {
                                    "kind": "text",
                                    "text": result,
                                }
                            ],
                        }
                    ],
                },
            )

        except Exception as e:
            return JSONRPCResponse(
                id=request.id,
                error={"code": -32000, "message": f"Server error: {e!s}"},
            )

    return app


def parse_args(
    args: list[str] | None = None, settings: PurpleSettings | None = None
) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Optional list of arguments (for testing)
        settings: Optional PurpleSettings for defaults (defaults to new instance)

    Returns:
        Parsed arguments namespace
    """
    if settings is None:
        settings = PurpleSettings()

    parser = argparse.ArgumentParser(description="Purple Agent A2A HTTP Server")

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
        help=f"AgentCard URL (default: {settings.get_card_url()}, override via PURPLE_CARD_URL)",
    )

    return parser.parse_args(args)


def main() -> None:
    """Main entry point for server."""
    import uvicorn

    settings = PurpleSettings()
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
