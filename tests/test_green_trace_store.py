"""Tests for Green Agent trace store.

RED phase: These tests should FAIL initially since green.trace_store doesn't exist yet.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from common.models import CallType, InteractionStep


@pytest.fixture
def sample_traces():
    """Sample trace data for testing."""
    return [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-123",
            call_type=CallType.AGENT,
            start_time=datetime(2026, 1, 31, 10, 0, 0),
            end_time=datetime(2026, 1, 31, 10, 0, 1),
            latency=1000,
        ),
        InteractionStep(
            step_id="step-2",
            trace_id="trace-123",
            call_type=CallType.TOOL,
            start_time=datetime(2026, 1, 31, 10, 0, 1),
            end_time=datetime(2026, 1, 31, 10, 0, 2),
            latency=1000,
        ),
    ]


class TestTraceStoreInitialization:
    """Test TraceStore initialization."""

    def test_trace_store_initializes_empty(self):
        """TraceStore initializes with empty storage."""
        from green.trace_store import TraceStore

        store = TraceStore()
        assert store is not None
        assert len(store.get_all_traces()) == 0

    def test_trace_store_initializes_with_empty_registry(self):
        """TraceStore initializes with empty agent registry."""
        from green.trace_store import TraceStore

        store = TraceStore()
        assert store is not None
        assert len(store.get_registered_agents()) == 0


class TestTraceStoreAddTraces:
    """Test adding traces to store."""

    def test_trace_store_adds_traces(self, sample_traces):
        """TraceStore stores incoming traces."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.add_traces(sample_traces)

        all_traces = store.get_all_traces()
        assert len(all_traces) == 2

    def test_trace_store_accumulates_traces(self, sample_traces):
        """TraceStore accumulates traces across multiple calls."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.add_traces(sample_traces[:1])
        store.add_traces(sample_traces[1:])

        all_traces = store.get_all_traces()
        assert len(all_traces) == 2

    def test_trace_store_handles_empty_trace_list(self):
        """TraceStore handles empty trace list."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.add_traces([])

        all_traces = store.get_all_traces()
        assert len(all_traces) == 0


class TestTraceStoreGetTraces:
    """Test retrieving traces from store."""

    def test_trace_store_returns_all_traces(self, sample_traces):
        """TraceStore returns all stored traces."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.add_traces(sample_traces)

        all_traces = store.get_all_traces()
        assert len(all_traces) == 2
        assert all_traces[0].step_id == "step-1"
        assert all_traces[1].step_id == "step-2"

    def test_trace_store_get_traces_by_trace_id(self, sample_traces):
        """TraceStore retrieves traces by trace_id."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.add_traces(sample_traces)

        # Add another trace with different trace_id
        other_trace = InteractionStep(
            step_id="step-3",
            trace_id="trace-456",
            call_type=CallType.AGENT,
            start_time=datetime(2026, 1, 31, 10, 0, 2),
            end_time=datetime(2026, 1, 31, 10, 0, 3),
            latency=1000,
        )
        store.add_traces([other_trace])

        # Get traces for specific trace_id
        trace_123 = store.get_traces_by_id("trace-123")
        assert len(trace_123) == 2
        assert all(t.trace_id == "trace-123" for t in trace_123)

    def test_trace_store_clear_traces(self, sample_traces):
        """TraceStore can clear all traces."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.add_traces(sample_traces)
        assert len(store.get_all_traces()) == 2

        store.clear_traces()
        assert len(store.get_all_traces()) == 0


class TestTraceStoreAgentRegistry:
    """Test agent registry functionality."""

    def test_trace_store_registers_agent(self):
        """TraceStore registers agent URLs."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.register_agent("http://agent1:8000")

        agents = store.get_registered_agents()
        assert len(agents) == 1
        assert "http://agent1:8000" in agents

    def test_trace_store_deduplicates_agents(self):
        """TraceStore deduplicates agent URLs."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.register_agent("http://agent1:8000")
        store.register_agent("http://agent1:8000")  # Duplicate

        agents = store.get_registered_agents()
        assert len(agents) == 1

    def test_trace_store_registers_multiple_agents(self):
        """TraceStore registers multiple agent URLs."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.register_agent("http://agent1:8000")
        store.register_agent("http://agent2:8000")
        store.register_agent("http://agent3:8000")

        agents = store.get_registered_agents()
        assert len(agents) == 3
        assert "http://agent1:8000" in agents
        assert "http://agent2:8000" in agents
        assert "http://agent3:8000" in agents

    def test_trace_store_unregister_agent(self):
        """TraceStore can unregister agents."""
        from green.trace_store import TraceStore

        store = TraceStore()
        store.register_agent("http://agent1:8000")
        store.register_agent("http://agent2:8000")

        store.unregister_agent("http://agent1:8000")

        agents = store.get_registered_agents()
        assert len(agents) == 1
        assert "http://agent2:8000" in agents


class TestTraceStoreThreadSafety:
    """Test thread-safety of TraceStore operations."""

    def test_trace_store_concurrent_trace_additions(self, sample_traces):
        """TraceStore handles concurrent trace additions."""
        import asyncio

        from green.trace_store import TraceStore

        store = TraceStore()

        async def add_traces_async():
            store.add_traces(sample_traces[:1])

        async def run_concurrent_additions():
            await asyncio.gather(*[add_traces_async() for _ in range(10)])

        # Run multiple concurrent additions
        asyncio.run(run_concurrent_additions())

        # Should have 10 traces (one per call)
        all_traces = store.get_all_traces()
        assert len(all_traces) == 10

    def test_trace_store_concurrent_agent_registrations(self):
        """TraceStore handles concurrent agent registrations."""
        import asyncio

        from green.trace_store import TraceStore

        store = TraceStore()

        async def register_agent_async(agent_url: str):
            store.register_agent(agent_url)

        async def run_concurrent_registrations():
            await asyncio.gather(
                *[register_agent_async(f"http://agent{i}:8000") for i in range(10)]
            )

        # Run multiple concurrent registrations
        asyncio.run(run_concurrent_registrations())

        # Should have 10 unique agents
        agents = store.get_registered_agents()
        assert len(agents) == 10
