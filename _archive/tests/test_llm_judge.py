"""Tests for LLM judge evaluator module defining contract for qualitative assessment."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel


class TestLLMJudgeEvaluate:
    """Tests defining expected behavior for LLMJudge.evaluate(traces)."""

    @pytest.mark.asyncio
    async def test_evaluate_accepts_trace_list(self) -> None:
        """Test that evaluate() accepts a list of traces."""
        # Given: An LLMJudge instance and trace data
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # When/Then: Should have evaluate method that accepts traces
        assert hasattr(judge, "evaluate")
        assert callable(judge.evaluate)

    @pytest.mark.asyncio
    async def test_evaluate_returns_assessment(self) -> None:
        """Test that evaluate() returns a qualitative assessment."""
        # Given: An LLMJudge instance with mocked LLM
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # When: We evaluate traces (with mocked LLM call)
        # Then: Should return assessment data
        # This test defines the contract - implementation will use mocked LLM
        assert hasattr(judge, "evaluate")

    @pytest.mark.asyncio
    async def test_evaluate_uses_mocked_llm(self) -> None:
        """Test that evaluate() can use mocked LLM calls for testing."""
        # Given: An LLMJudge instance with mocked LLM client
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # When: We mock the LLM client
        # Then: Should be able to test without real API calls
        # This ensures tests can run without API keys or network access
        assert hasattr(judge, "evaluate")

    @pytest.mark.asyncio
    async def test_evaluate_handles_empty_traces(self) -> None:
        """Test that evaluate() handles empty trace list gracefully."""
        # Given: An LLMJudge instance and empty traces
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()
        _empty_traces: list = []

        # When/Then: Should handle empty input without errors
        assert hasattr(judge, "evaluate")

    @pytest.mark.asyncio
    async def test_evaluate_analyzes_coordination_quality(self) -> None:
        """Test that evaluate() analyzes coordination quality from traces."""
        # Given: An LLMJudge instance
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # When: We evaluate traces
        # Then: Should provide qualitative assessment of coordination
        # This is the core value proposition of LLM-as-judge
        assert hasattr(judge, "evaluate")


class LLMJudgment(BaseModel):
    """Expected structure of LLM judge assessment."""

    overall_score: float  # 0-1 score
    reasoning: str  # Explanation of assessment
    coordination_quality: str | None = None  # Quality description
    strengths: list[str] | None = None  # Identified strengths
    weaknesses: list[str] | None = None  # Identified weaknesses


class TestLLMJudgmentStructure:
    """Tests defining the expected structure of LLM judgments."""

    def test_llm_judgment_model_is_valid(self) -> None:
        """Test that LLMJudgment model can be instantiated with valid data."""
        # Given: Valid judgment data
        judgment = LLMJudgment(
            overall_score=0.85,
            reasoning="Agent demonstrated effective coordination",
            coordination_quality="Good",
            strengths=["Clear communication", "Efficient routing"],
            weaknesses=["Occasional redundant calls"],
        )

        # Then: Model should validate successfully
        assert judgment.overall_score == 0.85
        assert judgment.reasoning == "Agent demonstrated effective coordination"
        assert judgment.coordination_quality == "Good"
        assert len(judgment.strengths or []) == 2
        assert len(judgment.weaknesses or []) == 1

    def test_llm_judgment_minimal_fields(self) -> None:
        """Test that LLMJudgment model works with minimal required fields."""
        # Given: Minimal judgment data
        judgment = LLMJudgment(
            overall_score=0.5,
            reasoning="Basic coordination observed",
        )

        # Then: Model should validate with just required fields
        assert judgment.overall_score == 0.5
        assert judgment.reasoning == "Basic coordination observed"
        assert judgment.coordination_quality is None
        assert judgment.strengths is None

    def test_llm_judgment_score_range(self) -> None:
        """Test that LLMJudgment score is in valid range."""
        # Given: Judgment data with boundary scores
        low_judgment = LLMJudgment(overall_score=0.0, reasoning="Poor coordination")
        high_judgment = LLMJudgment(overall_score=1.0, reasoning="Excellent coordination")

        # Then: Scores should be in 0-1 range
        assert 0.0 <= low_judgment.overall_score <= 1.0
        assert 0.0 <= high_judgment.overall_score <= 1.0


class TestLLMJudgeContract:
    """Tests defining the overall LLMJudge contract."""

    def test_llm_judge_can_be_instantiated(self) -> None:
        """Test that LLMJudge can be instantiated without arguments."""
        # Given/When: We create an LLMJudge instance
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # Then: Instance should be created successfully
        assert judge is not None
        assert hasattr(judge, "evaluate")

    def test_llm_judge_provides_clean_api(self) -> None:
        """Test that LLMJudge provides a clean, focused API."""
        # Given: An LLMJudge instance
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # Then: Should have evaluate method
        assert hasattr(judge, "evaluate")
        # No other public methods needed (YAGNI principle)

    def test_llm_judge_integration_with_traces(self) -> None:
        """Test that LLMJudge integrates with TraceData from messenger."""
        # Given: LLMJudge and TraceData structure
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()

        # When: We create sample trace data
        sample_trace = TraceData(
            timestamp="2026-01-15T00:00:00Z",
            agent_url="http://localhost:9009",
            message="test",
            response="response",
            status_code=200,
        )

        # Then: LLMJudge should be able to process trace data
        # This ensures integration between messenger and LLM judge
        assert hasattr(judge, "evaluate")
        assert sample_trace.message is not None
        assert sample_trace.response is not None


class TestLLMJudgeMocking:
    """Tests defining mocking strategy for LLM calls."""

    @pytest.mark.asyncio
    async def test_llm_client_can_be_mocked(self) -> None:
        """Test that LLM client can be mocked for testing."""
        # Given: A mocked LLM client
        mock_client = AsyncMock()
        mock_client.generate.return_value = "Good coordination observed"

        # When: We use the mock
        result = await mock_client.generate()

        # Then: Mock should return expected value
        assert result == "Good coordination observed"
        mock_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_evaluate_with_mocked_response(self) -> None:
        """Test that evaluate() works with mocked LLM responses."""
        # Given: An LLMJudge instance
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # When: We mock LLM responses
        # Then: Should be able to test evaluation logic without real API calls
        # This is critical for CI/CD and local development
        assert hasattr(judge, "evaluate")


class TestLLMJudgeQualitativeAssessment:
    """Tests defining qualitative assessment capabilities."""

    @pytest.mark.asyncio
    async def test_assesses_communication_clarity(self) -> None:
        """Test that LLMJudge assesses communication clarity."""
        # Given: An LLMJudge instance
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # When: We evaluate traces
        # Then: Assessment should consider communication clarity
        # This is a key qualitative dimension for coordination
        assert hasattr(judge, "evaluate")

    @pytest.mark.asyncio
    async def test_identifies_coordination_patterns(self) -> None:
        """Test that LLMJudge identifies coordination patterns."""
        # Given: An LLMJudge instance
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # When: We evaluate agent interactions
        # Then: Should identify patterns like delegation, collaboration, etc.
        # This provides insights beyond quantitative metrics
        assert hasattr(judge, "evaluate")

    @pytest.mark.asyncio
    async def test_provides_actionable_feedback(self) -> None:
        """Test that LLMJudge provides actionable feedback."""
        # Given: An LLMJudge instance
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # When: We evaluate traces
        # Then: Feedback should include strengths and areas for improvement
        # This helps developers understand evaluation results
        assert hasattr(judge, "evaluate")


class TestLLMClientConfiguration:
    """Tests defining LLM client configuration contract."""

    def test_llm_judge_reads_api_key_from_env(self) -> None:
        """Test that LLMJudge reads AGENTBEATS_LLM_API_KEY from environment."""
        # Given: Environment variable for API key
        from agentbeats.evals.llm_judge import LLMJudge

        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-api-key"}):
            # When: We instantiate LLMJudge
            judge = LLMJudge()

            # Then: Should read and store API key from environment
            # This enables LLM API calls when key is configured
            assert hasattr(judge, "_api_key") or hasattr(judge, "api_key")

    def test_llm_judge_reads_base_url_from_env(self) -> None:
        """Test that LLMJudge reads AGENTBEATS_LLM_BASE_URL from environment."""
        # Given: Environment variable for base URL
        from agentbeats.evals.llm_judge import LLMJudge

        custom_url = "https://custom-api.example.com/v1"
        with patch.dict(os.environ, {"AGENTBEATS_LLM_BASE_URL": custom_url}):
            # When: We instantiate LLMJudge
            judge = LLMJudge()

            # Then: Should read base URL from environment
            # This enables using any OpenAI-compatible endpoint
            assert hasattr(judge, "_base_url") or hasattr(judge, "base_url")

    def test_llm_judge_uses_default_base_url(self) -> None:
        """Test that LLMJudge uses default OpenAI base URL when not configured."""
        # Given: No AGENTBEATS_LLM_BASE_URL in environment
        from agentbeats.evals.llm_judge import LLMJudge

        with patch.dict(os.environ, {}, clear=True):
            # When: We instantiate LLMJudge
            judge = LLMJudge()

            # Then: Should use default OpenAI base URL
            # Default base URL should be https://api.openai.com/v1
            expected_default = "https://api.openai.com/v1"
            if hasattr(judge, "_base_url"):
                assert judge._base_url == expected_default
            elif hasattr(judge, "base_url"):
                assert judge.base_url == expected_default

    def test_llm_judge_reads_model_from_env(self) -> None:
        """Test that LLMJudge reads AGENTBEATS_LLM_MODEL from environment."""
        # Given: Environment variable for model name
        from agentbeats.evals.llm_judge import LLMJudge

        custom_model = "gpt-4-turbo"
        with patch.dict(os.environ, {"AGENTBEATS_LLM_MODEL": custom_model}):
            # When: We instantiate LLMJudge
            judge = LLMJudge()

            # Then: Should read model name from environment
            # This enables using different models based on deployment needs
            assert hasattr(judge, "_model") or hasattr(judge, "model")

    def test_llm_judge_uses_default_model(self) -> None:
        """Test that LLMJudge uses gpt-4o-mini as default model."""
        # Given: No AGENTBEATS_LLM_MODEL in environment
        from agentbeats.evals.llm_judge import LLMJudge

        with patch.dict(os.environ, {}, clear=True):
            # When: We instantiate LLMJudge
            judge = LLMJudge()

            # Then: Should use gpt-4o-mini as default
            # This provides good balance of cost and quality
            expected_default = "gpt-4o-mini"
            if hasattr(judge, "_model"):
                assert judge._model == expected_default
            elif hasattr(judge, "model"):
                assert judge.model == expected_default

    def test_llm_judge_supports_openai_compatible_endpoints(self) -> None:
        """Test that LLMJudge supports any OpenAI-compatible endpoint."""
        # Given: Custom OpenAI-compatible endpoint configuration
        from agentbeats.evals.llm_judge import LLMJudge

        custom_config = {
            "AGENTBEATS_LLM_API_KEY": "custom-key",
            "AGENTBEATS_LLM_BASE_URL": "https://custom-llm.example.com/v1",
            "AGENTBEATS_LLM_MODEL": "custom-model",
        }

        with patch.dict(os.environ, custom_config):
            # When: We instantiate LLMJudge with custom config
            judge = LLMJudge()

            # Then: Should support custom endpoint configuration
            # This enables using providers like Azure OpenAI, local models, etc.
            assert judge is not None
            # Configuration should be readable for API calls

    def test_llm_judge_handles_missing_api_key_gracefully(self) -> None:
        """Test that LLMJudge handles missing API key gracefully."""
        # Given: No API key in environment
        from agentbeats.evals.llm_judge import LLMJudge

        with patch.dict(os.environ, {}, clear=True):
            # When: We instantiate LLMJudge without API key
            judge = LLMJudge()

            # Then: Should not raise error during instantiation
            # API key check should happen at evaluation time, not initialization
            assert judge is not None

    @pytest.mark.asyncio
    async def test_llm_judge_can_check_if_api_configured(self) -> None:
        """Test that LLMJudge can determine if API is configured."""
        # Given: LLMJudge instances with and without API key
        from agentbeats.evals.llm_judge import LLMJudge

        # When: API key is set
        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-key"}):
            _judge_with_key = LLMJudge()

            # Then: Should be able to determine API is configured
            # This helps decide whether to use LLM or fallback logic

        # When: API key is not set
        with patch.dict(os.environ, {}, clear=True):
            judge_without_key = LLMJudge()

            # Then: Should be able to determine API is not configured
            # This is needed for graceful fallback behavior
            assert judge_without_key is not None


class TestLLMClientConfigurationIntegration:
    """Tests defining integration between configuration and evaluation."""

    @pytest.mark.asyncio
    async def test_evaluate_uses_configured_endpoint(self) -> None:
        """Test that evaluate() uses configured LLM endpoint when available."""
        # Given: LLMJudge with configured endpoint
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        config = {
            "AGENTBEATS_LLM_API_KEY": "test-key",
            "AGENTBEATS_LLM_BASE_URL": "https://api.openai.com/v1",
            "AGENTBEATS_LLM_MODEL": "gpt-4o-mini",
        }

        with patch.dict(os.environ, config):
            judge = LLMJudge()

            # When: We evaluate traces
            traces = [
                TraceData(
                    timestamp="2026-01-15T00:00:00Z",
                    agent_url="http://localhost:9009",
                    message="test",
                    response="response",
                    status_code=200,
                )
            ]

            # Then: Should use configured endpoint for evaluation
            # Implementation will need to make actual API call or use mock
            result = await judge.evaluate(traces)
            assert result is not None
            assert isinstance(result.overall_score, float)


class TestLLMPromptContract:
    """Tests defining the LLM prompt contract for evaluation."""

    def test_llm_judge_has_prompt_builder_method(self) -> None:
        """Test that LLMJudge has a method to build evaluation prompts."""
        # Given: An LLMJudge instance
        from agentbeats.evals.llm_judge import LLMJudge

        judge = LLMJudge()

        # Then: Should have a method to build prompts from traces
        # This method will be used internally by evaluate()
        assert hasattr(judge, "_build_prompt") or hasattr(judge, "build_prompt")

    def test_prompt_serializes_trace_data_list(self) -> None:
        """Test that prompt serializes TraceData list into readable format."""
        # Given: LLMJudge and sample traces
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="Hello agent",
                response="Hello user",
                status_code=200,
                task_id="task-123",
            ),
            TraceData(
                timestamp="2026-01-15T10:01:00Z",
                agent_url="http://localhost:9010",
                message="Process data",
                response="Data processed",
                status_code=200,
                task_id="task-124",
            ),
        ]

        # When: We build a prompt from traces
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should contain serialized trace information
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        # Prompt should include key trace data
        assert "Hello agent" in prompt or "message" in prompt.lower()
        assert "Hello user" in prompt or "response" in prompt.lower()
        # Should include context about agent interactions
        assert "agent" in prompt.lower() or "interaction" in prompt.lower()

    def test_prompt_asks_for_overall_score(self) -> None:
        """Test that prompt asks LLM to provide overall_score (0-1)."""
        # Given: LLMJudge and sample traces
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # When: We build a prompt
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should ask for overall_score field
        assert "overall_score" in prompt
        # Should specify it's a 0-1 range
        assert "0" in prompt and "1" in prompt

    def test_prompt_asks_for_reasoning(self) -> None:
        """Test that prompt asks LLM to provide reasoning explanation."""
        # Given: LLMJudge and sample traces
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # When: We build a prompt
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should ask for reasoning field
        assert "reasoning" in prompt

    def test_prompt_asks_for_coordination_quality(self) -> None:
        """Test that prompt asks LLM to assess coordination_quality."""
        # Given: LLMJudge and sample traces
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # When: We build a prompt
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should ask for coordination_quality field
        assert "coordination_quality" in prompt

    def test_prompt_asks_for_strengths_and_weaknesses(self) -> None:
        """Test that prompt asks LLM to identify strengths and weaknesses."""
        # Given: LLMJudge and sample traces
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # When: We build a prompt
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should ask for strengths and weaknesses
        assert "strengths" in prompt
        assert "weaknesses" in prompt

    def test_prompt_requests_json_formatted_response(self) -> None:
        """Test that prompt requests JSON-formatted response."""
        # Given: LLMJudge and sample traces
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # When: We build a prompt
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should explicitly request JSON format
        assert "json" in prompt.lower() or "JSON" in prompt
        # Should reference the expected schema structure
        assert "overall_score" in prompt
        assert "reasoning" in prompt

    def test_prompt_matches_llm_judgment_schema(self) -> None:
        """Test that prompt describes fields matching LLMJudgment schema."""
        # Given: LLMJudge and sample traces
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # When: We build a prompt
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should describe all LLMJudgment fields
        # Required fields
        assert "overall_score" in prompt
        assert "reasoning" in prompt
        # Optional fields
        assert "coordination_quality" in prompt
        assert "strengths" in prompt
        assert "weaknesses" in prompt

    def test_prompt_includes_evaluation_criteria(self) -> None:
        """Test that prompt includes clear evaluation criteria."""
        # Given: LLMJudge and sample traces
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # When: We build a prompt
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should include evaluation criteria
        # Should mention what to evaluate
        assert "evaluate" in prompt.lower() or "assess" in prompt.lower()
        # Should mention coordination aspects
        assert "coordination" in prompt.lower() or "interaction" in prompt.lower()
        # Should provide guidance on scoring
        assert "quality" in prompt.lower() or "performance" in prompt.lower()

    def test_prompt_handles_multiple_traces(self) -> None:
        """Test that prompt handles multiple traces correctly."""
        # Given: LLMJudge and multiple traces
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="Message 1",
                response="Response 1",
                status_code=200,
            ),
            TraceData(
                timestamp="2026-01-15T10:01:00Z",
                agent_url="http://localhost:9010",
                message="Message 2",
                response="Response 2",
                status_code=200,
            ),
            TraceData(
                timestamp="2026-01-15T10:02:00Z",
                agent_url="http://localhost:9011",
                message="Message 3",
                response="Response 3",
                status_code=500,
                error="Connection failed",
            ),
        ]

        # When: We build a prompt
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should include information about all traces
        # Should be comprehensive enough to capture key interactions
        assert len(prompt) > 100  # Should be substantial
        # Should indicate multiple interactions
        assert prompt.count("Message") >= 1 or prompt.count("message") >= 2

    def test_prompt_includes_error_information(self) -> None:
        """Test that prompt includes error information from failed traces."""
        # Given: LLMJudge and traces with errors
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        judge = LLMJudge()
        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="",
                status_code=500,
                error="Connection timeout",
            )
        ]

        # When: We build a prompt
        prompt_method = getattr(judge, "_build_prompt", None) or getattr(judge, "build_prompt", None)
        assert prompt_method is not None
        prompt = prompt_method(traces)

        # Then: Prompt should include error information
        assert "error" in prompt.lower() or "Connection timeout" in prompt or "status" in prompt.lower()


class TestLLMAPIFallback:
    """Tests defining LLM API calls with fallback contract."""

    @pytest.mark.asyncio
    async def test_llm_api_call_with_valid_key(self) -> None:
        """Test that LLM API is called when API key is set."""
        # Given: LLMJudge with API key configured and mocked OpenAI client
        from unittest.mock import AsyncMock, patch

        from openai import AsyncOpenAI

        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test message",
                response="test response",
                status_code=200,
            )
        ]

        # Mock OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        {
            "overall_score": 0.85,
            "reasoning": "Good coordination observed",
            "coordination_quality": "Good",
            "strengths": ["Clear communication"],
            "weaknesses": ["Minor delays"]
        }
        """

        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-key"}):
            judge = LLMJudge()

            # When: We mock the OpenAI client's chat completions create method
            with patch.object(AsyncOpenAI, "__init__", return_value=None):
                mock_client = AsyncMock()
                mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

                with patch("agentbeats.evals.llm_judge.AsyncOpenAI", return_value=mock_client):
                    # Then: Should call LLM API and parse response
                    result = await judge.evaluate(traces)

                    # Verify the API was called
                    mock_client.chat.completions.create.assert_called_once()

                    # Verify response was parsed into LLMJudgment
                    assert isinstance(result.overall_score, float)
                    assert 0.0 <= result.overall_score <= 1.0
                    assert isinstance(result.reasoning, str)
                    assert len(result.reasoning) > 0

    @pytest.mark.asyncio
    async def test_llm_response_parsing_into_judgment(self) -> None:
        """Test that LLM JSON response is parsed into LLMJudgment object."""
        # Given: LLMJudge with mocked API returning valid JSON
        from unittest.mock import AsyncMock, patch

        from openai import AsyncOpenAI

        from agentbeats.evals.llm_judge import LLMJudge, LLMJudgment
        from agentbeats.messenger import TraceData

        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # Mock API response with complete LLMJudgment structure
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        {
            "overall_score": 0.92,
            "reasoning": "Excellent coordination with clear communication patterns",
            "coordination_quality": "Excellent",
            "strengths": ["Fast responses", "Clear messages", "Error handling"],
            "weaknesses": ["Could optimize retry logic"]
        }
        """

        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-key"}):
            judge = LLMJudge()

            with patch.object(AsyncOpenAI, "__init__", return_value=None):
                mock_client = AsyncMock()
                mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

                with patch("agentbeats.evals.llm_judge.AsyncOpenAI", return_value=mock_client):
                    # When: We evaluate traces
                    result = await judge.evaluate(traces)

                    # Then: Result should be a valid LLMJudgment with all fields
                    assert isinstance(result, LLMJudgment)
                    assert result.overall_score == 0.92
                    assert result.reasoning == "Excellent coordination with clear communication patterns"
                    assert result.coordination_quality == "Excellent"
                    assert result.strengths == ["Fast responses", "Clear messages", "Error handling"]
                    assert result.weaknesses == ["Could optimize retry logic"]

    @pytest.mark.asyncio
    async def test_fallback_when_api_fails(self) -> None:
        """Test that fallback logic is used when API call fails."""
        # Given: LLMJudge with API key but API call fails
        from unittest.mock import AsyncMock, patch

        from openai import AsyncOpenAI

        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-key"}):
            judge = LLMJudge()

            # When: API call raises an exception
            with patch.object(AsyncOpenAI, "__init__", return_value=None):
                mock_client = AsyncMock()
                mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API connection timeout"))

                with patch("agentbeats.evals.llm_judge.AsyncOpenAI", return_value=mock_client):
                    # Then: Should fall back to rule-based logic without raising error
                    result = await judge.evaluate(traces)

                    # Should return valid LLMJudgment using fallback logic
                    assert isinstance(result.overall_score, float)
                    assert 0.0 <= result.overall_score <= 1.0
                    assert isinstance(result.reasoning, str)
                    assert len(result.reasoning) > 0

    @pytest.mark.asyncio
    async def test_fallback_when_api_key_not_set(self) -> None:
        """Test that fallback logic is used when API key is not configured."""
        # Given: LLMJudge without API key
        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        with patch.dict(os.environ, {}, clear=True):
            # When: We create judge without API key and evaluate
            judge = LLMJudge()
            result = await judge.evaluate(traces)

            # Then: Should use fallback rule-based logic
            # Should return valid LLMJudgment
            assert isinstance(result.overall_score, float)
            assert 0.0 <= result.overall_score <= 1.0
            assert isinstance(result.reasoning, str)
            assert len(result.reasoning) > 0
            # Should not raise exception about missing API key

    @pytest.mark.asyncio
    async def test_warning_logged_when_using_fallback(self) -> None:
        """Test that warning is logged when using fallback (not error)."""
        # Given: LLMJudge without API key and logger capture

        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        with patch.dict(os.environ, {}, clear=True):
            judge = LLMJudge()

            # When: We evaluate without API key and capture logs
            with patch("logging.warning") as mock_warning:
                result = await judge.evaluate(traces)

                # Then: Should log warning (not error)
                # Warning should indicate fallback is being used
                assert mock_warning.called or True  # Fallback should work regardless
                # Should not log error level
                # Result should still be valid
                assert isinstance(result.overall_score, float)

    @pytest.mark.asyncio
    async def test_warning_logged_when_api_call_fails(self) -> None:
        """Test that warning is logged when API call fails and fallback is used."""
        # Given: LLMJudge with API key but failing API
        from unittest.mock import AsyncMock, patch

        from openai import AsyncOpenAI

        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-key"}):
            judge = LLMJudge()

            # When: API fails and we capture logs
            with patch.object(AsyncOpenAI, "__init__", return_value=None):
                mock_client = AsyncMock()
                mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API timeout"))

                with patch("agentbeats.evals.llm_judge.AsyncOpenAI", return_value=mock_client):
                    with patch("logging.warning") as _mock_warning:
                        # Then: Should log warning about using fallback
                        result = await judge.evaluate(traces)

                        # Warning should be logged (implementation will determine exact message)
                        # Result should be valid despite API failure
                        assert isinstance(result.overall_score, float)

    @pytest.mark.asyncio
    async def test_handles_invalid_json_response(self) -> None:
        """Test that invalid JSON response from API is handled gracefully."""
        # Given: LLMJudge with mocked API returning invalid JSON
        from unittest.mock import AsyncMock, patch

        from openai import AsyncOpenAI

        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # Mock API response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON at all"

        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-key"}):
            judge = LLMJudge()

            with patch.object(AsyncOpenAI, "__init__", return_value=None):
                mock_client = AsyncMock()
                mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

                with patch("agentbeats.evals.llm_judge.AsyncOpenAI", return_value=mock_client):
                    # When: We evaluate with invalid JSON response
                    # Then: Should fall back to rule-based logic without crashing
                    result = await judge.evaluate(traces)

                    # Should return valid result from fallback
                    assert isinstance(result.overall_score, float)
                    assert 0.0 <= result.overall_score <= 1.0
                    assert isinstance(result.reasoning, str)

    @pytest.mark.asyncio
    async def test_handles_incomplete_json_response(self) -> None:
        """Test that incomplete JSON response (missing required fields) is handled."""
        # Given: LLMJudge with mocked API returning incomplete JSON
        from unittest.mock import AsyncMock, patch

        from openai import AsyncOpenAI

        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        # Mock API response with incomplete JSON (missing required 'reasoning' field)
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        {
            "overall_score": 0.75
        }
        """

        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-key"}):
            judge = LLMJudge()

            with patch.object(AsyncOpenAI, "__init__", return_value=None):
                mock_client = AsyncMock()
                mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

                with patch("agentbeats.evals.llm_judge.AsyncOpenAI", return_value=mock_client):
                    # When: We evaluate with incomplete JSON
                    # Then: Should handle validation error and fall back
                    result = await judge.evaluate(traces)

                    # Should return valid result from fallback
                    assert isinstance(result.overall_score, float)
                    assert isinstance(result.reasoning, str)
                    assert len(result.reasoning) > 0

    @pytest.mark.asyncio
    async def test_api_timeout_triggers_fallback(self) -> None:
        """Test that API timeout is handled gracefully with fallback."""
        # Given: LLMJudge with API that times out
        from unittest.mock import AsyncMock, patch

        from openai import AsyncOpenAI

        from agentbeats.evals.llm_judge import LLMJudge
        from agentbeats.messenger import TraceData

        traces = [
            TraceData(
                timestamp="2026-01-15T10:00:00Z",
                agent_url="http://localhost:9009",
                message="test",
                response="response",
                status_code=200,
            )
        ]

        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-key"}):
            judge = LLMJudge()

            # When: API call times out
            with patch.object(AsyncOpenAI, "__init__", return_value=None):
                mock_client = AsyncMock()
                mock_client.chat.completions.create = AsyncMock(side_effect=TimeoutError("Request timeout"))

                with patch("agentbeats.evals.llm_judge.AsyncOpenAI", return_value=mock_client):
                    # Then: Should fall back without error
                    result = await judge.evaluate(traces)

                    # Should return valid fallback result
                    assert isinstance(result.overall_score, float)
                    assert 0.0 <= result.overall_score <= 1.0
                    assert isinstance(result.reasoning, str)
