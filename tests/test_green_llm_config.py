"""Tests for LLM configuration defaults."""

from __future__ import annotations


def test_llm_config_default_base_url() -> None:
    """LLM config defaults to OpenAI base URL."""
    from green.evals.llm_judge import get_llm_config

    config = get_llm_config()
    assert config.base_url == "https://api.openai.com/v1"


def test_llm_config_default_model() -> None:
    """LLM config defaults to gpt-4o-mini."""
    from green.evals.llm_judge import get_llm_config

    config = get_llm_config()
    assert config.model == "gpt-4o-mini"
