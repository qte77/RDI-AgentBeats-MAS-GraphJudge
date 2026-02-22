"""In-memory trace storage for Green Agent.

Provides centralized storage for:
- Trace collection from Purple agents
- Agent registry for peer discovery
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from common.models import InteractionStep


class TraceStore:
    """Thread-safe in-memory storage for traces and agent registry."""

    def __init__(self) -> None:
        """Initialize TraceStore with empty storage."""
        self._traces: list[InteractionStep] = []
        self._registered_agents: set[str] = set()
        self._lock = threading.Lock()

    def add_traces(self, traces: list[InteractionStep]) -> None:
        """Add traces to storage.

        Thread-safe operation for concurrent trace additions.

        Args:
            traces: List of InteractionStep traces to store
        """
        with self._lock:
            self._traces.extend(traces)

    def get_all_traces(self) -> list[InteractionStep]:
        """Get all stored traces.

        Thread-safe operation.

        Returns:
            List of all stored InteractionStep traces
        """
        with self._lock:
            return list(self._traces)

    def get_traces_by_id(self, trace_id: str) -> list[InteractionStep]:
        """Get traces filtered by trace_id.

        Thread-safe operation.

        Args:
            trace_id: Trace ID to filter by

        Returns:
            List of InteractionStep traces with matching trace_id
        """
        with self._lock:
            return [trace for trace in self._traces if trace.trace_id == trace_id]

    def clear_traces(self) -> None:
        """Clear all stored traces.

        Thread-safe operation.
        """
        with self._lock:
            self._traces.clear()

    def register_agent(self, agent_url: str) -> None:
        """Register agent URL in registry.

        Thread-safe operation. Automatically deduplicates URLs.

        Args:
            agent_url: Agent URL to register (e.g., "http://agent1:8000")
        """
        with self._lock:
            self._registered_agents.add(agent_url)

    def unregister_agent(self, agent_url: str) -> None:
        """Unregister agent URL from registry.

        Thread-safe operation.

        Args:
            agent_url: Agent URL to unregister
        """
        with self._lock:
            self._registered_agents.discard(agent_url)

    def get_registered_agents(self) -> list[str]:
        """Get list of registered agent URLs.

        Thread-safe operation.

        Returns:
            List of registered agent URLs
        """
        with self._lock:
            return list(self._registered_agents)
