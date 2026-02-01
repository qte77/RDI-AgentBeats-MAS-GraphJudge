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
        AGENT_UUID: Agent identifier (default: generated UUID)
    """

    model_config = SettingsConfigDict(env_prefix="PURPLE_")

    host: str = "0.0.0.0"
    port: int = 9010  # Container port (host: 9010)
    card_url: str | None = None
    agent_uuid: UUID = Field(default_factory=uuid4, validation_alias="AGENT_UUID")

    # Nested A2A settings
    a2a: A2ASettings = Field(default_factory=A2ASettings)

    def get_card_url(self) -> str:
        """Get AgentCard URL, constructing from host/port if not explicitly set."""
        if self.card_url:
            return self.card_url
        return f"http://{self.host}:{self.port}"
