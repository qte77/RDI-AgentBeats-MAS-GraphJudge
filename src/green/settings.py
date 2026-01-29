"""Green Agent configuration using pydantic-settings.

Centralizes configuration for Green Agent with environment variable support.
"""

from __future__ import annotations

from pathlib import Path

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
        GREEN_CARD_URL: AgentCard URL (default: http://{host}:{port})
        GREEN_OUTPUT_FILE: Output file path (default: output/results.json)
        AGENT_UUID: Agent identifier (default: green-agent)
        PURPLE_AGENT_URL: URL for Purple Agent (default: http://{host}:{purple_port})
    """

    model_config = SettingsConfigDict(env_prefix="GREEN_")

    # Server settings
    host: str = "0.0.0.0"
    port: int = 9009  # Container port (host: 9009)
    purple_port: int = 9010

    # Agent settings - use validation_alias for non-prefixed env vars
    agent_uuid: str = Field(default="green-agent", validation_alias="AGENT_UUID")
    purple_agent_url: str = Field(
        default=f"http://{host}:{purple_port}", validation_alias="PURPLE_AGENT_URL"
    )
    card_url: str | None = Field(
        default=None,
        validation_alias="GREEN_CARD_URL",
        description="AgentCard URL (defaults to http://{host}:{port})",
    )
    output_file: Path = Field(
        default=Path("output/results.json"),
        description="Output file path for evaluation results",
    )

    # Nested LLM settings
    llm: LLMSettings = Field(default_factory=LLMSettings)

    def get_card_url(self) -> str:
        """Get AgentCard URL, constructing from host/port if not explicitly set."""
        if self.card_url:
            return self.card_url
        return f"http://{self.host}:{self.port}"
