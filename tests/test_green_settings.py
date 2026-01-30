"""Tests for Green Agent settings configuration.

Tests validate UUID format compliance per A2A protocol specification.
"""

from uuid import UUID

import pytest
from pydantic import ValidationError


class TestGreenSettingsUUID:
    """Tests for agent_uuid validation in GreenSettings."""

    def test_default_uuid_is_valid(self):
        """Test that default agent_uuid is a valid UUID (auto-generated)."""
        from green.settings import GreenSettings

        settings = GreenSettings()
        # Should be a valid UUID instance or string representation
        assert settings.agent_uuid is not None
        # Validate it's a proper UUID format
        UUID(str(settings.agent_uuid))

    def test_custom_uuid_accepted(self, monkeypatch):
        """Test that custom valid UUID is accepted via env var."""
        from green.settings import GreenSettings

        custom_uuid = "550e8400-e29b-41d4-a716-446655440000"
        monkeypatch.setenv("AGENT_UUID", custom_uuid)
        settings = GreenSettings()
        assert str(settings.agent_uuid) == custom_uuid

    def test_invalid_uuid_rejected(self):
        """Test that non-UUID string is rejected (A2A compliance)."""
        from green.settings import GreenSettings

        with pytest.raises(ValidationError):
            GreenSettings(agent_uuid="green-agent")

    def test_malformed_uuid_rejected(self):
        """Test that malformed UUID is rejected."""
        from green.settings import GreenSettings

        with pytest.raises(ValidationError):
            GreenSettings(agent_uuid="not-a-uuid")


class TestGreenSettingsAgentName:
    """Tests for agent_name (display name) in GreenSettings."""

    def test_default_agent_name(self):
        """Test that default agent_name is set."""
        from green.settings import GreenSettings

        settings = GreenSettings()
        assert settings.agent_name == "green-agent"

    def test_custom_agent_name(self, monkeypatch):
        """Test that custom agent_name is accepted via env var."""
        from green.settings import GreenSettings

        monkeypatch.setenv("AGENT_NAME", "my-custom-agent")
        settings = GreenSettings()
        assert settings.agent_name == "my-custom-agent"


class TestGreenSettingsEnvVars:
    """Tests for environment variable configuration."""

    def test_agent_uuid_from_env(self, monkeypatch):
        """Test AGENT_UUID environment variable is respected."""
        from green.settings import GreenSettings

        test_uuid = "019b4d08-d84c-7a00-b2ec-4905ef7afc96"
        monkeypatch.setenv("AGENT_UUID", test_uuid)

        settings = GreenSettings()
        assert str(settings.agent_uuid) == test_uuid

    def test_agent_name_from_env(self, monkeypatch):
        """Test AGENT_NAME environment variable is respected."""
        from green.settings import GreenSettings

        monkeypatch.setenv("AGENT_NAME", "env-agent-name")

        settings = GreenSettings()
        assert settings.agent_name == "env-agent-name"

    def test_invalid_uuid_env_rejected(self, monkeypatch):
        """Test invalid UUID from environment is rejected."""
        from green.settings import GreenSettings

        monkeypatch.setenv("AGENT_UUID", "invalid-uuid")

        with pytest.raises(ValidationError):
            GreenSettings()
