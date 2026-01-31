"""Common shared module for AgentBeats Green and Purple agents.

Exports all shared types for use by both agents.
"""

from common.models import CallType, InteractionStep, JSONRPCRequest, JSONRPCResponse

__all__ = ["CallType", "InteractionStep", "JSONRPCRequest", "JSONRPCResponse"]
