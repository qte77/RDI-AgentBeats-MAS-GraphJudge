"""Models for A2A Traceability Extension integration.

Implements InteractionStep conforming to A2A Traceability Extension Step specification.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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

    Fields conform to A2A Traceability Extension spec:
    - step_id: Unique step identifier
    - trace_id: Belonging trace ID
    - call_type: Call type (AGENT/TOOL/HOST)
    - start_time: Start time
    - end_time: End time
    - latency: Latency in milliseconds (optional)
    - error: Error information (optional)
    - parent_step_id: Parent step ID for nested tracing (optional)
    """

    step_id: str
    trace_id: str
    call_type: CallType
    start_time: datetime
    end_time: datetime
    latency: int | None = None
    error: str | None = None
    parent_step_id: str | None = None
