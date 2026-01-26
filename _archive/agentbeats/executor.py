"""A2A task executor for coordinating multi-tier agent evaluations."""

from __future__ import annotations

import logging
import time
from typing import Any

from pydantic import BaseModel

from agentbeats.evals.graph import GraphEvaluator
from agentbeats.evals.latency import LatencyEvaluator
from agentbeats.evals.llm_judge import LLMJudge
from agentbeats.evals.text_metrics import TextMetrics
from agentbeats.messenger import Messenger, TraceData

logger = logging.getLogger(__name__)


class TaskStatus(BaseModel):
    """Task status information following A2A protocol."""

    task_id: str
    state: str  # pending, working, completed, failed, canceled
    progress: float | None = None  # 0-1 progress indicator
    message: str | None = None  # Status message
    error: str | None = None  # Error message if failed


class TaskResult(BaseModel):
    """Task execution result with multi-tier evaluation data."""

    task_id: str
    state: str
    results: dict[str, dict[str, Any]] | None = None  # Evaluation results by tier
    artifacts: list[str] | None = None  # Generated artifacts (URLs, files)
    duration_seconds: float | None = None  # Execution duration


class Executor:
    """Coordinates A2A task execution and multi-tier evaluations."""

    def __init__(self) -> None:
        """Initialize executor with empty task state."""
        self._tasks: dict[str, TaskStatus] = {}

    async def execute(
        self,
        task_id: str,
        agent_url: str,
        messages: list[str] | None = None,
    ) -> TaskResult:
        """Execute an evaluation task coordinating all evaluation tiers.

        Args:
            task_id: Unique task identifier for namespacing
            agent_url: URL of the agent to evaluate
            messages: Optional list of messages to send to the agent

        Returns:
            TaskResult with aggregated multi-tier evaluation results
        """
        start_time = time.time()

        # Initialize task in pending state
        self._tasks[task_id] = TaskStatus(
            task_id=task_id,
            state="pending",
            message="Task created",
        )

        # Initialize fresh messenger for this task
        messenger = Messenger()

        try:
            # Transition to working state
            self._tasks[task_id] = TaskStatus(
                task_id=task_id,
                state="working",
                progress=0.0,
                message="Starting evaluation",
            )

            # Collect traces if messages provided
            if messages:
                for i, message in enumerate(messages):
                    try:
                        await messenger.talk_to_agent(agent_url, message)
                    except Exception as e:
                        # Log error but continue with other messages
                        logger.warning(f"Failed to send message {i + 1}/{len(messages)} to {agent_url}: {e}")

                    # Update progress
                    progress = (i + 1) / (len(messages) + 3)  # Account for eval steps
                    self._tasks[task_id] = TaskStatus(
                        task_id=task_id,
                        state="working",
                        progress=progress,
                        message=f"Processed message {i + 1}/{len(messages)}",
                    )

            traces = messenger.get_traces()

            # Coordinate Tier 1: Graph evaluation
            self._tasks[task_id] = TaskStatus(
                task_id=task_id,
                state="working",
                progress=0.6,
                message="Running Tier 1 graph evaluation",
            )
            tier1_result = await self._evaluate_tier1(traces)

            # Coordinate Tier 2: LLM judge evaluation
            self._tasks[task_id] = TaskStatus(
                task_id=task_id,
                state="working",
                progress=0.8,
                message="Running Tier 2 LLM judge evaluation",
            )
            tier2_result = await self._evaluate_tier2(traces)

            # Coordinate Tier 3: Text metrics evaluation
            self._tasks[task_id] = TaskStatus(
                task_id=task_id,
                state="working",
                progress=0.85,
                message="Running Tier 3 text metrics evaluation",
            )
            tier3_result = await self._evaluate_tier3(traces)

            # Coordinate Tier 1: Latency evaluation
            self._tasks[task_id] = TaskStatus(
                task_id=task_id,
                state="working",
                progress=0.95,
                message="Running Tier 1 latency evaluation",
            )
            tier1_latency = await self._evaluate_latency(traces)

            # Aggregate results
            results = {
                "tier1_graph": tier1_result,
                "tier1_latency": tier1_latency,
                "tier2_llm_judge": tier2_result,
                "tier3_text_metrics": tier3_result,
            }

            duration = time.time() - start_time

            # Transition to completed state
            self._tasks[task_id] = TaskStatus(
                task_id=task_id,
                state="completed",
                progress=1.0,
                message="Evaluation completed successfully",
            )

            return TaskResult(
                task_id=task_id,
                state="completed",
                results=results,
                duration_seconds=duration,
            )

        except Exception as e:
            # Handle failures gracefully
            duration = time.time() - start_time
            error_message = str(e)

            self._tasks[task_id] = TaskStatus(
                task_id=task_id,
                state="failed",
                message="Task execution failed",
                error=error_message,
            )

            return TaskResult(
                task_id=task_id,
                state="failed",
                duration_seconds=duration,
            )

        finally:
            # Always cleanup A2A clients, even on error
            await messenger.close()

    async def _evaluate_tier1(self, traces: list[TraceData]) -> dict[str, Any]:
        """Run Tier 1 graph evaluation.

        Args:
            traces: List of captured interaction traces

        Returns:
            Dictionary with graph metrics
        """
        try:
            evaluator = GraphEvaluator()
            evaluator.build_graph(traces)
            metrics = evaluator.get_metrics()
            return metrics.model_dump()
        except Exception as e:
            # Return error information if evaluation fails
            return {"error": str(e), "metrics": None}

    async def _evaluate_tier2(self, traces: list[TraceData]) -> dict[str, Any]:
        """Run Tier 2 LLM judge evaluation.

        Args:
            traces: List of captured interaction traces

        Returns:
            Dictionary with LLM judgment
        """
        try:
            evaluator = LLMJudge()
            judgment = await evaluator.evaluate(traces)
            return judgment.model_dump()
        except Exception as e:
            # Return error information if evaluation fails
            return {"error": str(e), "judgment": None}

    async def _evaluate_tier3(self, traces: list[TraceData]) -> dict[str, Any]:
        """Run Tier 3 text metrics evaluation.

        Args:
            traces: List of captured interaction traces

        Returns:
            Dictionary with text similarity metrics
        """
        try:
            # For text metrics, we need response-reference pairs
            # Use the first trace as reference if available
            if not traces:
                return {"error": "No traces available", "similarity_score": 0.0}

            evaluator = TextMetrics()

            # Evaluate similarity between consecutive responses
            if len(traces) >= 2:
                result = evaluator.evaluate(
                    response=traces[-1].response,
                    reference=traces[0].response,
                )
                return result.model_dump()
            elif len(traces) == 1:
                # Single trace - compare with itself (perfect similarity)
                result = evaluator.evaluate(
                    response=traces[0].response,
                    reference=traces[0].response,
                )
                return result.model_dump()
            else:
                return {"error": "No traces available", "similarity_score": 0.0}

        except Exception as e:
            # Return error information if evaluation fails
            return {"error": str(e), "similarity_score": 0.0}

    async def _evaluate_latency(self, traces: list[TraceData]) -> dict[str, Any]:
        """Run latency metrics evaluation.

        Args:
            traces: List of captured interaction traces

        Returns:
            Dictionary with latency metrics
        """
        try:
            evaluator = LatencyEvaluator()
            metrics = evaluator.evaluate(traces)
            return metrics.model_dump()
        except Exception as e:
            # Return error information if evaluation fails
            return {"error": str(e), "metrics": None}

    def get_status(self, task_id: str) -> TaskStatus | None:
        """Get the current status of a task.

        Args:
            task_id: Task identifier

        Returns:
            TaskStatus object or None if task not found
        """
        return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or working task.

        Args:
            task_id: Task identifier

        Returns:
            True if task was canceled, False if task not found or already terminal
        """
        task = self._tasks.get(task_id)
        if task and task.state in ("pending", "working"):
            self._tasks[task_id] = TaskStatus(
                task_id=task_id,
                state="canceled",
                message="Task canceled by user",
            )
            return True
        return False
