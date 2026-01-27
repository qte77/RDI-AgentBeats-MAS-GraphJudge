"""Tests for STORY-004: OpenAI dependency configuration.

Validates that OpenAI client can be imported and is available.
"""


def test_openai_import():
    """Verify OpenAI client can be imported from openai package."""
    try:
        from openai import OpenAI  # noqa: F401
    except ImportError as e:
        raise AssertionError(f"Failed to import OpenAI: {e}") from e
