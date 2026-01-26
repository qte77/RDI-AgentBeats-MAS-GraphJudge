"""LLM judge evaluator for qualitative assessment of agent coordination."""

from __future__ import annotations

import json
import logging
import os

from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from agentbeats.messenger import TraceData


class LLMJudgment(BaseModel):
    """Expected structure of LLM judge assessment."""

    overall_score: float  # 0-1 score
    reasoning: str  # Explanation of assessment
    coordination_quality: str | None = None  # Quality description
    strengths: list[str] | None = None  # Identified strengths
    weaknesses: list[str] | None = None  # Identified weaknesses


class LLMJudge:
    """Evaluates agent coordination using LLM-as-judge approach."""

    def __init__(self) -> None:
        """Initialize LLM judge evaluator."""
        # Read configuration from environment variables
        self._api_key = os.environ.get("AGENTBEATS_LLM_API_KEY")
        self._base_url = os.environ.get("AGENTBEATS_LLM_BASE_URL", "https://api.openai.com/v1")
        self._model = os.environ.get("AGENTBEATS_LLM_MODEL", "gpt-4o-mini")

        # Lazy initialization of OpenAI client
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI | None:
        """Get or create OpenAI client lazily.

        Returns:
            AsyncOpenAI client if API key is configured, None otherwise
        """
        if self._api_key and self._client is None:
            self._client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
        return self._client

    def _build_prompt(self, traces: list[TraceData]) -> str:
        """Build evaluation prompt from trace data.

        Args:
            traces: List of TraceData objects to serialize into prompt

        Returns:
            Prompt string for LLM evaluation
        """
        # Serialize trace data into readable format
        trace_lines: list[str] = []
        for i, trace in enumerate(traces, 1):
            trace_lines.append(f"Interaction {i}:")
            trace_lines.append(f"  Timestamp: {trace.timestamp}")
            trace_lines.append(f"  Agent URL: {trace.agent_url}")
            trace_lines.append(f"  Message: {trace.message}")
            trace_lines.append(f"  Response: {trace.response}")
            trace_lines.append(f"  Status Code: {trace.status_code}")
            if trace.error:
                trace_lines.append(f"  Error: {trace.error}")
            if trace.task_id:
                trace_lines.append(f"  Task ID: {trace.task_id}")
            trace_lines.append("")

        trace_data = "\n".join(trace_lines)

        # Build prompt with clear evaluation criteria
        prompt = f"""You are evaluating agent coordination quality based on interaction traces.

Agent Interaction Traces:
{trace_data}

Please evaluate the coordination quality and provide your assessment in JSON format with the following fields:

{{
  "overall_score": <float between 0 and 1>,
  "reasoning": "<detailed explanation of your assessment>",
  "coordination_quality": "<qualitative description: Excellent/Good/Fair/Poor>",
  "strengths": ["<strength 1>", "<strength 2>", ...],
  "weaknesses": ["<weakness 1>", "<weakness 2>", ...]
}}

Evaluation Criteria:
- Communication clarity: Are messages and responses clear and well-formed?
- Coordination effectiveness: Do agents coordinate smoothly or encounter issues?
- Error handling: How well do agents handle errors and failures?
- Response quality: Are responses appropriate and complete?
- Overall performance: Success rate, consistency, and reliability

Provide your assessment as valid JSON matching the schema above."""

        return prompt

    def _fallback_evaluate(self, traces: list[TraceData]) -> LLMJudgment:
        """Rule-based fallback evaluation when LLM API is not available.

        Args:
            traces: List of TraceData objects representing agent interactions

        Returns:
            LLMJudgment object with rule-based assessment
        """
        # Analyze traces for coordination quality indicators
        total_interactions = len(traces)
        successful_interactions = sum(1 for trace in traces if trace.status_code == 200 and not trace.error)
        error_count = sum(1 for trace in traces if trace.error)

        # Calculate success rate
        success_rate = successful_interactions / total_interactions if total_interactions > 0 else 0.0

        # Determine overall score and quality assessment
        overall_score = success_rate

        if success_rate >= 0.9:
            coordination_quality = "Excellent"
            reasoning = (
                f"Agent demonstrated excellent coordination with {success_rate:.0%} "
                f"success rate across {total_interactions} interactions"
            )
            strengths = ["High success rate", "Consistent performance", "Reliable communication"]
            weaknesses = [] if success_rate == 1.0 else ["Minor occasional failures"]
        elif success_rate >= 0.7:
            coordination_quality = "Good"
            reasoning = (
                f"Agent demonstrated good coordination with {success_rate:.0%} "
                f"success rate across {total_interactions} interactions"
            )
            strengths = ["Mostly reliable", "Acceptable performance"]
            weaknesses = ["Some failed interactions", "Room for improvement"]
        elif success_rate >= 0.5:
            coordination_quality = "Fair"
            reasoning = (
                f"Agent demonstrated fair coordination with {success_rate:.0%} "
                f"success rate across {total_interactions} interactions"
            )
            strengths = ["Basic functionality working"]
            weaknesses = ["High failure rate", "Inconsistent reliability", "Needs improvement"]
        else:
            coordination_quality = "Poor"
            reasoning = (
                f"Agent demonstrated poor coordination with {success_rate:.0%} "
                f"success rate across {total_interactions} interactions"
            )
            strengths = []
            weaknesses = [
                "Very high failure rate",
                "Unreliable communication",
                "Significant coordination issues",
            ]

        # Add error analysis if errors present
        if error_count > 0:
            reasoning += f". {error_count} errors encountered"

        return LLMJudgment(
            overall_score=overall_score,
            reasoning=reasoning,
            coordination_quality=coordination_quality,
            strengths=strengths if strengths else None,
            weaknesses=weaknesses if weaknesses else None,
        )

    async def evaluate(self, traces: list[TraceData]) -> LLMJudgment:
        """Evaluate agent coordination quality from traces using LLM judgment.

        Args:
            traces: List of TraceData objects representing agent interactions

        Returns:
            LLMJudgment object with qualitative assessment
        """
        # Handle empty traces
        if not traces:
            return LLMJudgment(
                overall_score=0.0,
                reasoning="No traces available for evaluation",
                coordination_quality="None",
                strengths=[],
                weaknesses=["No agent interactions captured"],
            )

        # Try LLM API if API key is configured
        client = self._get_client()
        if client:
            try:
                # Build prompt for LLM evaluation
                prompt = self._build_prompt(traces)

                # Call LLM API
                response = await client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": "You are an expert evaluator of agent coordination quality."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )

                # Extract and parse JSON response
                content = response.choices[0].message.content
                if content:
                    # Try to parse JSON response
                    try:
                        # Remove markdown code blocks if present
                        content = content.strip()
                        if content.startswith("```"):
                            content = content.split("```")[1]
                            if content.startswith("json"):
                                content = content[4:]
                        content = content.strip()

                        judgment_data = json.loads(content)
                        return LLMJudgment(**judgment_data)
                    except (json.JSONDecodeError, ValidationError) as e:
                        # Invalid JSON or validation error - fall back
                        logging.warning(
                            f"Failed to parse LLM response as valid JSON/LLMJudgment: {e}. Using fallback evaluation."
                        )

            except Exception as e:
                # API call failed - fall back to rule-based logic
                logging.warning(f"LLM API call failed: {e}. Using fallback rule-based evaluation.")

        else:
            # No API key configured - use fallback
            logging.warning("AGENTBEATS_LLM_API_KEY not set. Using fallback rule-based evaluation.")

        # Use fallback rule-based evaluation
        return self._fallback_evaluate(traces)
