"""Green Agent configuration using pydantic-settings.

Centralizes configuration for Green Agent with environment variable support.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import settings from common module for single source of truth
from common.settings import A2ASettings, LLMSettings


class GreenSettings(BaseSettings):
    """Green Agent configuration.

    Environment variables:
        GREEN_HOST: Server host (default: 0.0.0.0)
        GREEN_PORT: Server port (default: 9009)
        GREEN_CARD_URL: AgentCard URL (default: http://{host}:{port})
        GREEN_OUTPUT_FILE: Output file path (default: output/results.json)
        GREEN_COORDINATION_ROUNDS: Number of coordination rounds (default: 3)
        GREEN_ROUND_DELAY_SECONDS: Delay between rounds in seconds (default: 0.1)
        GREEN_AGENT_VERSION: Agent version string (default: 1.0.0)
        GREEN_DOMAIN: Evaluation domain (default: graph-assessment)
        GREEN_MAX_SCORE: Maximum score for evaluation (default: 100.0)
        AGENT_UUID: Agent identifier (default: green-agent)
        PURPLE_AGENT_URL: URL for Purple Agent (default: http://{host}:{purple_port})
    """

    model_config = SettingsConfigDict(env_prefix="GREEN_")

    # Server settings
    host: str = "0.0.0.0"
    port: int = 9009  # Container port (host: 9009)
    purple_port: int = 9010

    # Execution settings
    coordination_rounds: int = 3
    round_delay_seconds: float = 0.1

    # Agent metadata
    agent_version: str = "1.0.0"
    domain: str = "graph-assessment"
    max_score: float = 100.0

    # Agent settings - use validation_alias for non-prefixed env vars
    agent_uuid: UUID = Field(default_factory=uuid4, validation_alias="AGENT_UUID")
    agent_name: str = Field(default="green-agent", validation_alias="AGENT_NAME")
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

    # Nested A2A settings
    a2a: A2ASettings = Field(default_factory=A2ASettings)

    def get_card_url(self) -> str:
        """Get AgentCard URL, constructing from host/port if not explicitly set."""
        if self.card_url:
            return self.card_url
        return f"http://{self.host}:{self.port}"
