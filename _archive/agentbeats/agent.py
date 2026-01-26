"""Agent orchestrator for coordinating agent evaluation workflows."""

from __future__ import annotations

import time
import uuid
from typing import Any

from pydantic import BaseModel, Field

from agentbeats.executor import Executor


class EvalRequest(BaseModel):
    """Request model for agent evaluation."""

    agent_url: str
    messages: list[str] = Field(default_factory=list)
    task_id: str = Field(default_factory=lambda: f"task-{uuid.uuid4()}")


class EvalResult(BaseModel):
    """Result model for agent evaluation."""

    task_id: str
    agent_url: str
    status: str
    results: dict[str, dict[str, Any]] | None = None
    duration_seconds: float | None = None
    error: str | None = None


class Agent:
    """Orchestrates agent evaluation workflows with fresh state per assessment."""

    def __init__(self) -> None:
        """Initialize agent orchestrator."""
        pass

    async def run(self, request: EvalRequest) -> EvalResult:
        """Run a complete evaluation workflow for an agent.

        This method orchestrates the full evaluation flow:
        1. Creates a fresh Executor instance (no state leakage)
        2. Uses task_id to namespace temporary resources
        3. Delegates multi-tier evaluation coordination to Executor
        4. Returns structured results or error information

        Args:
            request: EvalRequest containing agent_url, messages, and task_id

        Returns:
            EvalResult with evaluation outcomes from all tiers
        """
        start_time = time.time()

        try:
            # Create fresh executor for this evaluation (fresh state per assessment)
            executor = Executor()

            # Execute evaluation with task_id namespacing
            task_result = await executor.execute(
                task_id=request.task_id,
                agent_url=request.agent_url,
                messages=request.messages,
            )

            # Map executor result to agent result
            duration = time.time() - start_time

            return EvalResult(
                task_id=request.task_id,
                agent_url=request.agent_url,
                status=task_result.state,
                results=task_result.results,
                duration_seconds=duration,
                error=None if task_result.state == "completed" else "Evaluation failed",
            )

        except Exception as e:
            # Handle errors gracefully
            duration = time.time() - start_time

            return EvalResult(
                task_id=request.task_id,
                agent_url=request.agent_url,
                status="failed",
                results=None,
                duration_seconds=duration,
                error=str(e),
            )
