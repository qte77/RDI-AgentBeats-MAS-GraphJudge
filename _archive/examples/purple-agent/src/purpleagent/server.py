"""A2A server entry point for Purple Agent."""

from __future__ import annotations

import argparse
import uuid

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, Message, Role, TextPart


class PurpleAgentExecutor(AgentExecutor):
    """Simple A2A AgentExecutor for demonstration purposes."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute a simple coordination task.

        Args:
            context: Request context containing task information
            event_queue: Queue for publishing task events and results
        """
        task_id = context.task_id or "unknown"

        # Simple coordination response - echo back a friendly message
        response_text = (
            "Purple Agent responding! I'm a simple demo agent that can participate "
            "in coordination scenarios. I can process requests and provide structured "
            "responses for evaluation."
        )

        # Create response message
        text_parts: list[TextPart] = [TextPart(text=response_text)]
        message = Message(
            message_id=str(uuid.uuid4()),
            task_id=task_id,
            role=Role.agent,
            parts=text_parts,  # type: ignore[reportArgumentType]
            metadata={
                "agent": "purple",
                "status": "success",
                "coordination_ready": True,
            },
        )
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel an ongoing task.

        Args:
            context: Request context containing task information
            event_queue: Queue for publishing cancellation events
        """
        # Simple agent - tasks are atomic and cannot be canceled
        pass


def create_agent_card(card_url: str | None = None) -> AgentCard:
    """Create the AgentCard for Purple Agent.

    Args:
        card_url: Optional custom URL for the agent card endpoint

    Returns:
        AgentCard with agent metadata
    """
    skills = [
        AgentSkill(
            id="coordination",
            name="Coordination",
            description="Participates in simple multi-agent coordination scenarios",
            tags=["coordination", "demo", "simple"],
        ),
    ]

    return AgentCard(
        name="Purple Agent",
        description="Simple A2A-compatible demo agent for AgentBeats evaluation scenarios",
        skills=skills,
        version="0.1.0",
        url=card_url or "http://localhost:9010",
        protocol_version="1.0",
        capabilities=AgentCapabilities(),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
    )


def create_server(
    host: str = "127.0.0.1",
    port: int = 9010,
    card_url: str | None = None,
) -> A2AStarletteApplication:
    """Create and configure the A2A server.

    Args:
        host: Host address to bind to (default: 127.0.0.1 for security)
        port: Port number to bind to
        card_url: Optional custom URL for agent card metadata

    Returns:
        Configured A2AStarletteApplication instance
    """
    agent_card = create_agent_card(card_url)

    request_handler = DefaultRequestHandler(
        agent_executor=PurpleAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    return server


def main() -> None:
    """Main entry point for the A2A server."""
    parser = argparse.ArgumentParser(description="Purple Agent A2A Server")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1, use 0.0.0.0 for containers)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9010,
        help="Port number to bind to (default: 9010)",
    )
    parser.add_argument(
        "--card-url",
        type=str,
        default=None,
        help="Custom URL for agent card metadata (default: http://localhost:9010)",
    )

    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("Port must be in range 1-65535")

    server = create_server(
        host=args.host,
        port=args.port,
        card_url=args.card_url,
    )

    app = server.build()

    print(f"Starting Purple Agent on {args.host}:{args.port}")
    print(f"Agent card available at: http://{args.host}:{args.port}/.well-known/agent-card.json")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
