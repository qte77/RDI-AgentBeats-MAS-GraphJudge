"""Pydantic models for Purple Agent.

All Purple Agent data models centralized here for consistency and reusability.
JSON-RPC protocol models imported from common module (single source of truth).
"""

from __future__ import annotations

# Re-export JSONRPC models from common for Purple's use
from common.models import JSONRPCRequest, JSONRPCResponse

__all__ = ["JSONRPCRequest", "JSONRPCResponse"]
