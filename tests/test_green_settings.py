"""Tests for Green Agent settings configuration.

Tests validate UUID format compliance per A2A protocol specification,
and coverage of all configurable fields via environment variables.
"""

from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError


class TestGreenSettingsUUID:
    """Tests for agent_uuid validation in GreenSettings."""

    def test_default_uuid_is_valid(self):
        """Test that default agent_uuid is a valid UUID (auto-generated)."""
        from green.settings import GreenSettings

        settings = GreenSettings()
        assert settings.agent_uuid is not None
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


class TestGreenSettingsServerConfig:
    """Tests for server configuration fields in GreenSettings."""

    def test_default_host(self):
        """Test that default host is 0.0.0.0."""
        from green.settings import GreenSettings

        settings = GreenSettings()
        assert settings.host == "0.0.0.0"

    def test_host_from_env(self, monkeypatch):
        """Test GREEN_HOST env var is respected."""
        from green.settings import GreenSettings

        monkeypatch.setenv("GREEN_HOST", "127.0.0.1")
        settings = GreenSettings()
        assert settings.host == "127.0.0.1"

    def test_default_port(self):
        """Test that default port is 9009."""
        from green.settings import GreenSettings

        settings = GreenSettings()
        assert settings.port == 9009

    def test_port_from_env(self, monkeypatch):
        """Test GREEN_PORT env var is respected."""
        from green.settings import GreenSettings

        monkeypatch.setenv("GREEN_PORT", "8080")
        settings = GreenSettings()
        assert settings.port == 8080

    def test_default_output_file(self):
        """Test that default output_file is output/results.json."""
        from green.settings import GreenSettings

        settings = GreenSettings()
        assert settings.output_file == Path("output/results.json")

    def test_output_file_from_env(self, monkeypatch):
        """Test GREEN_OUTPUT_FILE env var is respected."""
        from green.settings import GreenSettings

        monkeypatch.setenv("GREEN_OUTPUT_FILE", "/tmp/results.json")
        settings = GreenSettings()
        assert settings.output_file == Path("/tmp/results.json")

    def test_default_log_level(self):
        """Test that default log_level is info."""
        from green.settings import GreenSettings

        settings = GreenSettings()
        assert settings.log_level == "info"

    def test_log_level_from_env(self, monkeypatch):
        """Test GREEN_LOG_LEVEL env var is respected."""
        from green.settings import GreenSettings

        monkeypatch.setenv("GREEN_LOG_LEVEL", "debug")
        settings = GreenSettings()
        assert settings.log_level == "debug"


class TestGreenSettingsAgentDescription:
    """Tests for agent_description field in GreenSettings."""

    def test_default_agent_description(self):
        """Test that default agent_description is set."""
        from green.settings import GreenSettings

        settings = GreenSettings()
        assert settings.agent_description is not None
        assert len(settings.agent_description) > 0

    def test_agent_description_from_env(self, monkeypatch):
        """Test GREEN_AGENT_DESCRIPTION env var is respected."""
        from green.settings import GreenSettings

        monkeypatch.setenv("GREEN_AGENT_DESCRIPTION", "Custom evaluator description")
        settings = GreenSettings()
        assert settings.agent_description == "Custom evaluator description"


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
