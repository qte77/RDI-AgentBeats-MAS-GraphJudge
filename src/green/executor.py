"""Executor with trace collection and cleanup.

Collects interaction traces during task execution and provides cleanup.
Real agent-to-agent communication enables authentic coordination measurement.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from green.evals.system import LatencyMetrics, evaluate_latency
from green.models import CallType, InteractionStep

if TYPE_CHECKING:
    from green.messenger import Messenger


class Executor:
    """Executor that collects interaction traces and manages cleanup."""

    def __init__(self) -> None:
        """Initialize executor."""
        pass

    async def execute_task(self, task_description: str, messenger: Messenger, agent_url: str) -> list[InteractionStep]:
        """Execute task and collect interaction traces.

        Args:
            task_description: Task description to send to agent
            messenger: Messenger instance for agent communication
            agent_url: URL of agent to communicate with

        Returns:
            List of InteractionStep traces collected during execution

        Raises:
            Exception: If task execution fails (after cleanup)
        """
        traces: list[InteractionStep] = []
        trace_id = str(uuid.uuid4())

        try:
            # Record start time
            start_time = datetime.now()

            # Send message via messenger
            await messenger.send_message(url=agent_url, message=task_description)

            # Record end time
            end_time = datetime.now()

            # Calculate latency in milliseconds
            latency = int((end_time - start_time).total_seconds() * 1000)

            # Create interaction step
            step = InteractionStep(
                step_id=str(uuid.uuid4()),
                trace_id=trace_id,
                call_type=CallType.AGENT,
                start_time=start_time,
                end_time=end_time,
                latency=latency,
            )

            traces.append(step)

            return traces

        finally:
            # Always cleanup messenger connections
            await messenger.close()

    def _evaluate_latency(self, steps: list[InteractionStep]) -> LatencyMetrics:
        """Evaluate latency metrics from interaction steps.

        Part of Tier 2 assessment. Computes percentiles and identifies
        performance bottlenecks within the same system/run.

        Args:
            steps: List of InteractionStep traces to analyze

        Returns:
            LatencyMetrics with percentiles and slowest agent identification
        """
        return evaluate_latency(steps)
