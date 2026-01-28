"""Tests for Purple Agent Pydantic models.

Tests for models centralized in purple.models module.
"""

from __future__ import annotations

from purple.models import JSONRPCRequest, JSONRPCResponse


class TestJSONRPCRequest:
    """Test JSONRPCRequest model."""

    def test_model_validate_from_dict(self):
        """JSONRPCRequest validates from dict using model_validate()."""
        data = {
            "jsonrpc": "2.0",
            "method": "tasks.send",
            "params": {"task": {"description": "Test"}},
            "id": 1,
        }
        request = JSONRPCRequest.model_validate(data)
        assert request.jsonrpc == "2.0"
        assert request.method == "tasks.send"
        assert request.id == 1

    def test_default_jsonrpc_version(self):
        """JSONRPCRequest defaults to jsonrpc 2.0."""
        request = JSONRPCRequest(method="test", params={}, id=1)
        assert request.jsonrpc == "2.0"

    def test_params_field(self):
        """JSONRPCRequest stores params dict."""
        params = {"task": {"description": "Test"}, "context": {"key": "value"}}
        request = JSONRPCRequest(method="tasks.send", params=params, id=1)
        assert request.params == params

    def test_id_can_be_string(self):
        """JSONRPCRequest id can be a string."""
        request = JSONRPCRequest(method="test", params={}, id="request-123")
        assert request.id == "request-123"

    def test_id_can_be_int(self):
        """JSONRPCRequest id can be an integer."""
        request = JSONRPCRequest(method="test", params={}, id=42)
        assert request.id == 42


class TestJSONRPCResponse:
    """Test JSONRPCResponse model."""

    def test_model_validate_from_dict(self):
        """JSONRPCResponse validates from dict using model_validate()."""
        data = {
            "jsonrpc": "2.0",
            "result": {"status": "completed"},
            "id": 1,
        }
        response = JSONRPCResponse.model_validate(data)
        assert response.jsonrpc == "2.0"
        assert response.result == {"status": "completed"}
        assert response.error is None
        assert response.id == 1

    def test_response_with_error(self):
        """JSONRPCResponse validates error responses."""
        data = {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": 2,
        }
        response = JSONRPCResponse.model_validate(data)
        assert response.error is not None
        assert response.error["code"] == -32601
        assert response.result is None

    def test_default_jsonrpc_version(self):
        """JSONRPCResponse defaults to jsonrpc 2.0."""
        response = JSONRPCResponse(id=1)
        assert response.jsonrpc == "2.0"

    def test_result_is_optional(self):
        """JSONRPCResponse result field is optional."""
        response = JSONRPCResponse(id=1)
        assert response.result is None

    def test_error_is_optional(self):
        """JSONRPCResponse error field is optional."""
        response = JSONRPCResponse(id=1)
        assert response.error is None

    def test_id_can_be_string(self):
        """JSONRPCResponse id can be a string."""
        response = JSONRPCResponse(id="response-456")
        assert response.id == "response-456"


class TestModelsModuleLocation:
    """Test that models are centralized in purple.models module."""

    def test_models_located_in_purple_models(self):
        """Pydantic models are centralized in purple.models module."""
        from purple import models

        assert hasattr(models, "JSONRPCRequest")
        assert hasattr(models, "JSONRPCResponse")
