"""Tests for Executor pipeline integration with all evaluators.

RED phase: These tests should FAIL initially until evaluator integration is complete.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from green.executor import Executor
from green.models import CallType, InteractionStep


@pytest.fixture
def mock_messenger():
    """Mock Messenger."""
    messenger = MagicMock()
    messenger.send_message = AsyncMock(return_value="Response from agent")
    messenger.close = AsyncMock()
    return messenger


@pytest.fixture
def sample_traces():
    """Sample interaction traces for testing."""
    now = datetime.now()
    return [
        InteractionStep(
            step_id="step-1",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=now,
            end_time=now,
            latency=1000,
        ),
        InteractionStep(
            step_id="step-2",
            trace_id="trace-1",
            call_type=CallType.AGENT,
            start_time=now,
            end_time=now,
            latency=1500,
        ),
    ]


@pytest.fixture
def mock_graph_evaluator():
    """Mock Graph evaluator."""
    evaluator = MagicMock()
    evaluator.evaluate = AsyncMock(
        return_value={
            "graph_density": 0.5,
            "avg_degree": 2.0,
            "clustering_coefficient": 0.3,
            "bottlenecks": [],
        }
    )
    return evaluator


@pytest.fixture
def mock_llm_judge():
    """Mock LLM Judge evaluator."""
    evaluator = MagicMock()
    evaluator.evaluate = AsyncMock(
        return_value={
            "overall_score": 0.8,
            "reasoning": "Good coordination observed",
            "coordination_quality": "high",
            "strengths": ["Fast response", "Clear communication"],
            "weaknesses": [],
        }
    )
    return evaluator


@pytest.fixture
def mock_latency_evaluator():
    """Mock Latency evaluator."""
    evaluator = MagicMock()
    evaluator.evaluate = AsyncMock(
        return_value={
            "avg": 1250.0,
            "p50": 1250.0,
            "p95": 1500.0,
            "p99": 1500.0,
            "slowest_agent": "step-2",
            "warning": "Latency values only comparable within same system/run",
        }
    )
    return evaluator


class TestExecutorGraphEvaluatorIntegration:
    """Test Executor integrates Graph evaluator (Tier 1)."""

    def test_executor_has_evaluate_graph_method(self):
        """Executor includes _evaluate_graph() method for Tier 1 assessment."""
        executor = Executor()
        assert hasattr(executor, "_evaluate_graph")
        assert callable(executor._evaluate_graph)

    async def test_executor_evaluate_graph_calls_evaluator(self, sample_traces, mock_graph_evaluator):
        """Executor._evaluate_graph() calls graph evaluator with traces."""
        executor = Executor()

        result = await executor._evaluate_graph(sample_traces, mock_graph_evaluator)

        # Should call graph evaluator
        mock_graph_evaluator.evaluate.assert_called_once_with(sample_traces)

        # Should return graph metrics
        assert result is not None
        assert "graph_density" in result

    async def test_executor_evaluate_graph_handles_none_evaluator(self, sample_traces):
        """Executor._evaluate_graph() handles None evaluator gracefully."""
        executor = Executor()

        result = await executor._evaluate_graph(sample_traces, None)

        # Should return None or empty dict when evaluator is None
        assert result is None or result == {}


class TestExecutorLLMJudgeIntegration:
    """Test Executor integrates LLM Judge (Tier 2)."""

    def test_executor_has_evaluate_llm_method(self):
        """Executor includes _evaluate_llm() method for Tier 2 assessment."""
        executor = Executor()
        assert hasattr(executor, "_evaluate_llm")
        assert callable(executor._evaluate_llm)

    async def test_executor_evaluate_llm_calls_evaluator(self, sample_traces, mock_llm_judge):
        """Executor._evaluate_llm() calls LLM judge with traces."""
        executor = Executor()

        graph_results = {"graph_density": 0.5}
        result = await executor._evaluate_llm(sample_traces, mock_llm_judge, graph_results)

        # Should call LLM judge
        mock_llm_judge.evaluate.assert_called_once()

        # Should return LLM judgment
        assert result is not None
        assert "overall_score" in result

    async def test_executor_evaluate_llm_passes_graph_context(self, sample_traces, mock_llm_judge):
        """Executor._evaluate_llm() passes graph results as context to LLM."""
        executor = Executor()

        graph_results = {"graph_density": 0.5, "bottlenecks": []}
        await executor._evaluate_llm(sample_traces, mock_llm_judge, graph_results)

        # Should pass graph results to LLM judge
        call_args = mock_llm_judge.evaluate.call_args
        assert call_args is not None
        # Check if graph_results or graph_metrics was passed
        call_kwargs = call_args[1] if len(call_args) > 1 else {}
        assert "graph_results" in call_kwargs or "graph_metrics" in call_kwargs

    async def test_executor_evaluate_llm_handles_none_evaluator(self, sample_traces):
        """Executor._evaluate_llm() handles None evaluator gracefully."""
        executor = Executor()

        result = await executor._evaluate_llm(sample_traces, None, {})

        # Should return None or empty dict when evaluator is None
        assert result is None or result == {}


class TestExecutorPipelineOrchestration:
    """Test Executor orchestrates all evaluators in correct order."""

    async def test_executor_evaluate_all_calls_graph_first(
        self, sample_traces, mock_graph_evaluator, mock_llm_judge, mock_latency_evaluator
    ):
        """Executor.evaluate_all() calls graph evaluator first (Tier 1)."""
        executor = Executor()

        await executor.evaluate_all(
            traces=sample_traces,
            graph_evaluator=mock_graph_evaluator,
            llm_judge=mock_llm_judge,
            latency_evaluator=mock_latency_evaluator,
        )

        # Graph evaluator should be called
        mock_graph_evaluator.evaluate.assert_called_once_with(sample_traces)

    async def test_executor_evaluate_all_calls_tier2_evaluators(
        self, sample_traces, mock_graph_evaluator, mock_llm_judge, mock_latency_evaluator
    ):
        """Executor.evaluate_all() calls LLM judge and latency evaluators (Tier 2)."""
        executor = Executor()

        await executor.evaluate_all(
            traces=sample_traces,
            graph_evaluator=mock_graph_evaluator,
            llm_judge=mock_llm_judge,
            latency_evaluator=mock_latency_evaluator,
        )

        # Both Tier 2 evaluators should be called
        mock_llm_judge.evaluate.assert_called_once()
        mock_latency_evaluator.evaluate.assert_called_once()

    async def test_executor_evaluate_all_returns_aggregated_results(
        self, sample_traces, mock_graph_evaluator, mock_llm_judge, mock_latency_evaluator
    ):
        """Executor.evaluate_all() returns aggregated results from all evaluators."""
        executor = Executor()

        results = await executor.evaluate_all(
            traces=sample_traces,
            graph_evaluator=mock_graph_evaluator,
            llm_judge=mock_llm_judge,
            latency_evaluator=mock_latency_evaluator,
        )

        # Should return structured results with all tiers
        assert results is not None
        assert isinstance(results, dict)

        # Should include results from all tiers
        assert "tier1_graph" in results
        assert "tier2_llm" in results
        assert "tier2_latency" in results

    async def test_executor_evaluate_all_passes_graph_results_to_llm(
        self, sample_traces, mock_graph_evaluator, mock_llm_judge, mock_latency_evaluator
    ):
        """Executor.evaluate_all() passes graph results to LLM judge for context."""
        executor = Executor()

        await executor.evaluate_all(
            traces=sample_traces,
            graph_evaluator=mock_graph_evaluator,
            llm_judge=mock_llm_judge,
            latency_evaluator=mock_latency_evaluator,
        )

        # LLM judge should receive graph results as context
        call_args = mock_llm_judge.evaluate.call_args
        assert call_args is not None

        # Graph results should be passed to LLM
        call_kwargs = call_args[1] if len(call_args) > 1 else {}
        assert "graph_results" in call_kwargs or "graph_metrics" in call_kwargs


class TestExecutorPipelineErrorHandling:
    """Test Executor pipeline handles errors gracefully."""

    async def test_executor_pipeline_continues_when_graph_evaluator_fails(
        self, sample_traces, mock_llm_judge, mock_latency_evaluator
    ):
        """Pipeline continues when graph evaluator fails."""
        failing_graph = MagicMock()
        failing_graph.evaluate = AsyncMock(side_effect=Exception("Graph evaluation failed"))

        executor = Executor()

        results = await executor.evaluate_all(
            traces=sample_traces,
            graph_evaluator=failing_graph,
            llm_judge=mock_llm_judge,
            latency_evaluator=mock_latency_evaluator,
        )

        # Should still return results (with error in tier1_graph)
        assert results is not None
        assert "tier1_graph" in results

        # Other tiers should still execute
        assert "tier2_llm" in results
        assert "tier2_latency" in results

    async def test_executor_pipeline_continues_when_llm_judge_fails(
        self, sample_traces, mock_graph_evaluator, mock_latency_evaluator
    ):
        """Pipeline continues when LLM judge fails."""
        failing_llm = MagicMock()
        failing_llm.evaluate = AsyncMock(side_effect=Exception("LLM evaluation failed"))

        executor = Executor()

        results = await executor.evaluate_all(
            traces=sample_traces,
            graph_evaluator=mock_graph_evaluator,
            llm_judge=failing_llm,
            latency_evaluator=mock_latency_evaluator,
        )

        # Should still return results
        assert results is not None
        assert "tier2_llm" in results

        # Other tiers should still execute
        assert "tier1_graph" in results
        assert "tier2_latency" in results

    async def test_executor_pipeline_continues_when_latency_evaluator_fails(
        self, sample_traces, mock_graph_evaluator, mock_llm_judge
    ):
        """Pipeline continues when latency evaluator fails."""
        failing_latency = MagicMock()
        failing_latency.evaluate = AsyncMock(side_effect=Exception("Latency evaluation failed"))

        executor = Executor()

        results = await executor.evaluate_all(
            traces=sample_traces,
            graph_evaluator=mock_graph_evaluator,
            llm_judge=mock_llm_judge,
            latency_evaluator=failing_latency,
        )

        # Should still return results
        assert results is not None
        assert "tier2_latency" in results

        # Other tiers should still execute
        assert "tier1_graph" in results
        assert "tier2_llm" in results
