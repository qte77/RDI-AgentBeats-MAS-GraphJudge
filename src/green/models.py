"""Green Agent Pydantic models.

Consolidates all Green Agent models for single source of truth:
- A2A Traceability Extension: InteractionStep, CallType
- Graph Evaluation: GraphMetrics
- LLM Evaluation: LLMJudgment
- AgentBeats Output: GreenAgentOutput, AgentBeatsOutputModel
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from green.settings import GreenSettings


# =============================================================================
# A2A Traceability Extension Models
# =============================================================================


class CallType(str, Enum):
    """Call type enumeration for A2A Traceability Extension.

    Classification per STORY-002:
    - AGENT: Agent-to-agent communication (messenger)
    - TOOL: Tool invocations (LLM)
    - HOST: Host system calls (graph analysis)
    """

    AGENT = "AGENT"
    TOOL = "TOOL"
    HOST = "HOST"


class InteractionStep(BaseModel):
    """Interaction step conforming to A2A Traceability Extension Step specification.

    Tracks a single operation in the agent interaction trace with timing,
    classification, and optional error information. Supports hierarchical
    nested tracing via parent_step_id.
    """

    step_id: str
    trace_id: str
    call_type: CallType
    start_time: datetime
    end_time: datetime
    latency: int | None = None
    error: str | None = None
    parent_step_id: str | None = None


def get_agent_extensions() -> list[dict[str, str]]:
    """Get list of A2A protocol extensions supported by this agent."""
    return [
        {"uri": "github.com/a2aproject/a2a-samples/extensions/traceability/v1"},
        {"uri": "github.com/a2aproject/a2a-samples/extensions/timestamp/v1"},
    ]


# =============================================================================
# JSON-RPC 2.0 Protocol Models
# =============================================================================


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request model for A2A protocol."""

    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any]
    id: str | int


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response model for A2A protocol."""

    jsonrpc: str = "2.0"
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    id: str | int


# =============================================================================
# Graph Evaluation Models
# =============================================================================


class GraphMetrics(BaseModel):
    """Graph metrics for coordination quality assessment.

    Per PRD STORY-014: GraphMetrics with numerical scores for
    density, centrality, bottlenecks, etc.
    """

    model_config = {"extra": "allow"}

    degree_centrality: dict[str, float] = Field(default_factory=dict)
    betweenness_centrality: dict[str, float] = Field(default_factory=dict)
    closeness_centrality: dict[str, float] = Field(default_factory=dict)
    eigenvector_centrality: dict[str, float] = Field(default_factory=dict)
    pagerank: dict[str, float] = Field(default_factory=dict)
    graph_density: float = Field(0.0, ge=0.0, le=1.0)
    clustering_coefficient: float = Field(0.0, ge=0.0, le=1.0)
    connected_components: int = Field(0, ge=0)
    average_path_length: float = Field(0.0, ge=0.0)
    diameter: int = Field(0, ge=0)
    bottlenecks: list[str] = Field(default_factory=list)
    has_bottleneck: bool = Field(False)
    isolated_agents: list[str] = Field(default_factory=list)
    over_centralized: bool = Field(False)
    coordination_quality: str = Field("low")


# =============================================================================
# LLM Evaluation Models
# =============================================================================


class LLMJudgment(BaseModel):
    """Structured output from LLM-based coordination assessment.

    Per PRD STORY-008: LLM Judge output with score, reasoning, and quality.
    """

    overall_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    coordination_quality: str
    strengths: list[str]
    weaknesses: list[str]


# =============================================================================
# Latency Metrics Models
# =============================================================================


class LatencyMetrics(BaseModel):
    """Latency metrics for performance analysis.

    WARNING: Latency values are only comparable within the same system/run.
    Do not compare latency metrics across different environments, systems,
    or time periods.

    Per PRD STORY-010: Percentiles and performance bottleneck identification.
    """

    avg: float
    p50: float
    p95: float
    p99: float
    slowest_agent: str | None
    warning: str = "Latency values only comparable within same system/run"


# =============================================================================
# AgentBeats Output Models
# =============================================================================


class GreenAgentOutput(BaseModel):
    """Green Agent coordination evaluation output.

    Per PRD STORY-008, STORY-014: LLM Judge + Graph + Latency metrics.
    """

    model_config = {"extra": "allow"}

    overall_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(...)
    coordination_quality: Literal["low", "medium", "high"] = Field(...)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    graph_metrics: dict[str, Any] | None = Field(None)
    latency_metrics: dict[str, Any] | None = Field(None)


class ParticipantsModel(BaseModel):
    """Agent participant in the assessment."""

    agent: str = Field(..., description="Agent identifier")


class ResultModel(BaseModel):
    """Single evaluation result for AgentBeats leaderboard."""

    model_config = {"extra": "allow"}

    pass_rate: float = Field(..., ge=0.0)
    time_used: float = Field(..., ge=0.0)
    max_score: float = Field(..., gt=0.0)
    domain: str | None = Field(None)
    score: float | None = Field(None)
    task_rewards: dict[str, float] | None = Field(None)
    detail: GreenAgentOutput | dict[str, Any] | None = Field(None)


class AgentBeatsOutputModel(BaseModel):
    """Top-level AgentBeats output format for leaderboard compatibility."""

    participants: ParticipantsModel = Field(...)
    results: list[ResultModel] = Field(..., min_length=1)

    def to_json(self, **kwargs: Any) -> str:
        """Export as JSON string."""
        return self.model_dump_json(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary."""
        return self.model_dump()

    @classmethod
    def from_green_output(
        cls,
        green_output: GreenAgentOutput | dict[str, Any],
        agent_id: str,
        time_used: float = 0.0,
        domain: str = "coordination",
        max_score: float = 100.0,
    ) -> AgentBeatsOutputModel:
        """Create AgentBeats output from Green Agent evaluation."""
        if isinstance(green_output, dict):
            output = GreenAgentOutput.model_validate(green_output)
        else:
            output = green_output

        pass_rate = output.overall_score * 100.0
        score = output.overall_score * max_score

        graph_density = 0.0
        if output.graph_metrics:
            graph_density = output.graph_metrics.get("graph_density", 0.0)

        quality_map = {"low": 0.33, "medium": 0.66, "high": 1.0}
        quality_score = quality_map.get(output.coordination_quality, 0.0)

        task_rewards = {
            "overall_score": output.overall_score,
            "graph_density": graph_density,
            "coordination_quality": quality_score,
        }

        return cls(
            participants=ParticipantsModel(agent=agent_id),
            results=[
                ResultModel(
                    pass_rate=pass_rate,
                    time_used=time_used,
                    max_score=max_score,
                    score=score,
                    domain=domain,
                    task_rewards=task_rewards,
                    detail=output,
                )
            ],
        )

    @classmethod
    def from_evaluation_results(
        cls,
        evaluation_results: dict[str, Any],
        agent_id: str | None = None,
        domain: str = "coordination",
        max_score: float = 100.0,
        settings: GreenSettings | None = None,
    ) -> AgentBeatsOutputModel:
        """Create AgentBeats output from executor evaluation results."""
        if agent_id is None:
            if settings is None:
                from green.settings import GreenSettings

                settings = GreenSettings()
            agent_id = settings.agent_uuid

        graph_results: dict[str, Any] = evaluation_results.get("tier1_graph") or {}
        llm_results: dict[str, Any] = evaluation_results.get("tier2_llm") or {}
        latency_results: dict[str, Any] = evaluation_results.get("tier2_latency") or {}

        overall_score: float = llm_results.get("overall_score", 0.0)
        reasoning: str = llm_results.get("reasoning", "No evaluation performed")
        coordination_quality: str = llm_results.get("coordination_quality", "low")
        strengths: list[str] = llm_results.get("strengths", [])
        weaknesses: list[str] = llm_results.get("weaknesses", [])

        pass_rate: float = overall_score * 100.0
        score: float = overall_score * max_score
        time_used: float = latency_results.get("p99_latency", 0.0)

        graph_density: float = graph_results.get("graph_density", 0.0)
        quality_map: dict[str, float] = {"low": 0.33, "medium": 0.66, "high": 1.0}
        quality_score: float = quality_map.get(coordination_quality, 0.0)

        task_rewards: dict[str, float] = {
            "overall_score": overall_score,
            "graph_density": graph_density,
            "coordination_quality": quality_score,
        }

        detail: dict[str, Any] = {
            "overall_score": overall_score,
            "reasoning": reasoning,
            "coordination_quality": coordination_quality,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "graph_metrics": graph_results if graph_results else None,
            "latency_metrics": latency_results if latency_results else None,
        }

        return cls(
            participants=ParticipantsModel(agent=agent_id),
            results=[
                ResultModel(
                    pass_rate=pass_rate,
                    time_used=time_used,
                    max_score=max_score,
                    score=score,
                    domain=domain,
                    task_rewards=task_rewards,
                    detail=detail,
                )
            ],
        )
