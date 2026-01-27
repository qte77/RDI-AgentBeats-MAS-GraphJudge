"""Tests for LLM client configuration with environment variables."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def clean_env() -> None:
    """Clean environment variables before each test."""
    env_vars = ["AGENTBEATS_LLM_API_KEY", "AGENTBEATS_LLM_BASE_URL", "AGENTBEATS_LLM_MODEL"]
    for var in env_vars:
        os.environ.pop(var, None)


def test_llm_config_reads_api_key_from_env() -> None:
    """Test that LLM config reads API key from AGENTBEATS_LLM_API_KEY environment variable."""
    from green.evals.llm_judge import get_llm_config

    with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-api-key"}):
        config = get_llm_config()
        assert config.api_key == "test-api-key"


def test_llm_config_reads_base_url_from_env() -> None:
    """Test that LLM config reads base URL from AGENTBEATS_LLM_BASE_URL environment variable."""
    from green.evals.llm_judge import get_llm_config

    with patch.dict(os.environ, {"AGENTBEATS_LLM_BASE_URL": "https://custom.api.com/v1"}):
        config = get_llm_config()
        assert config.base_url == "https://custom.api.com/v1"


def test_llm_config_reads_model_from_env() -> None:
    """Test that LLM config reads model from AGENTBEATS_LLM_MODEL environment variable."""
    from green.evals.llm_judge import get_llm_config

    with patch.dict(os.environ, {"AGENTBEATS_LLM_MODEL": "gpt-4o"}):
        config = get_llm_config()
        assert config.model == "gpt-4o"


def test_llm_config_default_base_url() -> None:
    """Test that LLM config defaults to OpenAI base URL when AGENTBEATS_LLM_BASE_URL not set."""
    from green.evals.llm_judge import get_llm_config

    config = get_llm_config()
    assert config.base_url == "https://api.openai.com/v1"


def test_llm_config_default_model() -> None:
    """Test that LLM config defaults to gpt-4o-mini when AGENTBEATS_LLM_MODEL not set."""
    from green.evals.llm_judge import get_llm_config

    config = get_llm_config()
    assert config.model == "gpt-4o-mini"


def test_llm_config_supports_openai_compatible_endpoint() -> None:
    """Test that LLM config supports any OpenAI-compatible endpoint."""
    from green.evals.llm_judge import get_llm_config

    # Test with various OpenAI-compatible endpoints
    test_endpoints = [
        "https://api.openai.com/v1",
        "https://api.anthropic.com/v1",
        "https://localhost:8000/v1",
        "https://custom-llm-service.company.com/v1",
    ]

    for endpoint in test_endpoints:
        with patch.dict(os.environ, {"AGENTBEATS_LLM_BASE_URL": endpoint}):
            config = get_llm_config()
            assert config.base_url == endpoint


def test_llm_config_api_key_optional() -> None:
    """Test that LLM config allows API key to be optional (for local endpoints)."""
    from green.evals.llm_judge import get_llm_config

    config = get_llm_config()
    # API key can be None for local/auth-free endpoints
    assert config.api_key is None or isinstance(config.api_key, str)


def test_llm_config_all_environment_variables() -> None:
    """Test that LLM config reads all environment variables together."""
    from green.evals.llm_judge import get_llm_config

    with patch.dict(
        os.environ,
        {
            "AGENTBEATS_LLM_API_KEY": "full-test-key",
            "AGENTBEATS_LLM_BASE_URL": "https://full-test.api.com/v1",
            "AGENTBEATS_LLM_MODEL": "gpt-4o",
        },
    ):
        config = get_llm_config()
        assert config.api_key == "full-test-key"
        assert config.base_url == "https://full-test.api.com/v1"
        assert config.model == "gpt-4o"
