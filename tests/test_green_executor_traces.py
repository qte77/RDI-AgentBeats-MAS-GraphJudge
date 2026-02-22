"""Tests for Executor with trace collection and cleanup.

RED phase: These tests should FAIL initially since Executor doesn't exist yet.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.models import TraceCollectionConfig
from green.executor import Executor
from green.models import CallType, InteractionStep


@pytest.fixture
def mock_messenger():
    """Mock Messenger."""
    messenger = MagicMock()
    messenger.send_message = AsyncMock(return_value="Response from agent")
    messenger.close = AsyncMock()
    return messenger


class TestExecutorInitialization:
    """Test Executor initialization."""

    def test_executor_can_be_instantiated(self):
        """Executor can be instantiated."""
        executor = Executor(coordination_rounds=3)
        assert executor is not None


class TestExecutorTraceCollection:
    """Test Executor trace collection functionality."""

    async def test_executor_collects_interaction_traces_during_execution(self, mock_messenger):
        """Executor collects interaction traces during task execution."""
        executor = Executor(coordination_rounds=3)

        # Execute a simple task that involves sending messages
        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        # Should return traces
        assert traces is not None
        assert isinstance(traces, list)

    async def test_traces_include_all_interaction_step_fields(self, mock_messenger):
        """Traces include all InteractionStep fields (step_id, trace_id, latency, etc)."""
        executor = Executor(coordination_rounds=3)

        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        # Should have at least one trace
        assert len(traces) > 0

        # First trace should be an InteractionStep with all required fields
        trace = traces[0]
        assert isinstance(trace, InteractionStep)
        assert hasattr(trace, "step_id")
        assert hasattr(trace, "trace_id")
        assert hasattr(trace, "call_type")
        assert hasattr(trace, "start_time")
        assert hasattr(trace, "end_time")
        assert hasattr(trace, "latency")

    async def test_traces_have_correct_call_type(self, mock_messenger):
        """Traces have correct CallType classification."""
        executor = Executor(coordination_rounds=3)

        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        # Agent-to-agent communication should be classified as AGENT
        assert len(traces) > 0
        assert traces[0].call_type == CallType.AGENT

    async def test_traces_have_valid_timing_data(self, mock_messenger):
        """Traces have valid timing data (start_time, end_time, latency)."""
        executor = Executor(coordination_rounds=3)

        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        assert len(traces) > 0
        trace = traces[0]

        # Should have timing data
        assert isinstance(trace.start_time, datetime)
        assert isinstance(trace.end_time, datetime)
        assert trace.end_time >= trace.start_time

        # Latency should be calculated (in milliseconds)
        assert trace.latency is not None
        assert trace.latency >= 0


class TestExecutorCleanup:
    """Test Executor cleanup functionality."""

    async def test_executor_calls_messenger_close_after_trace_collection(self, mock_messenger):
        """Executor calls await messenger.close() after trace collection."""
        executor = Executor(coordination_rounds=3)

        await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        # Messenger.close() should have been called
        mock_messenger.close.assert_called_once()

    async def test_executor_closes_messenger_even_on_error(self, mock_messenger):
        """Executor closes messenger even if task execution fails."""
        mock_messenger.send_message.side_effect = Exception("Task execution failed")

        executor = Executor(coordination_rounds=3)

        with pytest.raises(Exception):
            await executor.execute_task(
                task_description="Test task",
                messenger=mock_messenger,
                agent_url="http://agent.example.com:9009",
            )

        # Messenger.close() should still have been called
        mock_messenger.close.assert_called_once()


class TestExecutorTaskExecution:
    """Test Executor task execution flow."""

    async def test_executor_sends_message_via_messenger(self, mock_messenger):
        """Executor uses messenger to send task to agent."""
        executor = Executor(coordination_rounds=3)

        await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        # Should have sent message via messenger (may be multiple rounds)
        mock_messenger.send_message.assert_called()
        first_call = mock_messenger.send_message.call_args_list[0]
        assert first_call[1]["url"] == "http://agent.example.com:9009"
        assert "Test task" in first_call[1]["message"]

    async def test_executor_generates_unique_trace_ids(self, mock_messenger):
        """Executor generates unique trace IDs for different executions."""
        executor = Executor(coordination_rounds=3)

        traces1 = await executor.execute_task(
            task_description="Task 1",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        traces2 = await executor.execute_task(
            task_description="Task 2",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        # Different executions should have different trace IDs
        assert traces1[0].trace_id != traces2[0].trace_id

    async def test_executor_generates_unique_step_ids(self, mock_messenger):
        """Executor generates unique step IDs for each interaction."""
        executor = Executor(coordination_rounds=3)

        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        # Each step should have unique step_id
        step_ids = [trace.step_id for trace in traces]
        assert len(step_ids) == len(set(step_ids))  # All unique


class TestExecutorLatencyEvaluation:
    """Test Executor latency evaluation functionality."""

    def test_executor_has_evaluate_latency_method(self):
        """Executor includes _evaluate_latency() method for Tier 2 assessment."""
        executor = Executor(coordination_rounds=3)
        assert hasattr(executor, "_evaluate_latency")
        assert callable(executor._evaluate_latency)

    async def test_executor_evaluate_latency_returns_metrics(self, mock_messenger):
        """Executor._evaluate_latency() returns LatencyMetrics."""
        from green.evals.system import LatencyMetrics

        executor = Executor(coordination_rounds=3)

        # Collect traces
        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )

        # Evaluate latency
        result = executor._evaluate_latency(traces)

        # Should return LatencyMetrics
        assert isinstance(result, LatencyMetrics)
        assert hasattr(result, "avg")
        assert hasattr(result, "p50")
        assert hasattr(result, "p95")
        assert hasattr(result, "p99")
        assert hasattr(result, "slowest_agent")


class TestAdaptiveCollectionStrategy:
    """Tests for adaptive hybrid trace collection strategy (idle + timeout + completion)."""

    async def test_executor_accepts_trace_collection_config(self):
        """Executor accepts TraceCollectionConfig as optional parameter."""
        config = TraceCollectionConfig(max_timeout_seconds=5, idle_threshold_seconds=1)
        executor = Executor(coordination_rounds=3, trace_collection=config)
        assert executor is not None

    async def test_adaptive_collects_at_least_one_trace(self, mock_messenger):
        """Adaptive executor collects at least one trace."""
        config = TraceCollectionConfig(
            max_timeout_seconds=1, idle_threshold_seconds=0.5, use_completion_signals=False
        )
        executor = Executor(coordination_rounds=3, trace_collection=config)
        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )
        assert len(traces) >= 1

    async def test_adaptive_stops_on_completion_signal(self, mock_messenger):
        """Adaptive loop stops after first response with status=complete."""
        mock_messenger.send_message = AsyncMock(return_value='{"status": "complete"}')
        config = TraceCollectionConfig(
            max_timeout_seconds=10, idle_threshold_seconds=5, use_completion_signals=True
        )
        executor = Executor(coordination_rounds=99, trace_collection=config)
        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )
        assert len(traces) == 1
        mock_messenger.send_message.assert_called_once()

    async def test_adaptive_ignores_completion_signal_when_disabled(self, mock_messenger):
        """When use_completion_signals=False, completion signal is not honoured."""
        mock_messenger.send_message = AsyncMock(return_value='{"status": "complete"}')
        config = TraceCollectionConfig(
            max_timeout_seconds=0.05,
            idle_threshold_seconds=10,
            use_completion_signals=False,
        )
        executor = Executor(coordination_rounds=99, trace_collection=config)
        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )
        # Stops on timeout, not on completion signal — so more than 1 call
        assert mock_messenger.send_message.call_count > 1
        assert len(traces) >= 1

    async def test_adaptive_stops_on_max_timeout(self, mock_messenger):
        """Adaptive loop stops after max_timeout_seconds regardless of activity."""

        async def slow_response(url: str, message: str) -> str:
            await asyncio.sleep(0.05)
            return "Response"

        mock_messenger.send_message.side_effect = slow_response
        config = TraceCollectionConfig(
            max_timeout_seconds=0.08,
            idle_threshold_seconds=10,
            use_completion_signals=False,
        )
        executor = Executor(coordination_rounds=100, trace_collection=config)
        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )
        assert len(traces) < 10

    async def test_adaptive_stops_on_idle_threshold(self, mock_messenger):
        """Adaptive loop stops when agent doesn't respond within idle_threshold_seconds."""
        call_count = 0

        async def slow_after_first(url: str, message: str) -> str:
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                await asyncio.sleep(0.2)
            return "Response"

        mock_messenger.send_message.side_effect = slow_after_first
        config = TraceCollectionConfig(
            max_timeout_seconds=10,
            idle_threshold_seconds=0.05,
            use_completion_signals=False,
        )
        executor = Executor(coordination_rounds=99, trace_collection=config)
        traces = await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )
        assert len(traces) == 1

    async def test_adaptive_closes_messenger_after_collection(self, mock_messenger):
        """Adaptive executor calls messenger.close() after collection completes."""
        mock_messenger.send_message = AsyncMock(return_value='{"status": "complete"}')
        config = TraceCollectionConfig(
            max_timeout_seconds=5, idle_threshold_seconds=5, use_completion_signals=True
        )
        executor = Executor(coordination_rounds=3, trace_collection=config)
        await executor.execute_task(
            task_description="Test task",
            messenger=mock_messenger,
            agent_url="http://agent.example.com:9009",
        )
        mock_messenger.close.assert_called_once()
