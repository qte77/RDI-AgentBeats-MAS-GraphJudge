"""Purple Agent configuration using pydantic-settings.

Purple Agent is a minimal A2A-compliant test fixture used for end-to-end testing
of Green Agent's evaluation pipeline. It is NOT a production agent.

Centralizes configuration for Purple Agent with environment variable support.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.settings import A2ASettings


class PurpleSettings(BaseSettings):
    """Purple Agent configuration.

    Environment variables:
        PURPLE_HOST: Server host (default: 0.0.0.0)
        PURPLE_PORT: Server port (default: 9010)
        PURPLE_CARD_URL: AgentCard URL (default: http://{host}:{port})
        PURPLE_AGENT_NAME: Agent display name (default: purple-agent)
        PURPLE_AGENT_DESCRIPTION: Agent description for AgentCard
        PURPLE_AGENT_VERSION: Agent version string (default: 1.0.0)
        PURPLE_STATIC_PEERS: JSON list of static peer URLs (default: [])
        PURPLE_GREEN_URL: Green agent URL (default: http://localhost:9009)
        PURPLE_LOG_LEVEL: Uvicorn log level (default: info)
        AGENT_UUID: Agent identifier (default: generated UUID)
    """

    model_config = SettingsConfigDict(env_prefix="PURPLE_")

    host: str = "0.0.0.0"
    port: int = 9010  # Container port (host: 9010)
    card_url: str | None = None
    log_level: str = "info"

    # Agent metadata
    agent_name: str = "purple-agent"
    agent_description: str = "Simple A2A-compliant agent for E2E testing and validation"
    agent_version: str = "1.0.0"

    # Peer discovery and green agent coordination
    static_peers: list[str] = Field(default_factory=list)
    green_url: str = "http://localhost:9009"

    agent_uuid: UUID = Field(default_factory=uuid4, validation_alias="AGENT_UUID")

    # Nested A2A settings
    a2a: A2ASettings = Field(default_factory=A2ASettings)

    def get_card_url(self) -> str:
        """Get AgentCard URL, constructing from host/port if not explicitly set."""
        if self.card_url:
            return self.card_url
        return f"http://{self.host}:{self.port}"
