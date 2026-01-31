"""Tests for Green Agent server settings and environment variable handling.

RED phase: Tests should FAIL until server properly reads GREEN_* environment variables.

Following TDD best practices:
- Test that main() reads GREEN_HOST and GREEN_PORT from environment
- Test that settings.py provides correct defaults
- Test that docker-compose environment variables are respected
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch


class TestGreenServerSettings:
    """Test Green Agent server reads environment variables correctly."""

    def test_green_settings_reads_green_host_from_env(self):
        """GreenSettings reads GREEN_HOST environment variable."""
        from green.settings import GreenSettings

        # Set environment variable
        with patch.dict(os.environ, {"GREEN_HOST": "0.0.0.0"}):
            settings = GreenSettings()
            assert settings.host == "0.0.0.0"

    def test_green_settings_reads_green_port_from_env(self):
        """GreenSettings reads GREEN_PORT environment variable."""
        from green.settings import GreenSettings

        # Set environment variable
        with patch.dict(os.environ, {"GREEN_PORT": "9009"}):
            settings = GreenSettings()
            assert settings.port == 9009

    def test_green_settings_has_correct_defaults(self):
        """GreenSettings has correct default values."""
        from green.settings import GreenSettings

        # Clear any environment variables
        with patch.dict(os.environ, {}, clear=True):
            settings = GreenSettings()
            assert settings.host == "0.0.0.0"
            assert settings.port == 9009

    def test_green_server_main_uses_settings(self):
        """Green server main() function uses GreenSettings for host/port."""
        from green.server import main

        # Mock uvicorn.run to capture what host/port it receives
        with patch("green.server.uvicorn.run") as mock_run:
            with patch.dict(os.environ, {"GREEN_HOST": "127.0.0.1", "GREEN_PORT": "8888"}):
                # Mock create_app to avoid actual app creation
                with patch("green.server.create_app") as mock_create_app:
                    mock_create_app.return_value = MagicMock()

                    try:
                        main()
                    except SystemExit:
                        pass  # main() may call sys.exit()

                    # Verify uvicorn.run was called with settings-based values
                    mock_run.assert_called_once()
                    call_kwargs = mock_run.call_args.kwargs
                    assert call_kwargs["host"] == "127.0.0.1"
                    assert call_kwargs["port"] == 8888

    def test_green_server_parse_args_respects_settings(self):
        """Green server parse_args() uses settings as defaults."""
        from green.server import parse_args
        from green.settings import GreenSettings

        with patch.dict(os.environ, {"GREEN_HOST": "192.168.1.1", "GREEN_PORT": "7777"}):
            settings = GreenSettings()
            args = parse_args(args=[], settings=settings)

            assert args.host == "192.168.1.1"
            assert args.port == 7777

    def test_green_server_ignores_generic_host_port_env(self):
        """Green server ignores generic HOST/PORT environment variables."""
        from green.settings import GreenSettings

        # Set generic HOST/PORT (should be ignored)
        # Set GREEN_HOST/GREEN_PORT (should be used)
        with patch.dict(
            os.environ,
            {
                "HOST": "wrong.host",
                "PORT": "9999",
                "GREEN_HOST": "correct.host",
                "GREEN_PORT": "9009",
            },
        ):
            settings = GreenSettings()
            # Should use GREEN_* not generic HOST/PORT
            assert settings.host == "correct.host"
            assert settings.port == 9009
