"""Common LLM settings for AgentBeats Green and Purple agents.

Centralizes LLM configuration with environment variable support.
Single source of truth for LLM client configuration.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """LLM client configuration.

    Environment variables:
        AGENTBEATS_LLM_API_KEY: API key for LLM service
        AGENTBEATS_LLM_BASE_URL: Base URL for LLM API (default: https://api.openai.com/v1)
        AGENTBEATS_LLM_MODEL: Model identifier (default: gpt-4o-mini)
        AGENTBEATS_LLM_TEMPERATURE: Sampling temperature for LLM calls (default: 0.0)
    """

    model_config = SettingsConfigDict(env_prefix="AGENTBEATS_LLM_")

    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    temperature: float = 0.0


class A2ASettings(BaseSettings):
    """A2A protocol client configuration.

    Environment variables:
        AGENTBEATS_A2A_TIMEOUT: Timeout in seconds for A2A client connections (default: 30.0)
        AGENTBEATS_A2A_CONNECT_TIMEOUT: Connect timeout in seconds (default: 10.0)
    """

    model_config = SettingsConfigDict(env_prefix="AGENTBEATS_A2A_")

    timeout: float = 30.0
    connect_timeout: float = 10.0
