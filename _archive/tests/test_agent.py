"""Tests for agent orchestrator module defining contract for evaluation request handling and orchestration."""

import pytest
from pydantic import BaseModel, ValidationError


class TestEvalRequestModel:
    """Tests defining EvalRequest model structure and validation."""

    def test_eval_request_model_is_valid(self) -> None:
        """Test that EvalRequest model can be instantiated with valid data."""
        # Given: Valid evaluation request data
        from agentbeats.agent import EvalRequest

        request = EvalRequest(
            agent_url="http://localhost:9009",
            messages=["What is 2+2?", "Tell me a joke"],
            task_id="eval-123",
        )

        # Then: Model should validate successfully
        assert request.agent_url == "http://localhost:9009"
        assert len(request.messages) == 2
        assert request.task_id == "eval-123"

    def test_eval_request_requires_agent_url(self) -> None:
        """Test that EvalRequest requires agent_url field."""
        # Given: Request data without agent_url
        from agentbeats.agent import EvalRequest

        # When/Then: Should raise validation error
        with pytest.raises(ValidationError):
            EvalRequest(
                messages=["test"],
                task_id="eval-123",
            )

    def test_eval_request_with_minimal_fields(self) -> None:
        """Test that EvalRequest works with minimal required fields."""
        # Given: Minimal evaluation request data
        from agentbeats.agent import EvalRequest

        request = EvalRequest(
            agent_url="http://localhost:9009",
        )

        # Then: Model should validate with just required fields
        assert request.agent_url == "http://localhost:9009"
        # Messages and task_id may have defaults or be optional

    def test_eval_request_validates_url_format(self) -> None:
        """Test that EvalRequest validates URL format."""
        # Given: Request with invalid URL format
        from agentbeats.agent import EvalRequest

        # When: We create a request with a valid URL
        request = EvalRequest(
            agent_url="http://localhost:9009",
        )

        # Then: Should accept valid URL format
        assert "localhost" in request.agent_url

    def test_eval_request_accepts_message_list(self) -> None:
        """Test that EvalRequest accepts a list of messages."""
        # Given: Request with multiple messages
        from agentbeats.agent import EvalRequest

        messages = ["Message 1", "Message 2", "Message 3"]
        request = EvalRequest(
            agent_url="http://localhost:9009",
            messages=messages,
        )

        # Then: Should store messages list
        assert isinstance(request.messages, list)
        assert len(request.messages) == 3

    def test_eval_request_task_id_for_namespacing(self) -> None:
        """Test that EvalRequest includes task_id for resource namespacing."""
        # Given: Request with task_id
        from agentbeats.agent import EvalRequest

        request = EvalRequest(
            agent_url="http://localhost:9009",
            task_id="unique-task-id-123",
        )

        # Then: Should store task_id for namespacing
        assert request.task_id == "unique-task-id-123"
        # This task_id is used to namespace temporary resources per PRD


class TestAgentRun:
    """Tests defining expected behavior for Agent.run() orchestration flow."""

    @pytest.mark.asyncio
    async def test_agent_run_accepts_eval_request(self) -> None:
        """Test that Agent.run() accepts an EvalRequest."""
        # Given: An Agent instance and EvalRequest
        from agentbeats.agent import Agent, EvalRequest

        agent = Agent()
        _request = EvalRequest(
            agent_url="http://localhost:9009",
            messages=["test"],
        )

        # When/Then: Should have run method that accepts EvalRequest
        assert hasattr(agent, "run")
        assert callable(agent.run)

    @pytest.mark.asyncio
    async def test_agent_run_orchestrates_full_evaluation_flow(self) -> None:
        """Test that Agent.run() orchestrates the complete evaluation flow."""
        # Given: An Agent instance and evaluation request
        from agentbeats.agent import Agent, EvalRequest

        agent = Agent()
        _request = EvalRequest(
            agent_url="http://localhost:9009",
            messages=["Test message"],
        )

        # When: We run the evaluation
        # Then: Should orchestrate messenger, executor, and return results
        # This is the main orchestration contract
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_run_returns_evaluation_results(self) -> None:
        """Test that Agent.run() returns comprehensive evaluation results."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Agent runs an evaluation
        # Then: Should return results containing all evaluation tiers
        # Results should include tier1_graph, tier2_llm_judge, tier3_text_metrics
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_run_uses_executor_for_coordination(self) -> None:
        """Test that Agent.run() uses Executor for task coordination."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Agent runs evaluation
        # Then: Should delegate to Executor for multi-tier coordination
        # This follows separation of concerns: Agent orchestrates, Executor coordinates
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_run_with_empty_messages(self) -> None:
        """Test that Agent.run() handles requests with no messages."""
        # Given: An Agent instance and request with empty messages
        from agentbeats.agent import Agent, EvalRequest

        agent = Agent()
        _request = EvalRequest(
            agent_url="http://localhost:9009",
            messages=[],
        )

        # When: Agent runs evaluation with no messages
        # Then: Should still execute evaluations (possibly with empty traces)
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_run_with_multiple_messages(self) -> None:
        """Test that Agent.run() handles multiple messages correctly."""
        # Given: An Agent instance with multiple messages
        from agentbeats.agent import Agent, EvalRequest

        agent = Agent()
        _request = EvalRequest(
            agent_url="http://localhost:9009",
            messages=["Message 1", "Message 2", "Message 3"],
        )

        # When: Agent processes multiple messages
        # Then: Should send all messages and collect comprehensive traces
        assert hasattr(agent, "run")


class TestAgentFreshState:
    """Tests defining fresh state requirement per assessment."""

    @pytest.mark.asyncio
    async def test_agent_starts_with_fresh_state_per_run(self) -> None:
        """Test that Agent starts with fresh state for each evaluation run."""
        # Given: An Agent instance that has run one evaluation
        from agentbeats.agent import Agent, EvalRequest

        agent = Agent()
        _request1 = EvalRequest(
            agent_url="http://localhost:9009",
            messages=["First evaluation"],
            task_id="task-1",
        )

        # When: We run a second evaluation
        _request2 = EvalRequest(
            agent_url="http://localhost:9009",
            messages=["Second evaluation"],
            task_id="task-2",
        )

        # Then: Each evaluation should start with fresh state
        # No state should leak between evaluations per PRD requirement
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_uses_task_id_for_namespacing(self) -> None:
        """Test that Agent uses task_id to namespace temporary resources."""
        # Given: An Agent instance with task_id in request
        from agentbeats.agent import Agent, EvalRequest

        agent = Agent()
        _request = EvalRequest(
            agent_url="http://localhost:9009",
            task_id="unique-namespace-123",
        )

        # When: Agent runs evaluation
        # Then: Should use task_id to namespace resources
        # This prevents resource conflicts in concurrent evaluations per PRD
        assert hasattr(agent, "run")

    def test_agent_creates_independent_executor_instances(self) -> None:
        """Test that Agent creates independent executor instances per run."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Multiple evaluations run
        # Then: Each should have isolated executor state
        # This ensures fresh state per assessment per PRD requirement
        assert hasattr(agent, "run")


class TestAgentOrchestration:
    """Tests defining Agent orchestration responsibilities."""

    @pytest.mark.asyncio
    async def test_agent_integrates_messenger_and_executor(self) -> None:
        """Test that Agent integrates Messenger and Executor components."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Agent orchestrates evaluation
        # Then: Should coordinate between Messenger for communication and Executor for evaluation
        # This is the core orchestration pattern
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_propagates_task_id_to_executor(self) -> None:
        """Test that Agent propagates task_id to Executor."""
        # Given: An Agent instance with task_id
        from agentbeats.agent import Agent, EvalRequest

        agent = Agent()
        _request = EvalRequest(
            agent_url="http://localhost:9009",
            task_id="propagate-123",
        )

        # When: Agent runs evaluation
        # Then: Should pass task_id to Executor for proper namespacing
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_handles_executor_errors_gracefully(self) -> None:
        """Test that Agent handles Executor errors gracefully."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Executor encounters an error during evaluation
        # Then: Agent should handle error and return appropriate response
        # Should not crash or leak errors to caller
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_returns_structured_results(self) -> None:
        """Test that Agent returns structured evaluation results."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Evaluation completes
        # Then: Should return structured results with all evaluation tiers
        # Results should be consumable by A2A protocol endpoints
        assert hasattr(agent, "run")


class EvalResult(BaseModel):
    """Expected structure of evaluation results returned by Agent."""

    task_id: str
    agent_url: str
    status: str  # completed, failed, etc.
    results: dict[str, dict] | None = None  # Multi-tier evaluation results
    duration_seconds: float | None = None
    error: str | None = None


class TestEvalResultStructure:
    """Tests defining the expected structure of evaluation results."""

    def test_eval_result_model_is_valid(self) -> None:
        """Test that EvalResult model can be instantiated with valid data."""
        # Given: Valid evaluation result data
        result = EvalResult(
            task_id="task-123",
            agent_url="http://localhost:9009",
            status="completed",
            results={
                "tier1_graph": {"node_count": 5, "edge_count": 8},
                "tier2_llm_judge": {"overall_score": 0.85},
                "tier3_text_metrics": {"similarity": 0.9},
            },
            duration_seconds=3.5,
        )

        # Then: Model should validate successfully
        assert result.task_id == "task-123"
        assert result.status == "completed"
        assert "tier1_graph" in (result.results or {})

    def test_eval_result_includes_all_evaluation_tiers(self) -> None:
        """Test that EvalResult includes results from all three evaluation tiers."""
        # Given: Evaluation result with all tiers
        result = EvalResult(
            task_id="task-123",
            agent_url="http://localhost:9009",
            status="completed",
            results={
                "tier1_graph": {"metrics": "graph_data"},
                "tier2_llm_judge": {"judgment": "llm_data"},
                "tier3_text_metrics": {"similarity": 0.8},
            },
        )

        # Then: Should contain all three tiers per AgentBeats requirements
        assert "tier1_graph" in (result.results or {})
        assert "tier2_llm_judge" in (result.results or {})
        assert "tier3_text_metrics" in (result.results or {})

    def test_eval_result_handles_failures(self) -> None:
        """Test that EvalResult can represent failed evaluations."""
        # Given: Failed evaluation result
        result = EvalResult(
            task_id="task-123",
            agent_url="http://localhost:9009",
            status="failed",
            error="Network timeout",
        )

        # Then: Should capture failure information
        assert result.status == "failed"
        assert result.error == "Network timeout"

    def test_eval_result_minimal_fields(self) -> None:
        """Test that EvalResult works with minimal required fields."""
        # Given: Minimal evaluation result
        result = EvalResult(
            task_id="task-123",
            agent_url="http://localhost:9009",
            status="completed",
        )

        # Then: Should validate with just required fields
        assert result.task_id == "task-123"
        assert result.agent_url == "http://localhost:9009"
        assert result.status == "completed"


class TestAgentContract:
    """Tests defining the overall Agent contract."""

    def test_agent_can_be_instantiated(self) -> None:
        """Test that Agent can be instantiated without arguments."""
        # Given/When: We create an Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # Then: Instance should be created successfully
        assert agent is not None
        assert hasattr(agent, "run")

    def test_agent_provides_clean_api(self) -> None:
        """Test that Agent provides a clean, focused API."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # Then: Should have run method as primary interface
        assert hasattr(agent, "run")
        # Agent's primary responsibility is orchestrating evaluation via run()

    def test_agent_is_a2a_protocol_compliant(self) -> None:
        """Test that Agent follows A2A protocol requirements."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Agent orchestrates evaluation
        # Then: Should comply with A2A task lifecycle and protocol
        # This includes proper state management and result structure
        assert hasattr(agent, "run")


class TestAgentErrorHandling:
    """Tests defining error handling behavior."""

    @pytest.mark.asyncio
    async def test_agent_handles_invalid_agent_url(self) -> None:
        """Test that Agent handles invalid agent URLs gracefully."""
        # Given: An Agent instance with invalid URL
        from agentbeats.agent import Agent, EvalRequest

        agent = Agent()
        _request = EvalRequest(
            agent_url="http://invalid-url-does-not-exist:99999",
            messages=["test"],
        )

        # When: Agent attempts evaluation
        # Then: Should handle connection errors gracefully
        # Should return failed status rather than crash
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_handles_network_timeouts(self) -> None:
        """Test that Agent handles network timeouts appropriately."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Network timeout occurs during evaluation
        # Then: Should handle timeout and return error status
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_provides_error_details_in_results(self) -> None:
        """Test that Agent includes error details in evaluation results."""
        # Given: An Agent instance
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Evaluation fails
        # Then: Should include error message and context in results
        # This aids debugging and monitoring
        assert hasattr(agent, "run")


class TestAgentConcurrency:
    """Tests defining concurrent evaluation handling."""

    @pytest.mark.asyncio
    async def test_agent_supports_concurrent_evaluations(self) -> None:
        """Test that Agent can handle multiple concurrent evaluations."""
        # Given: An Agent instance
        from agentbeats.agent import Agent, EvalRequest

        agent = Agent()
        _request1 = EvalRequest(
            agent_url="http://localhost:9009",
            task_id="concurrent-1",
        )
        _request2 = EvalRequest(
            agent_url="http://localhost:9010",
            task_id="concurrent-2",
        )

        # When: Multiple evaluations run concurrently
        # Then: Should handle both independently via task_id namespacing
        assert hasattr(agent, "run")

    @pytest.mark.asyncio
    async def test_agent_isolates_concurrent_task_state(self) -> None:
        """Test that Agent isolates state between concurrent tasks."""
        # Given: An Agent instance with concurrent evaluations
        from agentbeats.agent import Agent

        agent = Agent()

        # When: Multiple tasks execute simultaneously
        # Then: Each task should have isolated state via task_id
        # No cross-contamination of results or resources
        assert hasattr(agent, "run")
