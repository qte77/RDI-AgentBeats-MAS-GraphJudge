"""Executor for Purple Agent task execution.

Simple executor for test fixture - executes tasks and returns results.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from purple.messenger import Messenger


class Executor:
    """Simple executor for Purple Agent test fixture."""

    def __init__(self) -> None:
        """Initialize executor."""
        pass

    async def execute_task(self, task_description: str, messenger: Messenger, agent_url: str) -> str:
        """Execute task and return result.

        Args:
            task_description: Task description to execute
            messenger: Messenger instance for agent communication
            agent_url: URL of agent to communicate with

        Returns:
            Task execution result

        Raises:
            Exception: If task execution fails
        """
        try:
            # For simple test fixture, just echo back the task description
            # In real implementation, would process task and generate meaningful response
            result = f"Purple Agent processed: {task_description}"
            return result

        finally:
            # Always cleanup messenger connections
            await messenger.close()
