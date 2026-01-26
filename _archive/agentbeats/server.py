"""A2A server entry point for AgentBeats GreenAgent."""

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

from agentbeats.agent import Agent, EvalRequest


class AgentBeatsExecutor(AgentExecutor):
    """A2A AgentExecutor implementation for AgentBeats evaluation tasks."""

    def __init__(self) -> None:
        """Initialize the executor with an Agent orchestrator."""
        self._agent = Agent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute evaluation task and publish results to event queue.

        Args:
            context: Request context containing task information
            event_queue: Queue for publishing task events and results
        """
        # Extract request parameters from context
        task_id = context.task_id or "unknown"

        # For A2A evaluation, we need the agent URL and messages
        # Get message content from context
        message_content = context.message if hasattr(context, "message") else ""
        agent_url = str(message_content) if message_content else "http://localhost:9009"
        messages: list[str] = []

        # Create evaluation request
        eval_request = EvalRequest(
            agent_url=agent_url,
            messages=messages,
            task_id=task_id,
        )

        # Run evaluation
        result = await self._agent.run(eval_request)

        # Publish results to event queue as a Message
        text_parts: list[TextPart] = [
            TextPart(
                text=f"Evaluation completed with status: {result.status}",
            )
        ]
        message = Message(
            message_id=str(uuid.uuid4()),
            task_id=task_id,
            role=Role.agent,
            parts=text_parts,  # type: ignore[reportArgumentType]
            metadata={
                "status": result.status,
                "results": result.results,
                "duration_seconds": result.duration_seconds,
                "error": result.error,
            },
        )
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel an ongoing task.

        Args:
            context: Request context containing task information
            event_queue: Queue for publishing cancellation events
        """
        # AgentBeats evaluations are atomic and cannot be canceled mid-flight
        # This is a no-op as per A2A protocol requirements
        pass


def create_agent_card(card_url: str | None = None) -> AgentCard:
    """Create the AgentCard for AgentBeats GreenAgent.

    Args:
        card_url: Optional custom URL for the agent card endpoint

    Returns:
        AgentCard with agent metadata
    """
    # Create skill objects
    skills = [
        AgentSkill(
            id="graph_evaluation",
            name="Graph Evaluation",
            description="Analyzes agent interaction patterns using graph metrics",
            tags=["evaluation", "graph", "metrics"],
        ),
        AgentSkill(
            id="llm_judging",
            name="LLM Judging",
            description="Evaluates agent responses using LLM-based judgment",
            tags=["evaluation", "llm", "judgment"],
        ),
        AgentSkill(
            id="text_metrics",
            name="Text Metrics",
            description="Measures text similarity between agent responses",
            tags=["evaluation", "text", "similarity"],
        ),
        AgentSkill(
            id="agent_assessment",
            name="Agent Assessment",
            description="Comprehensive multi-tier evaluation of agent coordination",
            tags=["evaluation", "assessment", "coordination"],
        ),
    ]

    return AgentCard(
        name="AgentBeats GreenAgent",
        description=(
            "Multi-tier evaluation agent for assessing agent coordination "
            "using graph metrics, LLM judgment, and text similarity"
        ),
        skills=skills,
        version="0.1.0",
        url=card_url or "http://localhost:9009",
        protocol_version="1.0",
        capabilities=AgentCapabilities(),
        default_input_modes=["text/plain"],
        default_output_modes=["application/json"],
    )


def create_server(
    host: str = "127.0.0.1",
    port: int = 9009,
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
    # Create agent card
    agent_card = create_agent_card(card_url)

    # Create request handler with executor and task store
    request_handler = DefaultRequestHandler(
        agent_executor=AgentBeatsExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # Create A2A Starlette application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    return server


def main() -> None:
    """Main entry point for the A2A server."""
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="AgentBeats GreenAgent A2A Server")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1, use 0.0.0.0 for containers)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9009,
        help="Port number to bind to (default: 9009)",
    )
    parser.add_argument(
        "--card-url",
        type=str,
        default=None,
        help="Custom URL for agent card metadata (default: http://localhost:9009)",
    )

    args = parser.parse_args()

    # Validate port range
    if not 1 <= args.port <= 65535:
        parser.error("Port must be in range 1-65535")

    # Create server
    server = create_server(
        host=args.host,
        port=args.port,
        card_url=args.card_url,
    )

    # Build and run server
    app = server.build()

    print(f"Starting AgentBeats GreenAgent on {args.host}:{args.port}")
    print(f"Agent card available at: http://{args.host}:{args.port}/.well-known/agent-card.json")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
