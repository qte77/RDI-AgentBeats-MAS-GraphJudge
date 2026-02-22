"""LLM client factory for AgentBeats Green and Purple agents.

Provides centralized LLM client creation with configuration from LLMSettings.
"""

from __future__ import annotations

from openai import AsyncOpenAI

from common.settings import LLMSettings


def create_llm_client(settings: LLMSettings | None = None) -> AsyncOpenAI:
    """Create OpenAI-compatible async client with configuration.

    Args:
        settings: LLMSettings instance. If None, creates from environment variables.

    Returns:
        Configured AsyncOpenAI client

    Example:
        >>> settings = LLMSettings(api_key="sk-...", model="gpt-4")
        >>> client = create_llm_client(settings)
        >>> # Or use defaults from environment:
        >>> client = create_llm_client()
    """
    if settings is None:
        settings = LLMSettings()

    return AsyncOpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
    )
