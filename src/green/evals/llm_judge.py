"""LLM-based evaluation configuration and implementation."""

from __future__ import annotations

import json
import os

from pydantic import BaseModel, Field

from green.models import InteractionStep


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
