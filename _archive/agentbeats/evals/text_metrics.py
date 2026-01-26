"""Text metrics evaluator for response quality assessment."""

from __future__ import annotations

from pydantic import BaseModel


class TextMetricsResult(BaseModel):
    """Expected structure of text metrics evaluation result."""

    similarity_score: float  # 0-1 score
    response: str  # Original response text
    reference: str  # Reference text for comparison
    method: str | None = None  # Similarity method used
    details: dict[str, float] | None = None  # Additional metric details


class TextMetrics:
    """Evaluates text response quality using similarity metrics."""

    def __init__(self) -> None:
        """Initialize text metrics evaluator."""
        pass

    def evaluate(self, response: str, reference: str) -> TextMetricsResult:
        """Evaluate text similarity between response and reference.

        Args:
            response: The text to evaluate
            reference: The reference text to compare against

        Returns:
            TextMetricsResult with similarity score and metadata
        """
        # Handle empty strings
        if not response and not reference:
            # Both empty - perfect match
            return TextMetricsResult(
                similarity_score=1.0,
                response=response,
                reference=reference,
                method="exact",
                details={"token_overlap": 1.0, "length_ratio": 1.0},
            )

        if not response or not reference:
            # One is empty - no similarity
            return TextMetricsResult(
                similarity_score=0.0,
                response=response,
                reference=reference,
                method="exact",
                details={"token_overlap": 0.0, "length_ratio": 0.0},
            )

        # Handle identical strings
        if response == reference:
            return TextMetricsResult(
                similarity_score=1.0,
                response=response,
                reference=reference,
                method="exact",
                details={"token_overlap": 1.0, "length_ratio": 1.0},
            )

        # Normalize for case-insensitive comparison
        response_lower = response.lower()
        reference_lower = reference.lower()

        # Tokenize on whitespace
        response_tokens = set(response_lower.split())
        reference_tokens = set(reference_lower.split())

        # Calculate token overlap (Jaccard similarity)
        if response_tokens or reference_tokens:
            intersection = len(response_tokens & reference_tokens)
            union = len(response_tokens | reference_tokens)
            token_overlap = intersection / union if union > 0 else 0.0
        else:
            token_overlap = 1.0

        # Calculate length ratio (penalize extreme length differences)
        len_response = len(response)
        len_reference = len(reference)
        length_ratio = (
            min(len_response, len_reference) / max(len_response, len_reference)
            if max(len_response, len_reference) > 0
            else 1.0
        )

        # Combine token overlap and length ratio for overall similarity
        # Weight token overlap more heavily (0.7) than length (0.3)
        similarity_score = (0.7 * token_overlap) + (0.3 * length_ratio)

        # Ensure score is in [0, 1] range
        similarity_score = max(0.0, min(1.0, similarity_score))

        return TextMetricsResult(
            similarity_score=similarity_score,
            response=response,
            reference=reference,
            method="token_overlap",
            details={
                "token_overlap": token_overlap,
                "length_ratio": length_ratio,
            },
        )
