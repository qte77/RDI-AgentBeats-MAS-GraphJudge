"""LLM-based evaluation configuration and implementation."""

from __future__ import annotations

import os

from pydantic import BaseModel


class LLMConfig(BaseModel):
    """Configuration for LLM client.

    Reads environment variables:
    - AGENTBEATS_LLM_API_KEY: API key for authentication
    - AGENTBEATS_LLM_BASE_URL: Base URL for LLM endpoint (default: https://api.openai.com/v1)
    - AGENTBEATS_LLM_MODEL: Model name (default: gpt-4o-mini)

    Supports any OpenAI-compatible endpoint.
    """

    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"


def get_llm_config() -> LLMConfig:
    """Get LLM configuration from environment variables.

    Returns:
        LLMConfig with values from environment or defaults
    """
    return LLMConfig(
        api_key=os.environ.get("AGENTBEATS_LLM_API_KEY"),
        base_url=os.environ.get("AGENTBEATS_LLM_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("AGENTBEATS_LLM_MODEL", "gpt-4o-mini"),
    )
