"""Tests for TraceCollectionConfig model - STORY-030.

Validates:
- TraceCollectionConfig Pydantic model with correct fields and defaults
- Export from common package
- GreenSettings.trace_collection nested field
"""

from __future__ import annotations


def test_trace_collection_config_importable_from_models():
    """TraceCollectionConfig can be imported from common.models."""
    from common.models import TraceCollectionConfig

    assert TraceCollectionConfig is not None


def test_trace_collection_config_exported_from_common():
    """TraceCollectionConfig is exported from the common package."""
    from common import TraceCollectionConfig

    assert TraceCollectionConfig is not None


def test_trace_collection_config_default_values():
    """TraceCollectionConfig has correct default values."""
    from common.models import TraceCollectionConfig

    config = TraceCollectionConfig()

    assert config.max_timeout_seconds == 30
    assert config.idle_threshold_seconds == 5
    assert config.use_completion_signals is True


def test_trace_collection_config_custom_values():
    """TraceCollectionConfig accepts custom values."""
    from common.models import TraceCollectionConfig

    config = TraceCollectionConfig(
        max_timeout_seconds=60,
        idle_threshold_seconds=10,
        use_completion_signals=False,
    )

    assert config.max_timeout_seconds == 60
    assert config.idle_threshold_seconds == 10
    assert config.use_completion_signals is False


def test_green_settings_has_trace_collection_field():
    """GreenSettings includes a trace_collection field of type TraceCollectionConfig."""
    from common.models import TraceCollectionConfig
    from green.settings import GreenSettings

    settings = GreenSettings()

    assert hasattr(settings, "trace_collection")
    assert isinstance(settings.trace_collection, TraceCollectionConfig)


def test_green_settings_trace_collection_defaults():
    """GreenSettings.trace_collection has correct default values."""
    from green.settings import GreenSettings

    settings = GreenSettings()

    assert settings.trace_collection.max_timeout_seconds == 30
    assert settings.trace_collection.idle_threshold_seconds == 5
    assert settings.trace_collection.use_completion_signals is True
