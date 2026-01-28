"""LLM-based evaluation configuration and implementation.

LLMJudgment model consolidated in green.models for single source of truth.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from green.models import InteractionStep, LLMJudgment
from green.settings import LLMSettings

logger = logging.getLogger(__name__)


def get_llm_config() -> LLMSettings:
    """Get LLM configuration from environment variables.

    Returns:
        LLMSettings with values from environment or defaults
    """
    return LLMSettings()


def build_prompt(steps: list[InteractionStep]) -> str:
    """Build LLM prompt for coordination quality assessment.

    Constructs a prompt that includes:
    - Serialized TraceData from InteractionSteps
    - Evaluation criteria for coordination quality
    - JSON schema for structured LLMJudgment output
    - Request for temperature=0 for consistency

    Args:
        steps: List of InteractionStep traces to evaluate

    Returns:
        Formatted prompt string for LLM evaluation
    """
    # Serialize interaction steps to JSON
    trace_data = json.dumps(
        [
            {
                "step_id": step.step_id,
                "trace_id": step.trace_id,
                "call_type": step.call_type.value,
                "start_time": step.start_time.isoformat(),
                "end_time": step.end_time.isoformat(),
                "latency": step.latency,
                "error": step.error,
                "parent_step_id": step.parent_step_id,
            }
            for step in steps
        ],
        indent=2,
    )

    # Build prompt with evaluation criteria and JSON schema
    prompt = f"""You are evaluating the coordination quality of multi-agent interactions.
Based on the trace data below, assess how well the agents coordinated.

# Trace Data
{trace_data}

# Evaluation Criteria
Assess the coordination quality based on:
- Communication patterns and efficiency
- Task delegation and distribution
- Response times and latency
- Error handling and recovery
- Overall coordination effectiveness

# Output Format
Respond with a JSON object following this schema:
{{
  "overall_score": <float between 0 and 1>,
  "reasoning": "<explanation of the assessment>",
  "coordination_quality": "<low|medium|high>",
  "strengths": ["<strength 1>", "<strength 2>", ...],
  "weaknesses": ["<weakness 1>", "<weakness 2>", ...]
}}

The overall_score must be a number between 0 and 1, where:
- 0.0-0.3: Poor coordination
- 0.3-0.7: Moderate coordination
- 0.7-1.0: Excellent coordination

Provide your assessment as JSON only, with no additional text."""

    return prompt


def get_llm_client() -> AsyncOpenAI:
    """Get OpenAI-compatible client with configuration from environment.

    Returns:
        Configured AsyncOpenAI client

    Raises:
        ValueError: If API key is required but not provided
    """
    config = get_llm_config()
    return AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)


def rule_based_evaluate(steps: list[InteractionStep]) -> LLMJudgment:
    """Fallback rule-based evaluation when LLM API is unavailable.

    Provides basic assessment based on:
    - Error presence
    - Latency metrics
    - Number of steps

    Args:
        steps: List of InteractionStep traces to evaluate

    Returns:
        LLMJudgment with rule-based assessment
    """
    if not steps:
        return LLMJudgment(
            overall_score=0.0,
            reasoning="No interaction steps to evaluate",
            coordination_quality="low",
            strengths=[],
            weaknesses=["No coordination data available"],
        )

    # Calculate metrics
    has_errors = any(step.error is not None for step in steps)
    avg_latency = sum(step.latency or 0 for step in steps) / len(steps)
    num_steps = len(steps)

    # Compute score based on rules
    score = 0.8  # Base score

    # Penalize for errors
    if has_errors:
        score -= 0.3

    # Penalize for high latency (>2 seconds avg)
    if avg_latency > 2000:
        score -= 0.2
    elif avg_latency > 1000:
        score -= 0.1

    # Bonus for multiple steps (coordination happening)
    if num_steps > 1:
        score += 0.1

    # Clamp score to valid range
    score = max(0.0, min(1.0, score))

    # Determine quality level
    if score >= 0.7:
        quality = "high"
    elif score >= 0.3:
        quality = "medium"
    else:
        quality = "low"

    # Build strengths and weaknesses
    strengths: list[str] = []
    weaknesses: list[str] = []

    if not has_errors:
        strengths.append("No errors in coordination")
    else:
        weaknesses.append("Errors detected in coordination")

    if avg_latency < 1000:
        strengths.append("Low latency")
    elif avg_latency > 2000:
        weaknesses.append("High latency")

    if num_steps > 1:
        strengths.append("Multiple interaction steps")

    return LLMJudgment(
        overall_score=score,
        reasoning=f"Rule-based evaluation: {num_steps} steps, avg latency {avg_latency:.0f}ms, "
        f"{'with errors' if has_errors else 'no errors'}",
        coordination_quality=quality,
        strengths=strengths,
        weaknesses=weaknesses,
    )


def _build_context_section(
    graph_metrics: dict[str, Any] | None,
    latency_metrics: dict[str, Any] | None,
    text_metrics: dict[str, Any] | None,
    task_outcome: str | None,
) -> str:
    """Build additional context section for LLM prompt."""
    if not any([graph_metrics, latency_metrics, text_metrics, task_outcome]):
        return ""

    parts = ["\n\n# Additional Context\n"]
    if graph_metrics:
        parts.append(f"\nGraph Metrics: {json.dumps(graph_metrics, indent=2)}")
    if latency_metrics:
        parts.append(f"\nLatency Metrics: {json.dumps(latency_metrics, indent=2)}")
    if text_metrics:
        parts.append(f"\nText Metrics: {json.dumps(text_metrics, indent=2)}")
    if task_outcome:
        parts.append(f"\nTask Outcome: {task_outcome}")
    return "".join(parts)


async def _call_llm(prompt: str) -> LLMJudgment | None:
    """Call LLM API and parse response. Returns None on failure."""
    client = get_llm_client()
    config = get_llm_config()

    response = await client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = response.choices[0].message.content
    if not content:
        return None

    result_data = json.loads(content)
    return LLMJudgment.model_validate(result_data)


async def llm_evaluate(
    steps: list[InteractionStep],
    graph_metrics: dict[str, Any] | None = None,
    latency_metrics: dict[str, Any] | None = None,
    text_metrics: dict[str, Any] | None = None,
    task_outcome: str | None = None,
) -> LLMJudgment:
    """Evaluate coordination quality using LLM API with fallback to rule-based."""
    try:
        prompt = build_prompt(steps)
        prompt += _build_context_section(graph_metrics, latency_metrics, text_metrics, task_outcome)

        result = await _call_llm(prompt)
        if result:
            return result

        logger.warning("LLM returned empty response, falling back to rule-based evaluation")

    except Exception as e:
        logger.warning(
            "LLM evaluation failed (%s), falling back to rule-based evaluation", type(e).__name__
        )

    return rule_based_evaluate(steps)
