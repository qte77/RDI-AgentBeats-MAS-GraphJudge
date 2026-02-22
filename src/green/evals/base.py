"""Base evaluator ABC for the AgentBeats evaluation pipeline.

All custom Tier 3 evaluators must subclass BaseEvaluator and implement
the evaluate() method. See docs/AgentBeats/AGENTBEATS_REGISTRATION.md.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from green.models import InteractionStep


class BaseEvaluator(ABC):
    """Interface for custom Tier 3 evaluators."""

    @abstractmethod
    async def evaluate(
        self,
        traces: list[InteractionStep],
        **context: Any,
    ) -> dict[str, Any]:
        """Evaluate agent traces and return a results dict.

        Args:
            traces: Collected interaction steps from a task run.
            **context: Optional context (e.g., graph_results from Tier 1).

        Returns:
            Dict of evaluation results keyed by metric name.
        """

    @property
    def tier(self) -> int:
        return 3
