"""Tests for InteractionStep model conforming to A2A Traceability Extension.

RED phase: These tests should FAIL initially since InteractionStep model doesn't exist yet.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from green.models import CallType, InteractionStep


class TestCallTypeEnum:
    """Test CallType enumeration."""

    def test_call_type_has_agent_value(self):
        """CallType.AGENT exists for agent-to-agent communication."""
        assert CallType.AGENT is not None
        assert isinstance(CallType.AGENT, Enum)

    def test_call_type_has_tool_value(self):
        """CallType.TOOL exists for tool invocations."""
        assert CallType.TOOL is not None
        assert isinstance(CallType.TOOL, Enum)

    def test_call_type_has_host_value(self):
        """CallType.HOST exists for host system calls."""
        assert CallType.HOST is not None
        assert isinstance(CallType.HOST, Enum)


class TestInteractionStepModel:
    """Test InteractionStep model conforms to A2A Traceability Extension Step specification."""

    def test_interaction_step_has_step_id_field(self):
        """InteractionStep model includes step_id field."""
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
        )
        assert step.step_id == "step-001"

    def test_interaction_step_has_trace_id_field(self):
        """InteractionStep model includes trace_id field."""
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
        )
        assert step.trace_id == "trace-123"

    def test_interaction_step_has_call_type_field(self):
        """InteractionStep model includes call_type field."""
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.TOOL,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
        )
        assert step.call_type == CallType.TOOL

    def test_interaction_step_has_start_time_field(self):
        """InteractionStep model includes start_time field."""
        start = datetime.now(UTC)
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=start,
            end_time=datetime.now(UTC),
        )
        assert step.start_time == start

    def test_interaction_step_has_end_time_field(self):
        """InteractionStep model includes end_time field."""
        start = datetime.now(UTC)
        end = datetime.now(UTC)
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=start,
            end_time=end,
        )
        assert step.end_time == end

    def test_interaction_step_has_latency_field(self):
        """InteractionStep model includes latency field (auto-calculated)."""
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            latency=150,
        )
        assert step.latency == 150

    def test_interaction_step_has_optional_error_field(self):
        """InteractionStep model includes optional error field."""
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            error="Connection timeout",
        )
        assert step.error == "Connection timeout"

    def test_interaction_step_error_is_optional(self):
        """InteractionStep error field is optional (None by default)."""
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
        )
        assert step.error is None

    def test_interaction_step_has_optional_parent_step_id_field(self):
        """InteractionStep model includes optional parent_step_id field."""
        step = InteractionStep(
            step_id="step-002",
            trace_id="trace-123",
            call_type=CallType.TOOL,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            parent_step_id="step-001",
        )
        assert step.parent_step_id == "step-001"

    def test_interaction_step_parent_step_id_is_optional(self):
        """InteractionStep parent_step_id field is optional (None by default)."""
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
        )
        assert step.parent_step_id is None


class TestCallTypeClassification:
    """Test CallType classification requirements."""

    def test_call_type_agent_for_messenger(self):
        """CallType.AGENT used for messenger (agent-to-agent communication)."""
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
        )
        assert step.call_type == CallType.AGENT

    def test_call_type_tool_for_llm(self):
        """CallType.TOOL used for LLM invocations."""
        step = InteractionStep(
            step_id="step-002",
            trace_id="trace-123",
            call_type=CallType.TOOL,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
        )
        assert step.call_type == CallType.TOOL

    def test_call_type_host_for_graph(self):
        """CallType.HOST used for graph analysis."""
        step = InteractionStep(
            step_id="step-003",
            trace_id="trace-123",
            call_type=CallType.HOST,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
        )
        assert step.call_type == CallType.HOST


class TestInteractionStepA2AConformance:
    """Test InteractionStep conforms to A2A Traceability Extension Step specification."""

    def test_interaction_step_supports_nested_tracing(self):
        """InteractionStep supports nested tracing via parent_step_id."""
        parent_step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
        )

        child_step = InteractionStep(
            step_id="step-002",
            trace_id="trace-123",
            call_type=CallType.TOOL,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            parent_step_id=parent_step.step_id,
        )

        assert child_step.parent_step_id == parent_step.step_id
        assert child_step.trace_id == parent_step.trace_id

    def test_interaction_step_latency_in_milliseconds(self):
        """InteractionStep latency is measured in milliseconds."""
        step = InteractionStep(
            step_id="step-001",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),
            latency=250,
        )
        # Latency should be a positive integer representing milliseconds
        assert isinstance(step.latency, (int, type(None)))
        if step.latency is not None:
            assert step.latency >= 0


class TestAgentCardExtensions:
    """Test AgentCard extension declarations for A2A compliance."""

    def test_get_agent_extensions_returns_list(self):
        """get_agent_extensions() returns list of extension URIs."""
        from green.models import get_agent_extensions

        extensions = get_agent_extensions()
        assert isinstance(extensions, list)

    def test_agent_extensions_include_traceability(self):
        """AgentCard declares traceability extension support."""
        from green.models import get_agent_extensions

        extensions = get_agent_extensions()
        # Check for traceability extension (URI may vary based on spec version)
        traceability_extensions = [ext for ext in extensions if "traceability" in ext["uri"].lower()]
        assert len(traceability_extensions) > 0, "Traceability extension not declared"

    def test_agent_extensions_include_timestamp(self):
        """AgentCard declares timestamp extension support."""
        from green.models import get_agent_extensions

        extensions = get_agent_extensions()
        # Check for timestamp extension
        timestamp_extensions = [ext for ext in extensions if "timestamp" in ext["uri"].lower()]
        assert len(timestamp_extensions) > 0, "Timestamp extension not declared"
