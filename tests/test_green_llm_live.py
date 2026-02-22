"""Live LLM connectivity tests - STORY-035.

Network-gated tests that validate real LLM API calls without mocks.
Tests skip automatically when AGENTBEATS_LLM_API_KEY env var is unset.

Run with network tests: uv run pytest tests/ -m network
Exclude network tests:  uv run pytest tests/ -m "not network and not integration"
"""

from __future__ import annotations

import os
from datetime import datetime

import pytest

from green.evals.llm_judge import get_llm_config, llm_evaluate
from green.models import CallType, InteractionStep, LLMJudgment

pytestmark = pytest.mark.network


@pytest.fixture(scope="module", autouse=True)
def require_api_key() -> None:
    """Skip all network tests when AGENTBEATS_LLM_API_KEY is not set."""
    if not os.environ.get("AGENTBEATS_LLM_API_KEY"):
        pytest.skip("AGENTBEATS_LLM_API_KEY not set - skipping live LLM tests")


@pytest.fixture
def sample_steps() -> list[InteractionStep]:
    """Create sample interaction steps for live API testing."""
    return [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-live-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=1000,
        ),
        InteractionStep(
            step_id="step-2",
            trace_id="trace-live-1",
            call_type=CallType.TOOL,
            start_time=datetime(2024, 1, 1, 12, 0, 1),
            end_time=datetime(2024, 1, 1, 12, 0, 2),
            latency=500,
        ),
    ]


def test_live_llm_temperature_config_is_zero() -> None:
    """Live test: LLM config uses temperature=0 for deterministic responses."""
    config = get_llm_config()
    assert config.temperature == 0.0


async def test_live_llm_evaluate_returns_valid_judgment(
    sample_steps: list[InteractionStep],
) -> None:
    """Live test: real API call returns valid LLMJudgment structure."""
    result = await llm_evaluate(sample_steps)

    assert isinstance(result, LLMJudgment)
    assert 0.0 <= result.overall_score <= 1.0
    assert result.reasoning
    assert result.coordination_quality in ("low", "medium", "high")
    assert isinstance(result.strengths, list)
    assert isinstance(result.weaknesses, list)
    # Confirm LLM (not rule-based fallback) responded
    assert not result.reasoning.startswith("Rule-based evaluation:")
