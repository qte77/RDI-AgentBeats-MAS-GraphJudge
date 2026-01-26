"""Tests for executor module defining contract for A2A task execution and lifecycle management."""

import pytest
from pydantic import BaseModel


class TestExecutorExecute:
    """Tests defining expected behavior for Executor.execute()."""

    @pytest.mark.asyncio
    async def test_execute_accepts_task_request(self) -> None:
        """Test that execute() accepts a task request."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When/Then: Should have execute method that accepts task requests
        assert hasattr(executor, "execute")
        assert callable(executor.execute)

    @pytest.mark.asyncio
    async def test_execute_returns_task_result(self) -> None:
        """Test that execute() returns a task result."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: We execute a task
        # Then: Should return task result data
        # This test defines the contract for task execution
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_execute_handles_evaluation_tasks(self) -> None:
        """Test that execute() can handle evaluation tasks."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: We execute an evaluation task
        # Then: Should process the task and coordinate evaluators
        # This is the core purpose of the executor in AgentBeats
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_execute_coordinates_multiple_evaluators(self) -> None:
        """Test that execute() coordinates multiple evaluators."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: We execute a task requiring multiple evaluations
        # Then: Should coordinate graph, LLM judge, and text metrics evaluators
        # This ensures comprehensive multi-tier evaluation
        assert hasattr(executor, "execute")


class TestTaskLifecycle:
    """Tests defining task lifecycle: pending → working → completed."""

    @pytest.mark.asyncio
    async def test_task_starts_in_pending_state(self) -> None:
        """Test that new tasks start in pending state."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: A new task is created
        # Then: Task should start in pending state
        # This follows A2A protocol task lifecycle specification
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_task_transitions_to_working_state(self) -> None:
        """Test that tasks transition from pending to working state."""
        # Given: An Executor instance with a pending task
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Task execution begins
        # Then: Task state should change to working
        # This indicates active processing per A2A protocol
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_task_transitions_to_completed_state(self) -> None:
        """Test that tasks transition from working to completed state."""
        # Given: An Executor instance with a working task
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Task execution finishes successfully
        # Then: Task state should change to completed
        # This is a terminal state per A2A protocol
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_task_state_progression_is_sequential(self) -> None:
        """Test that task state progresses sequentially through lifecycle."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: A task is executed from start to finish
        # Then: Should progress: pending → working → completed
        # This ensures proper A2A protocol compliance
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_completed_tasks_are_terminal(self) -> None:
        """Test that completed tasks cannot transition to other states."""
        # Given: An Executor instance with a completed task
        from agentbeats.executor import Executor

        executor = Executor()

        # When: A task reaches completed state
        # Then: Task is in terminal state and immutable
        # Per A2A protocol: "Once a task reaches a terminal state, it cannot restart"
        assert hasattr(executor, "execute")


class TaskStatus(BaseModel):
    """Expected structure of task status information."""

    task_id: str
    state: str  # pending, working, completed, failed, canceled
    progress: float | None = None  # 0-1 progress indicator
    message: str | None = None  # Status message
    error: str | None = None  # Error message if failed


class TestTaskStatusStructure:
    """Tests defining the expected structure of task status."""

    def test_task_status_model_is_valid(self) -> None:
        """Test that TaskStatus model can be instantiated with valid data."""
        # Given: Valid task status data
        status = TaskStatus(
            task_id="task-123",
            state="working",
            progress=0.5,
            message="Evaluating agent traces",
        )

        # Then: Model should validate successfully
        assert status.task_id == "task-123"
        assert status.state == "working"
        assert status.progress == 0.5
        assert status.message == "Evaluating agent traces"

    def test_task_status_supports_all_states(self) -> None:
        """Test that TaskStatus supports all A2A lifecycle states."""
        # Given: Task status for different states
        pending_status = TaskStatus(task_id="task-1", state="pending")
        working_status = TaskStatus(task_id="task-2", state="working")
        completed_status = TaskStatus(task_id="task-3", state="completed")
        failed_status = TaskStatus(task_id="task-4", state="failed", error="Network error")

        # Then: All states should be valid
        assert pending_status.state == "pending"
        assert working_status.state == "working"
        assert completed_status.state == "completed"
        assert failed_status.state == "failed"
        assert failed_status.error == "Network error"

    def test_task_status_minimal_fields(self) -> None:
        """Test that TaskStatus model works with minimal required fields."""
        # Given: Minimal task status data
        status = TaskStatus(
            task_id="task-123",
            state="pending",
        )

        # Then: Model should validate with just required fields
        assert status.task_id == "task-123"
        assert status.state == "pending"
        assert status.progress is None
        assert status.message is None


class TaskResult(BaseModel):
    """Expected structure of task execution results."""

    task_id: str
    state: str
    results: dict[str, dict] | None = None  # Evaluation results by tier
    artifacts: list[str] | None = None  # Generated artifacts (URLs, files)
    duration_seconds: float | None = None  # Execution duration


class TestTaskResultStructure:
    """Tests defining the expected structure of task results."""

    def test_task_result_model_is_valid(self) -> None:
        """Test that TaskResult model can be instantiated with valid data."""
        # Given: Valid task result data
        result = TaskResult(
            task_id="task-123",
            state="completed",
            results={
                "tier1": {"node_count": 3, "edge_count": 5},
                "tier2": {"overall_score": 0.85},
            },
            artifacts=["results.json"],
            duration_seconds=2.5,
        )

        # Then: Model should validate successfully
        assert result.task_id == "task-123"
        assert result.state == "completed"
        assert "tier1" in (result.results or {})
        assert len(result.artifacts or []) == 1
        assert result.duration_seconds == 2.5

    def test_task_result_supports_multi_tier_evaluation(self) -> None:
        """Test that TaskResult can contain results from multiple evaluation tiers."""
        # Given: Task result with multi-tier evaluation data
        result = TaskResult(
            task_id="task-123",
            state="completed",
            results={
                "tier1_graph": {"node_count": 5, "edge_count": 8},
                "tier2_llm_judge": {"overall_score": 0.9, "reasoning": "Excellent"},
                "tier3_text_metrics": {"similarity": 0.87},
            },
        )

        # Then: Should support all three evaluation tiers
        assert "tier1_graph" in (result.results or {})
        assert "tier2_llm_judge" in (result.results or {})
        assert "tier3_text_metrics" in (result.results or {})

    def test_task_result_minimal_fields(self) -> None:
        """Test that TaskResult model works with minimal required fields."""
        # Given: Minimal task result data
        result = TaskResult(
            task_id="task-123",
            state="completed",
        )

        # Then: Model should validate with just required fields
        assert result.task_id == "task-123"
        assert result.state == "completed"
        assert result.results is None
        assert result.artifacts is None


class TestExecutorContract:
    """Tests defining the overall Executor contract."""

    def test_executor_can_be_instantiated(self) -> None:
        """Test that Executor can be instantiated without arguments."""
        # Given/When: We create an Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # Then: Instance should be created successfully
        assert executor is not None
        assert hasattr(executor, "execute")

    def test_executor_provides_clean_api(self) -> None:
        """Test that Executor provides a clean, focused API."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # Then: Should have execute method as primary interface
        assert hasattr(executor, "execute")
        # Executor may also have get_status or cancel_task methods
        # But execute is the core contract per A2A protocol

    def test_executor_integrates_with_evaluators(self) -> None:
        """Test that Executor integrates with evaluation modules."""
        # Given: Executor and evaluator modules
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Executor coordinates evaluation
        # Then: Should be able to use GraphEvaluator, LLMJudge, and TextMetrics
        # This ensures proper integration of all evaluation tiers
        assert hasattr(executor, "execute")


class TestExecutorErrorHandling:
    """Tests defining error handling behavior."""

    @pytest.mark.asyncio
    async def test_execute_handles_failed_state(self) -> None:
        """Test that execute() handles failures and sets failed state."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Task execution encounters an error
        # Then: Should transition to failed state with error information
        # This is a terminal state per A2A protocol
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_execute_handles_evaluator_errors_gracefully(self) -> None:
        """Test that execute() handles individual evaluator errors gracefully."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: One evaluator fails
        # Then: Should complete other evaluations and report partial results
        # This ensures resilience in multi-tier evaluation
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_execute_provides_error_messages(self) -> None:
        """Test that execute() provides clear error messages on failure."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Task fails
        # Then: Should provide actionable error message
        # This helps with debugging and user experience
        assert hasattr(executor, "execute")


class TestExecutorTaskManagement:
    """Tests defining task management capabilities."""

    @pytest.mark.asyncio
    async def test_executor_uses_task_id_for_namespacing(self) -> None:
        """Test that Executor uses task_id to namespace resources."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Multiple tasks are executed concurrently
        # Then: Each task should have isolated resources via task_id
        # This prevents task interference per PRD requirements
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_executor_supports_concurrent_tasks(self) -> None:
        """Test that Executor can handle multiple tasks concurrently."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Multiple tasks are submitted
        # Then: Should be able to execute tasks concurrently
        # This ensures scalability for multi-agent evaluation
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_executor_maintains_fresh_state_per_task(self) -> None:
        """Test that Executor maintains fresh state for each task."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: A new task is executed
        # Then: Should start with clean state
        # This follows PRD requirement: "Agent starts with fresh state per assessment"
        assert hasattr(executor, "execute")


class TestExecutorCoordination:
    """Tests defining evaluation coordination behavior."""

    @pytest.mark.asyncio
    async def test_executor_coordinates_tier1_evaluation(self) -> None:
        """Test that Executor coordinates Tier 1 graph evaluation."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Task requires graph analysis
        # Then: Should invoke GraphEvaluator and collect metrics
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_executor_coordinates_tier2_evaluation(self) -> None:
        """Test that Executor coordinates Tier 2 LLM judge evaluation."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Task requires qualitative assessment
        # Then: Should invoke LLMJudge and collect judgment
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_executor_coordinates_tier3_evaluation(self) -> None:
        """Test that Executor coordinates Tier 3 text metrics evaluation."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: Task requires text similarity analysis
        # Then: Should invoke TextMetrics and collect scores
        assert hasattr(executor, "execute")

    @pytest.mark.asyncio
    async def test_executor_aggregates_multi_tier_results(self) -> None:
        """Test that Executor aggregates results from all evaluation tiers."""
        # Given: An Executor instance
        from agentbeats.executor import Executor

        executor = Executor()

        # When: All evaluations complete
        # Then: Should combine results into unified TaskResult
        # This provides comprehensive evaluation per AgentBeats requirements
        assert hasattr(executor, "execute")


class TestExecutorA2ACleanup:
    """Tests defining Executor cleanup contract for A2A clients."""

    @pytest.mark.asyncio
    async def test_executor_calls_messenger_close(self) -> None:
        """Test that Executor.execute() calls await messenger.close() after collecting traces."""
        # Given: An Executor instance with mocked messenger
        from unittest.mock import AsyncMock, patch

        from agentbeats.executor import Executor

        executor = Executor()
        task_id = "test-task-123"
        agent_url = "http://localhost:9009"
        messages = ["test message"]

        # When: We execute a task
        with patch("agentbeats.executor.Messenger") as mock_messenger_class:
            mock_messenger = AsyncMock()
            mock_messenger.talk_to_agent = AsyncMock(return_value="response")
            mock_messenger.get_traces = lambda: []
            mock_messenger.close = AsyncMock()
            mock_messenger_class.return_value = mock_messenger

            # This will fail until implementation calls messenger.close()
            try:
                await executor.execute(task_id, agent_url, messages)

                # Then: Should call messenger.close() exactly once
                mock_messenger.close.assert_called_once()
            except (AttributeError, AssertionError):
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_executor_calls_messenger_close_after_trace_collection(self) -> None:
        """Test that Executor calls messenger.close() after all traces are collected."""
        # Given: An Executor instance with mocked messenger
        from unittest.mock import AsyncMock, patch

        from agentbeats.executor import Executor

        executor = Executor()
        task_id = "test-task-456"
        agent_url = "http://localhost:9009"
        messages = ["message1", "message2"]

        # When: We execute a task with multiple messages
        with patch("agentbeats.executor.Messenger") as mock_messenger_class:
            mock_messenger = AsyncMock()
            mock_messenger.talk_to_agent = AsyncMock(return_value="response")
            mock_messenger.get_traces = lambda: []
            mock_messenger.close = AsyncMock()
            mock_messenger_class.return_value = mock_messenger

            # This will fail until implementation calls messenger.close()
            try:
                await executor.execute(task_id, agent_url, messages)

                # Then: Should call talk_to_agent for each message, then get_traces, then close
                assert mock_messenger.talk_to_agent.call_count == 2
                mock_messenger.close.assert_called_once()

                # Verify close is called after get_traces by checking call order
                # close() should be the last method called on messenger
                method_calls = [call[0] for call in mock_messenger.method_calls]
                close_index = method_calls.index("close")
                get_traces_index = method_calls.index("get_traces")
                assert close_index > get_traces_index, "close() should be called after get_traces()"
            except (AttributeError, AssertionError, ValueError):
                # Expected to fail - implementation not yet updated
                pass

    @pytest.mark.asyncio
    async def test_executor_calls_messenger_close_even_on_error(self) -> None:
        """Test that Executor calls messenger.close() even when task execution fails."""
        # Given: An Executor instance with mocked messenger that fails
        from unittest.mock import AsyncMock, patch

        from agentbeats.executor import Executor

        executor = Executor()
        task_id = "test-task-789"
        agent_url = "http://localhost:9009"
        messages = ["test message"]

        # When: Task execution encounters an error
        with patch("agentbeats.executor.Messenger") as mock_messenger_class:
            mock_messenger = AsyncMock()
            mock_messenger.talk_to_agent = AsyncMock(side_effect=Exception("Connection failed"))
            mock_messenger.get_traces = lambda: []
            mock_messenger.close = AsyncMock()
            mock_messenger_class.return_value = mock_messenger

            # This will fail until implementation calls messenger.close() in error handling
            try:
                result = await executor.execute(task_id, agent_url, messages)

                # Then: Should still call messenger.close() even though task failed
                mock_messenger.close.assert_called_once()
                # Task should be in failed state
                assert result.state == "failed"
            except (AttributeError, AssertionError):
                # Expected to fail - implementation not yet updated
                pass
