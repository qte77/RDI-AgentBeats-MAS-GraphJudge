"""Tests for LLM prompt engineering for coordination assessment."""

from __future__ import annotations

from datetime import datetime

from green.evals.llm_judge import LLMJudgment, build_prompt
from green.models import CallType, InteractionStep


def test_llm_judgment_model_has_required_fields() -> None:
    """Test that LLMJudgment model includes all required fields from acceptance criteria."""
    judgment = LLMJudgment(
        overall_score=0.85,
        reasoning="Good coordination observed with efficient task delegation.",
        coordination_quality="high",
        strengths=["Efficient task delegation", "Clear communication"],
        weaknesses=["Minor delay in one agent response"],
    )

    assert judgment.overall_score == 0.85
    assert judgment.reasoning == "Good coordination observed with efficient task delegation."
    assert judgment.coordination_quality == "high"
    assert judgment.strengths == ["Efficient task delegation", "Clear communication"]
    assert judgment.weaknesses == ["Minor delay in one agent response"]


def test_llm_judgment_overall_score_range() -> None:
    """Test that overall_score is between 0 and 1."""
    judgment = LLMJudgment(
        overall_score=0.0,
        reasoning="Test",
        coordination_quality="low",
        strengths=[],
        weaknesses=["Test"],
    )
    assert 0.0 <= judgment.overall_score <= 1.0

    judgment = LLMJudgment(
        overall_score=1.0,
        reasoning="Test",
        coordination_quality="high",
        strengths=["Test"],
        weaknesses=[],
    )
    assert 0.0 <= judgment.overall_score <= 1.0


def test_build_prompt_includes_trace_data_serialization() -> None:
    """Test that prompt includes serialized TraceData from InteractionSteps."""
    steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=1000,
        ),
        InteractionStep(
            step_id="step-2",
            trace_id="trace-1",
            call_type=CallType.TOOL,
            start_time=datetime(2024, 1, 1, 12, 0, 1),
            end_time=datetime(2024, 1, 1, 12, 0, 2),
            latency=1000,
        ),
    ]

    prompt = build_prompt(steps)

    # Verify trace data is serialized in prompt
    assert "step-1" in prompt
    assert "step-2" in prompt
    assert "trace-1" in prompt
    assert "AGENT" in prompt
    assert "TOOL" in prompt
    assert "1000" in prompt  # latency


def test_build_prompt_includes_evaluation_criteria() -> None:
    """Test that prompt includes evaluation criteria for coordination quality."""
    steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=1000,
        ),
    ]

    prompt = build_prompt(steps)

    # Verify evaluation criteria are mentioned
    assert "coordination" in prompt.lower() or "evaluate" in prompt.lower()
    assert "quality" in prompt.lower() or "assessment" in prompt.lower()


def test_build_prompt_includes_json_schema() -> None:
    """Test that prompt includes JSON schema for LLMJudgment response format."""
    steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=1000,
        ),
    ]

    prompt = build_prompt(steps)

    # Verify JSON schema fields are documented in prompt
    assert "overall_score" in prompt
    assert "reasoning" in prompt
    assert "coordination_quality" in prompt
    assert "strengths" in prompt
    assert "weaknesses" in prompt


def test_build_prompt_specifies_score_range() -> None:
    """Test that prompt specifies overall_score must be between 0 and 1."""
    steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=1000,
        ),
    ]

    prompt = build_prompt(steps)

    # Verify score range is specified
    assert "0" in prompt and "1" in prompt
    assert "score" in prompt.lower()


def test_build_prompt_requests_structured_output() -> None:
    """Test that prompt requests structured JSON output."""
    steps = [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=datetime(2024, 1, 1, 12, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 1),
            latency=1000,
        ),
    ]

    prompt = build_prompt(steps)

    # Verify prompt requests JSON format
    assert "json" in prompt.lower() or "JSON" in prompt
