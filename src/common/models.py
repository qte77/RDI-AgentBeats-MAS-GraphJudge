"""Shared models for AgentBeats Green and Purple agents.

This module provides common data models used by both Green and Purple agents:
- A2A Traceability Extension: InteractionStep, CallType
- JSON-RPC 2.0 Protocol: JSONRPCRequest, JSONRPCResponse

Single source of truth for shared types to eliminate code duplication.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


# =============================================================================
# A2A Traceability Extension Models
# =============================================================================


class CallType(str, Enum):
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
