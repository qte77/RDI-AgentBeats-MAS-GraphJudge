"""Tests for Purple Agent settings configuration.

Tests validate UUID format compliance per A2A protocol specification,
and coverage of all configurable fields via environment variables.
"""

from uuid import UUID

import pytest
from pydantic import ValidationError


class TestPurpleSettingsUUID:
    """Tests for agent_uuid validation in PurpleSettings."""

    def test_default_uuid_is_valid(self):
        """Test that default agent_uuid is a valid UUID (auto-generated)."""
        from purple.settings import PurpleSettings

        settings = PurpleSettings()
        assert settings.agent_uuid is not None
        UUID(str(settings.agent_uuid))

    def test_custom_uuid_accepted(self, monkeypatch):
        """Test that custom valid UUID is accepted via env var."""
        from purple.settings import PurpleSettings

        custom_uuid = "550e8400-e29b-41d4-a716-446655440000"
        monkeypatch.setenv("AGENT_UUID", custom_uuid)
        settings = PurpleSettings()
        assert str(settings.agent_uuid) == custom_uuid

    def test_invalid_uuid_rejected(self):
        """Test that non-UUID string is rejected (A2A compliance)."""
        from purple.settings import PurpleSettings

        with pytest.raises(ValidationError):
            PurpleSettings(agent_uuid="purple-agent")

    def test_malformed_uuid_rejected(self):
        """Test that malformed UUID is rejected."""
        from purple.settings import PurpleSettings

        with pytest.raises(ValidationError):
            PurpleSettings(agent_uuid="not-a-uuid")


class TestPurpleSettingsServerConfig:
    """Tests for server configuration fields in PurpleSettings."""

    def test_default_host(self):
        """Test that default host is 0.0.0.0."""
        from purple.settings import PurpleSettings

        settings = PurpleSettings()
        assert settings.host == "0.0.0.0"

    def test_host_from_env(self, monkeypatch):
        """Test PURPLE_HOST env var is respected."""
        from purple.settings import PurpleSettings

        monkeypatch.setenv("PURPLE_HOST", "127.0.0.1")
        settings = PurpleSettings()
        assert settings.host == "127.0.0.1"

    def test_default_port(self):
        """Test that default port is 9010."""
        from purple.settings import PurpleSettings

        settings = PurpleSettings()
        assert settings.port == 9010

    def test_port_from_env(self, monkeypatch):
        """Test PURPLE_PORT env var is respected."""
        from purple.settings import PurpleSettings

        monkeypatch.setenv("PURPLE_PORT", "8081")
        settings = PurpleSettings()
        assert settings.port == 8081

    def test_default_log_level(self):
        """Test that default log_level is info."""
        from purple.settings import PurpleSettings

        settings = PurpleSettings()
        assert settings.log_level == "info"

    def test_log_level_from_env(self, monkeypatch):
        """Test PURPLE_LOG_LEVEL env var is respected."""
        from purple.settings import PurpleSettings

        monkeypatch.setenv("PURPLE_LOG_LEVEL", "debug")
        settings = PurpleSettings()
        assert settings.log_level == "debug"


class TestPurpleSettingsAgentMetadata:
    """Tests for agent metadata fields in PurpleSettings."""

    def test_default_agent_name(self):
        """Test that default agent_name is set."""
        from purple.settings import PurpleSettings

        settings = PurpleSettings()
        assert settings.agent_name == "purple-agent"

    def test_agent_name_from_env(self, monkeypatch):
        """Test PURPLE_AGENT_NAME env var is respected."""
        from purple.settings import PurpleSettings

        monkeypatch.setenv("PURPLE_AGENT_NAME", "my-purple-agent")
        settings = PurpleSettings()
        assert settings.agent_name == "my-purple-agent"

    def test_default_agent_description(self):
        """Test that default agent_description is set."""
        from purple.settings import PurpleSettings

        settings = PurpleSettings()
        assert settings.agent_description is not None
        assert len(settings.agent_description) > 0

    def test_agent_description_from_env(self, monkeypatch):
        """Test PURPLE_AGENT_DESCRIPTION env var is respected."""
        from purple.settings import PurpleSettings

        monkeypatch.setenv("PURPLE_AGENT_DESCRIPTION", "Custom test fixture")
        settings = PurpleSettings()
        assert settings.agent_description == "Custom test fixture"

    def test_default_agent_version(self):
        """Test that default agent_version is 1.0.0."""
        from purple.settings import PurpleSettings

        settings = PurpleSettings()
        assert settings.agent_version == "1.0.0"

    def test_agent_version_from_env(self, monkeypatch):
        """Test PURPLE_AGENT_VERSION env var is respected."""
        from purple.settings import PurpleSettings

        monkeypatch.setenv("PURPLE_AGENT_VERSION", "2.1.0")
        settings = PurpleSettings()
        assert settings.agent_version == "2.1.0"


class TestPurpleSettingsPeersAndGreenURL:
    """Tests for static_peers and green_url fields in PurpleSettings."""

    def test_default_static_peers_empty(self):
        """Test that default static_peers is empty list."""
        from purple.settings import PurpleSettings

        settings = PurpleSettings()
        assert settings.static_peers == []

    def test_static_peers_from_env(self, monkeypatch):
        """Test PURPLE_STATIC_PEERS env var is respected (JSON list)."""
        from purple.settings import PurpleSettings

        monkeypatch.setenv("PURPLE_STATIC_PEERS", '["http://agent1:8080", "http://agent2:8080"]')
        settings = PurpleSettings()
        assert settings.static_peers == ["http://agent1:8080", "http://agent2:8080"]

    def test_default_green_url(self):
        """Test that default green_url points to localhost green port."""
        from purple.settings import PurpleSettings

        settings = PurpleSettings()
        assert settings.green_url == "http://localhost:9009"

    def test_green_url_from_env(self, monkeypatch):
        """Test PURPLE_GREEN_URL env var is respected."""
        from purple.settings import PurpleSettings

        monkeypatch.setenv("PURPLE_GREEN_URL", "http://green-service:9009")
        settings = PurpleSettings()
        assert settings.green_url == "http://green-service:9009"


class TestPurpleSettingsEnvVars:
    """Tests for environment variable configuration."""

    def test_agent_uuid_from_env(self, monkeypatch):
        """Test AGENT_UUID environment variable is respected."""
        from purple.settings import PurpleSettings

        test_uuid = "019b4d08-d84c-7a00-b2ec-4905ef7afc96"
        monkeypatch.setenv("AGENT_UUID", test_uuid)

        settings = PurpleSettings()
        assert str(settings.agent_uuid) == test_uuid

    def test_invalid_uuid_env_rejected(self, monkeypatch):
        """Test invalid UUID from environment is rejected."""
        from purple.settings import PurpleSettings

        monkeypatch.setenv("AGENT_UUID", "invalid-uuid")

        with pytest.raises(ValidationError):
            PurpleSettings()
