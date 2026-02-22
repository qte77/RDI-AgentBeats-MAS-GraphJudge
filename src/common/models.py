"""Shared models for AgentBeats Green and Purple agents.

This module provides common data models used by both Green and Purple agents:
- A2A Protocol: AgentCard
- A2A Traceability Extension: InteractionStep, CallType
- JSON-RPC 2.0 Protocol: JSONRPCRequest, JSONRPCResponse

Single source of truth for shared types to eliminate code duplication.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ruff: noqa: N815 - A2A protocol requires camelCase field names

# =============================================================================
# A2A Protocol Models
# =============================================================================


class AgentSkill(BaseModel):
    """Agent skill definition per A2A protocol."""

    id: str
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)


class AgentCapabilities(BaseModel):
    """Agent capabilities per A2A protocol."""

    protocols: list[str]
    extensions: list[dict[str, str]] = Field(default_factory=list)


class AgentEndpoints(BaseModel):
    """Agent endpoints per A2A protocol."""

    a2a: str
    health: str


class AgentCard(BaseModel):
    """AgentCard model per A2A protocol specification.

    Single source of truth for A2A AgentCard structure validation.
    Used by both Green and Purple agents to ensure SDK compatibility.

    Required by A2A SDK ClientFactory.connect() for agent discovery.

    Note: Field names use camelCase per A2A spec (not Python convention).
    """

    model_config = ConfigDict(
        # Allow camelCase field names for external API compliance
        # Suppresses ruff N815 warnings for spec-required naming
        populate_by_name=True,
    )

    agentId: str  # noqa: N815 - A2A spec requires camelCase
    name: str
    description: str
    version: str
    url: str
    defaultInputModes: list[str]  # noqa: N815 - A2A spec requires camelCase
    defaultOutputModes: list[str]  # noqa: N815 - A2A spec requires camelCase
    skills: list[AgentSkill]
    capabilities: AgentCapabilities
    endpoints: AgentEndpoints


# =============================================================================
# A2A Traceability Extension Models
# =============================================================================


class CallType(StrEnum):
    """Call type enumeration for A2A Traceability Extension.

    Classification per A2A spec:
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
    agent_url: str | None = None


# =============================================================================
# Trace Collection Configuration
# =============================================================================


class TraceCollectionConfig(BaseModel):
    """Configurable timeout and idle detection settings for adaptive trace collection."""

    max_timeout_seconds: float = 30
    idle_threshold_seconds: float = 5
    use_completion_signals: bool = True


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
