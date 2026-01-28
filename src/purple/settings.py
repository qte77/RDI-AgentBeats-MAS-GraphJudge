"""Purple Agent configuration using pydantic-settings.

Purple Agent is a minimal A2A-compliant test fixture used for end-to-end testing
of Green Agent's evaluation pipeline. It is NOT a production agent.

Centralizes configuration for Purple Agent with environment variable support.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class PurpleSettings(BaseSettings):
    """Purple Agent configuration.

    Environment variables:
        PURPLE_HOST: Server host (default: 0.0.0.0)
        PURPLE_PORT: Server port (default: 9010)
        PURPLE_CARD_URL: AgentCard URL (default: http://{host}:{port})
    """

    model_config = SettingsConfigDict(env_prefix="PURPLE_")

    host: str = "0.0.0.0"
    port: int = 9010
    card_url: str | None = None

    def get_card_url(self) -> str:
        """Get AgentCard URL, constructing from host/port if not explicitly set."""
        if self.card_url:
            return self.card_url
        return f"http://{self.host}:{self.port}"
