"""Tests for common LLM settings and client factory.

Validates:
- LLMSettings class with environment variable support
- create_llm_client() factory function
- Backward compatibility with green agent settings
"""

import os
from unittest.mock import patch

import pytest
from openai import AsyncOpenAI

from common.llm_client import create_llm_client
from common.settings import LLMSettings


class TestLLMSettings:
    """Test suite for LLMSettings class."""

    def test_default_values(self):
        """LLMSettings should have correct default values."""
        settings = LLMSettings()
        assert settings.api_key is None
        assert settings.base_url == "https://api.openai.com/v1"
        assert settings.model == "gpt-4o-mini"
        assert settings.temperature == 0.0

    def test_env_var_api_key(self):
        """LLMSettings should read API key from environment."""
        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "test-key-123"}):
            settings = LLMSettings()
            assert settings.api_key == "test-key-123"

    def test_env_var_base_url(self):
        """LLMSettings should read base URL from environment."""
        with patch.dict(os.environ, {"AGENTBEATS_LLM_BASE_URL": "https://custom.api.com"}):
            settings = LLMSettings()
            assert settings.base_url == "https://custom.api.com"

    def test_env_var_model(self):
        """LLMSettings should read model from environment."""
        with patch.dict(os.environ, {"AGENTBEATS_LLM_MODEL": "gpt-4"}):
            settings = LLMSettings()
            assert settings.model == "gpt-4"

    def test_env_var_temperature(self):
        """LLMSettings should read temperature from environment."""
        with patch.dict(os.environ, {"AGENTBEATS_LLM_TEMPERATURE": "0.7"}):
            settings = LLMSettings()
            assert settings.temperature == 0.7

    def test_all_env_vars(self):
        """LLMSettings should read all environment variables together."""
        with patch.dict(
            os.environ,
            {
                "AGENTBEATS_LLM_API_KEY": "env-key",
                "AGENTBEATS_LLM_BASE_URL": "https://env.api.com",
                "AGENTBEATS_LLM_MODEL": "gpt-3.5-turbo",
                "AGENTBEATS_LLM_TEMPERATURE": "0.5",
            },
        ):
            settings = LLMSettings()
            assert settings.api_key == "env-key"
            assert settings.base_url == "https://env.api.com"
            assert settings.model == "gpt-3.5-turbo"
            assert settings.temperature == 0.5


class TestCreateLLMClient:
    """Test suite for create_llm_client() factory function."""

    def test_creates_async_openai_client(self):
        """create_llm_client() should return AsyncOpenAI instance."""
        client = create_llm_client()
        assert isinstance(client, AsyncOpenAI)

    def test_uses_settings_api_key(self):
        """create_llm_client() should use API key from settings."""
        settings = LLMSettings(api_key="factory-test-key")
        client = create_llm_client(settings)
        assert client.api_key == "factory-test-key"

    def test_uses_settings_base_url(self):
        """create_llm_client() should use base URL from settings."""
        settings = LLMSettings(base_url="https://factory.test.com")
        client = create_llm_client(settings)
        assert client.base_url == "https://factory.test.com/"

    def test_uses_default_settings_if_none_provided(self):
        """create_llm_client() should create default settings if none provided."""
        with patch.dict(os.environ, {"AGENTBEATS_LLM_API_KEY": "default-key"}):
            client = create_llm_client()
            assert client.api_key == "default-key"

    def test_accepts_none_api_key(self):
        """create_llm_client() should accept None as API key for compatibility."""
        settings = LLMSettings(api_key=None)
        client = create_llm_client(settings)
        # AsyncOpenAI accepts None for api_key (useful for testing)
        assert isinstance(client, AsyncOpenAI)


class TestGreenAgentBackwardCompatibility:
    """Test backward compatibility with green agent settings."""

    def test_green_settings_has_llm_field(self):
        """GreenSettings should have nested llm field using common LLMSettings."""
        # Import inside test to avoid circular dependencies
        from green.settings import GreenSettings

        settings = GreenSettings()
        assert hasattr(settings, "llm")
        assert isinstance(settings.llm, LLMSettings)

    def test_green_settings_llm_env_vars(self):
        """GreenSettings.llm should read from AGENTBEATS_LLM_* env vars."""
        from green.settings import GreenSettings

        with patch.dict(
            os.environ,
            {
                "AGENTBEATS_LLM_API_KEY": "green-test-key",
                "AGENTBEATS_LLM_MODEL": "gpt-4-turbo",
            },
        ):
            settings = GreenSettings()
            assert settings.llm.api_key == "green-test-key"
            assert settings.llm.model == "gpt-4-turbo"
