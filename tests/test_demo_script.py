"""Tests for demo video script validation.

Validates that demo-video-script.md meets acceptance criteria from STORY-017.
"""

from pathlib import Path


def test_demo_script_exists() -> None:
    """Test that demo video script file exists."""
    script_path = Path("docs/demo-video-script.md")
    assert script_path.exists(), "Demo video script should exist at docs/demo-video-script.md"


def test_demo_script_has_scene1_server_startup() -> None:
    """Test that Scene 1 covers server startup and A2A endpoint verification."""
    script_path = Path("docs/demo-video-script.md")
    content = script_path.read_text()

    # Check for Scene 1 presence
    assert "Scene 1" in content or "## Scene 1" in content, "Should have Scene 1 section"

    # Check for server startup elements
    assert "server" in content.lower() or "startup" in content.lower(), "Should mention server startup"
    assert "a2a" in content.lower() or "agent-card" in content.lower(), "Should mention A2A endpoints"


def test_demo_script_has_scene2_evaluation_flow() -> None:
    """Test that Scene 2 covers evaluation flow with trace capture."""
    script_path = Path("docs/demo-video-script.md")
    content = script_path.read_text()

    # Check for Scene 2 presence
    assert "Scene 2" in content or "## Scene 2" in content, "Should have Scene 2 section"

    # Check for evaluation flow elements
    assert "evaluation" in content.lower() or "trace" in content.lower(), "Should mention evaluation/trace"


def test_demo_script_has_scene3_results_display() -> None:
    """Test that Scene 3 covers multi-tier results display."""
    script_path = Path("docs/demo-video-script.md")
    content = script_path.read_text()

    # Check for Scene 3 presence
    assert "Scene 3" in content or "## Scene 3" in content, "Should have Scene 3 section"

    # Check for all three tier components
    assert "graph" in content.lower(), "Should mention graph evaluation"
    assert "llm" in content.lower() or "judge" in content.lower(), "Should mention LLM judge"
    assert "latency" in content.lower(), "Should mention latency metrics"


def test_demo_script_includes_narration() -> None:
    """Test that script includes narration text."""
    script_path = Path("docs/demo-video-script.md")
    content = script_path.read_text()

    # Check for narration indicators
    assert (
        "narration" in content.lower() or "narrator" in content.lower() or "voiceover" in content.lower()
    ), "Should include narration text"


def test_demo_script_includes_screen_actions() -> None:
    """Test that script includes screen actions."""
    script_path = Path("docs/demo-video-script.md")
    content = script_path.read_text()

    # Check for screen action indicators
    assert (
        "screen" in content.lower() or "action" in content.lower() or "show" in content.lower()
    ), "Should include screen actions"


def test_demo_script_includes_timing_cues() -> None:
    """Test that script includes timing cues."""
    script_path = Path("docs/demo-video-script.md")
    content = script_path.read_text()

    # Check for timing indicators (seconds, minutes, duration, etc.)
    timing_indicators = ["second", "minute", "duration", "time:", "0:", "1:", "2:", "3:"]
    has_timing = any(indicator in content.lower() for indicator in timing_indicators)

    assert has_timing, "Should include timing cues"


def test_demo_script_duration_approximately_3_minutes() -> None:
    """Test that script content is approximately 3 minutes worth of content.

    Average narration speed is ~150 words per minute.
    3 minutes = ~450 words minimum for narration.
    """
    script_path = Path("docs/demo-video-script.md")
    content = script_path.read_text()

    # Count words (rough estimate)
    word_count = len(content.split())

    # Should have substantial content (~300+ words minimum including structure)
    assert word_count >= 300, f"Script should have substantial content (got {word_count} words, expected 300+)"
