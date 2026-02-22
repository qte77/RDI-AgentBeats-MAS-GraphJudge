"""Tests for BaseEvaluator ABC.

Validates the BaseEvaluator abstract base class and that existing
evaluators conform to the interface documented in AGENTBEATS_REGISTRATION.md.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest


def test_base_evaluator_importable() -> None:
    """Test that BaseEvaluator is importable from green.evals.base."""
    from green.evals.base import BaseEvaluator

    assert BaseEvaluator is not None


def test_base_evaluator_is_abc() -> None:
    """Test that BaseEvaluator is an ABC with abstract evaluate method."""
    from green.evals.base import BaseEvaluator

    # Must be abstract — instantiation should raise TypeError
    with pytest.raises(TypeError):
        BaseEvaluator()  # type: ignore[abstract]


def test_base_evaluator_evaluate_signature() -> None:
    """Test that evaluate has correct signature: (self, traces, **context) -> dict[str, Any]."""
    from green.evals.base import BaseEvaluator

    sig = inspect.signature(BaseEvaluator.evaluate)
    params = list(sig.parameters.keys())
    assert "self" in params
    assert "traces" in params
    assert "context" in params  # **context


def test_base_evaluator_tier_defaults_to_3() -> None:
    """Test that BaseEvaluator.tier property defaults to 3."""
    from green.evals.base import BaseEvaluator
    from green.models import InteractionStep

    # Create a concrete subclass to test the default tier
    class _Stub(BaseEvaluator):
        async def evaluate(self, traces: list[InteractionStep], **context: Any) -> dict[str, Any]:
            return {}

    assert _Stub().tier == 3


def test_llm_judge_evaluator_is_base_evaluator() -> None:
    """Test that _LLMJudgeEvaluator is a BaseEvaluator subclass."""
    from green.evals.base import BaseEvaluator
    from green.server import _LLMJudgeEvaluator

    assert issubclass(_LLMJudgeEvaluator, BaseEvaluator)


def test_latency_evaluator_is_base_evaluator() -> None:
    """Test that _LatencyEvaluator is a BaseEvaluator subclass."""
    from green.evals.base import BaseEvaluator
    from green.server import _LatencyEvaluator

    assert issubclass(_LatencyEvaluator, BaseEvaluator)
