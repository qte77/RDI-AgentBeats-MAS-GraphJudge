"""Green Agent configuration using pydantic-settings.

Centralizes configuration for Green Agent with environment variable support.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """LLM client configuration.

    Environment variables:
        AGENTBEATS_LLM_API_KEY: API key for LLM service
        AGENTBEATS_LLM_BASE_URL: Base URL for LLM API
        AGENTBEATS_LLM_MODEL: Model identifier
    """

    model_config = SettingsConfigDict(env_prefix="AGENTBEATS_LLM_")

    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"


class GreenSettings(BaseSettings):
    """Green Agent configuration.

    Environment variables:
        GREEN_HOST: Server host (default: 0.0.0.0)
        GREEN_PORT: Server port (default: 9009)
        AGENT_UUID: Agent identifier (default: green-agent)
        PURPLE_AGENT_URL: URL for Purple Agent (default: http://localhost:8002)
    """

    model_config = SettingsConfigDict(env_prefix="GREEN_")

    # Server settings
    host: str = "0.0.0.0"
    port: int = 9009

    # Agent settings - use validation_alias for non-prefixed env vars
    agent_uuid: str = Field(default="green-agent", validation_alias="AGENT_UUID")
    purple_agent_url: str = Field(
        default="http://localhost:8002", validation_alias="PURPLE_AGENT_URL"
    )

    # Nested LLM settings
    llm: LLMSettings = Field(default_factory=LLMSettings)
