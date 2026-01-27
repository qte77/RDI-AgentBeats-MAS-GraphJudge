"""Messenger for A2A agent-to-agent communication.

Stub implementation for RED phase - tests should fail.
"""

from __future__ import annotations


class Messenger:
    """Agent messenger using A2A SDK (stub for RED phase)."""

    async def send_message(self, url: str, message: str) -> str:
        """Send message to agent (not implemented yet)."""
        raise NotImplementedError("RED phase - not implemented yet")

    async def close(self) -> None:
        """Close all client connections (not implemented yet)."""
        raise NotImplementedError("RED phase - not implemented yet")
