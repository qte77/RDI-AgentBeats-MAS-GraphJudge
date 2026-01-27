"""LLM-based evaluation configuration and implementation."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from green.models import InteractionStep

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM client.

    Reads environment variables:
    - AGENTBEATS_LLM_API_KEY: API key for authentication
    - AGENTBEATS_LLM_BASE_URL: Base URL for LLM endpoint (default: https://api.openai.com/v1)
    - AGENTBEATS_LLM_MODEL: Model name (default: gpt-4o-mini)

    Supports any OpenAI-compatible endpoint.
    """

    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"


class LLMJudgment(BaseModel):
    """Structured output from LLM-based coordination assessment.

    Fields requested in prompt:
    - overall_score: Numeric score between 0 and 1
    - reasoning: Explanation of the assessment
    - coordination_quality: Qualitative assessment (low/medium/high)
    - strengths: List of observed coordination strengths
    - weaknesses: List of observed coordination weaknesses

    Example output (high coordination):
    {
        "overall_score": 0.85,
        "reasoning": "Agents demonstrated efficient task delegation with clear communication...",
        "coordination_quality": "high",
        "strengths": ["Fast response times", "Clear delegation", "No errors"],
        "weaknesses": ["Could optimize parallel execution"]
    }

    Example output (moderate coordination):
    {
        "overall_score": 0.55,
        "reasoning": "Coordination was adequate but showed some inefficiencies...",
        "coordination_quality": "medium",
        "strengths": ["Task completion achieved", "Basic communication established"],
        "weaknesses": ["High latency", "Sequential execution", "Bottleneck at coordinator"]
    }

    Example output (poor coordination):
    {
        "overall_score": 0.20,
        "reasoning": "Significant coordination issues with multiple failures...",
        "coordination_quality": "low",
        "strengths": ["Agents attempted communication"],
        "weaknesses": ["Multiple errors", "Very high latency", "Poor task distribution", "Failed to complete"]
    }
    """

    overall_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    coordination_quality: str
    strengths: list[str]
    weaknesses: list[str]


def get_llm_config() -> LLMConfig:
    """Get LLM configuration from environment variables.

    Returns:
        LLMConfig with values from environment or defaults
    """
    return LLMConfig(
        api_key=os.environ.get("AGENTBEATS_LLM_API_KEY"),
        base_url=os.environ.get("AGENTBEATS_LLM_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("AGENTBEATS_LLM_MODEL", "gpt-4o-mini"),
    )


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
    prompt = f"""You are evaluating the coordination quality of multi-agent interactions based on trace data.

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


async def llm_evaluate(
    steps: list[InteractionStep],
    graph_metrics: dict[str, Any] | None = None,
    latency_metrics: dict[str, Any] | None = None,
    text_metrics: dict[str, Any] | None = None,
    task_outcome: str | None = None,
) -> LLMJudgment:
    """Evaluate coordination quality using LLM API with fallback to rule-based.

    Integrates LLM API calls with graceful fallback to rule-based evaluation
    if API is unavailable. Handles API errors and timeouts.

    Args:
        steps: List of InteractionStep traces to evaluate
        graph_metrics: Optional graph evaluator output
        latency_metrics: Optional latency evaluator output
        text_metrics: Optional text evaluator output
        task_outcome: Optional task outcome assessment (success/failure)

    Returns:
        LLMJudgment with coordination assessment
    """
    try:
        # Get LLM client
        client = get_llm_client()
        config = get_llm_config()

        # Build prompt with trace data
        prompt = build_prompt(steps)

        # Enhance prompt with additional context if provided
        if graph_metrics or latency_metrics or text_metrics or task_outcome:
            prompt += "\n\n# Additional Context\n"

            if graph_metrics:
                prompt += f"\nGraph Metrics: {json.dumps(graph_metrics, indent=2)}"

            if latency_metrics:
                prompt += f"\nLatency Metrics: {json.dumps(latency_metrics, indent=2)}"

            if text_metrics:
                prompt += f"\nText Metrics: {json.dumps(text_metrics, indent=2)}"

            if task_outcome:
                prompt += f"\nTask Outcome: {task_outcome}"

        # Call LLM API with temperature=0 for consistency
        response = await client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        # Extract response content
        content = response.choices[0].message.content

        # Parse JSON response
        if content:
            result_data = json.loads(content)
            return LLMJudgment(**result_data)

        # Fallback if no content
        logger.warning("LLM returned empty response, falling back to rule-based evaluation")
        return rule_based_evaluate(steps)

    except (ConnectionError, TimeoutError) as e:
        # Log warning (not error) for API unavailability
        logger.warning(
            "LLM API unavailable (%s), falling back to rule-based evaluation", type(e).__name__
        )
        return rule_based_evaluate(steps)

    except (json.JSONDecodeError, ValidationError) as e:
        # Handle invalid JSON or validation errors
        logger.warning(
            "LLM response parsing failed (%s), falling back to rule-based evaluation",
            type(e).__name__,
        )
        return rule_based_evaluate(steps)

    except Exception as e:
        # Catch-all for any other errors
        logger.warning(
            "LLM evaluation failed (%s), falling back to rule-based evaluation", type(e).__name__
        )
        return rule_based_evaluate(steps)
