"""Tests for common shared models module.

This test suite validates STORY-018:
- Common module exports all shared types
- Models conform to A2A Traceability Extension Step specification
- CallType, InteractionStep, JSONRPCRequest, JSONRPCResponse available
- Backward compatibility via Green agent re-exports
"""

from __future__ import annotations

from datetime import UTC, datetime


def test_common_module_exports_all_types():
    """Verify src/common/__init__.py exports all shared types."""
    from common import CallType, InteractionStep, JSONRPCRequest, JSONRPCResponse

    # Verify all types are accessible
    assert CallType is not None
    assert InteractionStep is not None
    assert JSONRPCRequest is not None
    assert JSONRPCResponse is not None


def test_call_type_enum_values():
    """Verify CallType enum contains AGENT, TOOL, HOST per A2A spec."""
    from common import CallType

    assert hasattr(CallType, "AGENT")
    assert hasattr(CallType, "TOOL")
    assert hasattr(CallType, "HOST")

    # Verify enum values
    assert CallType.AGENT.value == "AGENT"
    assert CallType.TOOL.value == "TOOL"
    assert CallType.HOST.value == "HOST"


def test_interaction_step_model_structure():
    """Verify InteractionStep conforms to A2A Traceability Extension Step spec."""
    from common import CallType, InteractionStep

    now = datetime.now(UTC)
    later = datetime.now(UTC)

    step = InteractionStep(
        step_id="step-123",
        trace_id="trace-456",
        call_type=CallType.AGENT,
        start_time=now,
        end_time=later,
        latency=100,
        error=None,
        parent_step_id=None,
    )

    # Verify required fields
    assert step.step_id == "step-123"
    assert step.trace_id == "trace-456"
    assert step.call_type == CallType.AGENT
    assert step.start_time == now
    assert step.end_time == later

    # Verify optional fields
    assert step.latency == 100
    assert step.error is None
    assert step.parent_step_id is None


def test_interaction_step_with_error():
    """Verify InteractionStep handles error field."""
    from common import CallType, InteractionStep

    now = datetime.now(UTC)
    later = datetime.now(UTC)

    step = InteractionStep(
        step_id="step-error",
        trace_id="trace-error",
        call_type=CallType.TOOL,
        start_time=now,
        end_time=later,
        error="Connection timeout",
    )

    assert step.error == "Connection timeout"


def test_interaction_step_with_parent():
    """Verify InteractionStep supports hierarchical nesting via parent_step_id."""
    from common import CallType, InteractionStep

    now = datetime.now(UTC)
    later = datetime.now(UTC)

    child_step = InteractionStep(
        step_id="step-child",
        trace_id="trace-nested",
        call_type=CallType.HOST,
        start_time=now,
        end_time=later,
        parent_step_id="step-parent",
    )

    assert child_step.parent_step_id == "step-parent"


def test_jsonrpc_request_model():
    """Verify JSONRPCRequest model structure."""
    from common import JSONRPCRequest

    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="message/send",
        params={"message": "test"},
        id="req-123",
    )

    assert request.jsonrpc == "2.0"
    assert request.method == "message/send"
    assert request.params == {"message": "test"}
    assert request.id == "req-123"


def test_jsonrpc_response_model_success():
    """Verify JSONRPCResponse model for successful response."""
    from common import JSONRPCResponse

    response = JSONRPCResponse(
        jsonrpc="2.0",
        result={"status": "ok"},
        id="req-123",
    )

    assert response.jsonrpc == "2.0"
    assert response.result == {"status": "ok"}
    assert response.error is None
    assert response.id == "req-123"


def test_jsonrpc_response_model_error():
    """Verify JSONRPCResponse model for error response."""
    from common import JSONRPCResponse

    response = JSONRPCResponse(
        jsonrpc="2.0",
        error={"code": -32600, "message": "Invalid Request"},
        id="req-123",
    )

    assert response.jsonrpc == "2.0"
    assert response.result is None
    assert response.error == {"code": -32600, "message": "Invalid Request"}
    assert response.id == "req-123"


def test_green_agent_backward_compatible_imports():
    """Verify Green agent can still import from green.models (backward compatible)."""
    from green.models import CallType, InteractionStep, JSONRPCRequest, JSONRPCResponse

    # Verify all types are accessible from green.models
    assert CallType is not None
    assert InteractionStep is not None
    assert JSONRPCRequest is not None
    assert JSONRPCResponse is not None


def test_green_imports_reference_same_types_as_common():
    """Verify green.models re-exports are the same types as common."""
    from common import CallType as CommonCallType
    from common import InteractionStep as CommonInteractionStep
    from common import JSONRPCRequest as CommonJSONRPCRequest
    from common import JSONRPCResponse as CommonJSONRPCResponse
    from green.models import CallType as GreenCallType
    from green.models import InteractionStep as GreenInteractionStep
    from green.models import JSONRPCRequest as GreenJSONRPCRequest
    from green.models import JSONRPCResponse as GreenJSONRPCResponse

    # Verify they are the exact same types (not just compatible)
    assert CommonCallType is GreenCallType
    assert CommonInteractionStep is GreenInteractionStep
    assert CommonJSONRPCRequest is GreenJSONRPCRequest
    assert CommonJSONRPCResponse is GreenJSONRPCResponse
