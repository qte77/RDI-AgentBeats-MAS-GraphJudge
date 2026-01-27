"""Messenger for A2A agent-to-agent communication.

Implements real agent communication using A2A SDK for authentic coordination measurement.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from a2a.client import Client, ClientFactory, create_text_message_object
from a2a.types import TaskState

if TYPE_CHECKING:
    pass


class Messenger:
    """Agent messenger using A2A SDK."""

    def __init__(self) -> None:
        """Initialize messenger with client cache."""
        self._clients: dict[str, Client] = {}

    async def send_message(self, url: str, message: str, extensions: list[str] | None = None) -> str:
        """Send message to agent via A2A protocol.

        Args:
            url: Agent URL endpoint
            message: Text message content
            extensions: Optional X-A2A-Extensions headers

        Returns:
            Response text from completed task

        Raises:
            A2AClientError: If A2A protocol communication fails
        """
        # Get or create cached client for this URL
        if url not in self._clients:
            self._clients[url] = await ClientFactory.connect(url)

        client = self._clients[url]

        # Create message via A2A SDK
        msg = create_text_message_object(content=message)

        # Send message and iterate over events
        async for result in client.send_message(msg, extensions=extensions):
            if isinstance(result, tuple):
                task, _event = result
                if task.status.state == TaskState.completed:
                    # Extract response from completed task artifacts
                    if task.artifacts:
                        return task.artifacts[0].parts[0].root.text  # type: ignore[union-attr]
                    return ""

        return ""

    async def close(self) -> None:
        """Close all cached client connections."""
        for client in self._clients.values():
            await client.close()  # type: ignore[attr-defined]
        self._clients.clear()
