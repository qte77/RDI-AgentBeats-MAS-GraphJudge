"""Tests for Purple Agent server settings and environment variable handling.

RED phase: Tests should FAIL until server properly reads PURPLE_* environment variables.

Following TDD best practices:
- Test that main() reads PURPLE_HOST and PURPLE_PORT from environment
- Test that settings.py provides correct defaults
- Test that docker-compose environment variables are respected
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch


class TestPurpleServerSettings:
    """Test Purple Agent server reads environment variables correctly."""

    def test_purple_settings_reads_purple_host_from_env(self):
        """PurpleSettings reads PURPLE_HOST environment variable."""
        from purple.settings import PurpleSettings

        # Set environment variable
        with patch.dict(os.environ, {"PURPLE_HOST": "0.0.0.0"}):
            settings = PurpleSettings()
            assert settings.host == "0.0.0.0"

    def test_purple_settings_reads_purple_port_from_env(self):
        """PurpleSettings reads PURPLE_PORT environment variable."""
        from purple.settings import PurpleSettings

        # Set environment variable
        with patch.dict(os.environ, {"PURPLE_PORT": "9010"}):
            settings = PurpleSettings()
            assert settings.port == 9010

    def test_purple_settings_has_correct_defaults(self):
        """PurpleSettings has correct default values."""
        from purple.settings import PurpleSettings

        # Clear any environment variables
        with patch.dict(os.environ, {}, clear=True):
            settings = PurpleSettings()
            assert settings.host == "0.0.0.0"
            assert settings.port == 9010

    def test_purple_server_main_uses_settings(self):
        """Purple server main() function uses PurpleSettings for host/port."""
        from purple.server import main

        # Mock uvicorn.run to capture what host/port it receives
        with patch("purple.server.uvicorn.run") as mock_run:
            with patch.dict(os.environ, {"PURPLE_HOST": "127.0.0.1", "PURPLE_PORT": "7777"}):
                # Mock create_app to avoid actual app creation
                with patch("purple.server.create_app") as mock_create_app:
                    mock_create_app.return_value = MagicMock()

                    try:
                        main()
                    except SystemExit:
                        pass  # main() may call sys.exit()

                    # Verify uvicorn.run was called with settings-based values
                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args.kwargs
                    assert call_kwargs["host"] == "127.0.0.1"
                    assert call_kwargs["port"] == 7777

    def test_purple_server_parse_args_respects_settings(self):
        """Purple server parse_args() uses settings as defaults."""
        from purple.server import parse_args
        from purple.settings import PurpleSettings

        with patch.dict(os.environ, {"PURPLE_HOST": "192.168.1.1", "PURPLE_PORT": "8888"}):
            settings = PurpleSettings()
            args = parse_args(args=[], settings=settings)

            assert args.host == "192.168.1.1"
            assert args.port == 8888

    def test_purple_server_ignores_generic_host_port_env(self):
        """Purple server ignores generic HOST/PORT environment variables."""
        from purple.settings import PurpleSettings

        # Set generic HOST/PORT (should be ignored)
        # Set PURPLE_HOST/PURPLE_PORT (should be used)
        with patch.dict(
            os.environ,
            {
                "HOST": "wrong.host",
                "PORT": "9999",
                "PURPLE_HOST": "correct.host",
                "PURPLE_PORT": "9010",
            },
        ):
            settings = PurpleSettings()
            # Should use PURPLE_* not generic HOST/PORT
            assert settings.host == "correct.host"
            assert settings.port == 9010
