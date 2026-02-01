"""Messenger for A2A agent-to-agent communication.

Implements real agent communication using A2A SDK for authentic coordination measurement.
Shared by both Green and Purple agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from a2a.client import Client, ClientConfig, ClientFactory, create_text_message_object
from a2a.types import TaskState

from common.settings import A2ASettings

if TYPE_CHECKING:
    pass


class Messenger:
    """Agent messenger using A2A SDK."""

    def __init__(self, a2a_settings: A2ASettings | None = None) -> None:
        """Initialize messenger with client cache.

        Args:
            a2a_settings: A2A configuration settings for timeout and connection parameters
        """
        self._clients: dict[str, Client] = {}
        self._settings = a2a_settings or A2ASettings()

    async def send_message(
        self, url: str, message: str, extensions: list[str] | None = None
    ) -> str:
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
            # Configure httpx client with proper timeout settings
            timeout = httpx.Timeout(
                timeout=self._settings.timeout,
                connect=self._settings.connect_timeout,
            )
            httpx_client = httpx.AsyncClient(timeout=timeout)

            # Create client config with configured httpx client
            client_config = ClientConfig(httpx_client=httpx_client)

            # Connect using ClientFactory with timeout-configured client
            self._clients[url] = await ClientFactory.connect(url, client_config=client_config)

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
