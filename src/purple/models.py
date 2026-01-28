"""Pydantic models for Purple Agent.

All Purple Agent data models centralized here for consistency and reusability.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request model."""

    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any]
    id: str | int


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response model."""

    jsonrpc: str = "2.0"
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    id: str | int
