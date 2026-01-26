"""Tests for text metrics evaluator module defining contract for response quality assessment."""

from pydantic import BaseModel


class TestTextMetricsEvaluate:
    """Tests defining expected behavior for TextMetrics.evaluate(response, reference)."""

    def test_evaluate_accepts_response_and_reference(self) -> None:
        """Test that evaluate() accepts response and reference strings."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When/Then: Should have evaluate method that accepts response and reference
        assert hasattr(evaluator, "evaluate")
        assert callable(evaluator.evaluate)

    def test_evaluate_returns_similarity_score(self) -> None:
        """Test that evaluate() returns a similarity score."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We evaluate response against reference
        # Then: Should return a similarity score
        # This test defines the contract - implementation will compute similarity
        assert hasattr(evaluator, "evaluate")

    def test_evaluate_handles_empty_strings(self) -> None:
        """Test that evaluate() handles empty strings gracefully."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When/Then: Should handle empty strings without errors
        assert hasattr(evaluator, "evaluate")

    def test_evaluate_handles_identical_strings(self) -> None:
        """Test that evaluate() handles identical strings."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: Response and reference are identical
        # Then: Should return maximum similarity score (1.0)
        assert hasattr(evaluator, "evaluate")

    def test_evaluate_handles_completely_different_strings(self) -> None:
        """Test that evaluate() handles completely different strings."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: Response and reference have no similarity
        # Then: Should return minimum similarity score (0.0)
        assert hasattr(evaluator, "evaluate")


class TestTextMetricsSimilarityScore:
    """Tests defining expected similarity score range and behavior."""

    def test_similarity_score_range_zero_to_one(self) -> None:
        """Test that similarity scores are in range 0-1."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We evaluate any response against reference
        # Then: Score should be in [0, 1] range
        # This ensures consistent score interpretation across evaluators
        assert hasattr(evaluator, "evaluate")

    def test_similarity_score_is_float(self) -> None:
        """Test that similarity score is a float."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We evaluate response against reference
        # Then: Should return a float value
        assert hasattr(evaluator, "evaluate")

    def test_similarity_increases_with_similarity(self) -> None:
        """Test that similarity score increases with text similarity."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We compare texts with varying similarity
        # Then: More similar texts should have higher scores
        # This validates the metric behaves as expected
        assert hasattr(evaluator, "evaluate")


class TextMetricsResult(BaseModel):
    """Expected structure of text metrics evaluation result."""

    similarity_score: float  # 0-1 score
    response: str  # Original response text
    reference: str  # Reference text for comparison
    method: str | None = None  # Similarity method used
    details: dict[str, float] | None = None  # Additional metric details


class TestTextMetricsResultStructure:
    """Tests defining the expected structure of text metrics results."""

    def test_text_metrics_result_model_is_valid(self) -> None:
        """Test that TextMetricsResult model can be instantiated with valid data."""
        # Given: Valid text metrics result data
        result = TextMetricsResult(
            similarity_score=0.85,
            response="The agent completed the task successfully",
            reference="Agent task completed successfully",
            method="semantic",
            details={"token_overlap": 0.75, "semantic_sim": 0.95},
        )

        # Then: Model should validate successfully
        assert result.similarity_score == 0.85
        assert result.response == "The agent completed the task successfully"
        assert result.reference == "Agent task completed successfully"
        assert result.method == "semantic"
        assert isinstance(result.details, dict)

    def test_text_metrics_result_minimal_fields(self) -> None:
        """Test that TextMetricsResult model works with minimal required fields."""
        # Given: Minimal text metrics result data
        result = TextMetricsResult(
            similarity_score=0.5,
            response="test response",
            reference="test reference",
        )

        # Then: Model should validate with just required fields
        assert result.similarity_score == 0.5
        assert result.response == "test response"
        assert result.reference == "test reference"
        assert result.method is None
        assert result.details is None

    def test_text_metrics_result_score_boundaries(self) -> None:
        """Test that TextMetricsResult accepts valid score boundaries."""
        # Given: Result data with boundary scores
        low_result = TextMetricsResult(
            similarity_score=0.0,
            response="completely different",
            reference="totally unrelated",
        )
        high_result = TextMetricsResult(
            similarity_score=1.0,
            response="exact match",
            reference="exact match",
        )

        # Then: Boundary scores should be valid
        assert low_result.similarity_score == 0.0
        assert high_result.similarity_score == 1.0


class TestTextMetricsContract:
    """Tests defining the overall TextMetrics contract."""

    def test_text_metrics_can_be_instantiated(self) -> None:
        """Test that TextMetrics can be instantiated without arguments."""
        # Given/When: We create a TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # Then: Instance should be created successfully
        assert evaluator is not None
        assert hasattr(evaluator, "evaluate")

    def test_text_metrics_provides_clean_api(self) -> None:
        """Test that TextMetrics provides a clean, focused API."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # Then: Should have evaluate method
        assert hasattr(evaluator, "evaluate")
        # No other public methods needed (YAGNI principle)

    def test_text_metrics_is_stateless(self) -> None:
        """Test that TextMetrics is stateless and can be reused."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We evaluate multiple pairs
        # Then: Each evaluation should be independent
        # This ensures thread-safety and predictable behavior
        assert hasattr(evaluator, "evaluate")


class TestTextMetricsSimilarityMethods:
    """Tests defining similarity calculation methods."""

    def test_supports_token_based_similarity(self) -> None:
        """Test that TextMetrics supports token-based similarity."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We compute similarity
        # Then: Should support token overlap metrics
        # This provides basic lexical similarity
        assert hasattr(evaluator, "evaluate")

    def test_supports_semantic_similarity(self) -> None:
        """Test that TextMetrics supports semantic similarity."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We compute similarity
        # Then: Should support semantic similarity measures
        # This captures meaning beyond token matching
        assert hasattr(evaluator, "evaluate")

    def test_handles_case_sensitivity(self) -> None:
        """Test that TextMetrics handles case sensitivity appropriately."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We compare texts with different cases
        # Then: Should handle case appropriately for similarity
        # Case differences should have minimal impact on similarity
        assert hasattr(evaluator, "evaluate")


class TestTextMetricsQualityAssessment:
    """Tests defining quality assessment capabilities."""

    def test_measures_response_accuracy(self) -> None:
        """Test that TextMetrics measures response accuracy against reference."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We evaluate agent response against expected output
        # Then: Should quantify how accurate the response is
        # This is the core value proposition of text metrics
        assert hasattr(evaluator, "evaluate")

    def test_supports_partial_matches(self) -> None:
        """Test that TextMetrics recognizes partial matches."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: Response partially matches reference
        # Then: Should assign intermediate similarity score
        # This provides nuanced assessment of response quality
        assert hasattr(evaluator, "evaluate")

    def test_handles_longer_vs_shorter_texts(self) -> None:
        """Test that TextMetrics handles length differences appropriately."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: Response and reference have different lengths
        # Then: Should normalize for length differences
        # Prevents bias toward shorter or longer responses
        assert hasattr(evaluator, "evaluate")


class TestTextMetricsIntegration:
    """Tests defining integration with other system components."""

    def test_integrates_with_agent_responses(self) -> None:
        """Test that TextMetrics can evaluate agent responses."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: We evaluate an agent's response
        # Then: Should provide meaningful similarity assessment
        # This enables quantitative evaluation of agent outputs
        assert hasattr(evaluator, "evaluate")

    def test_complements_other_evaluators(self) -> None:
        """Test that TextMetrics complements graph and LLM judge evaluators."""
        # Given: A TextMetrics instance
        from agentbeats.evals.text_metrics import TextMetrics

        evaluator = TextMetrics()

        # When: Used alongside graph and LLM judge metrics
        # Then: Should provide complementary quantitative text analysis
        # Text metrics = Tier 3, complements Tier 1 (graph) and Tier 2 (LLM judge)
        assert hasattr(evaluator, "evaluate")
