"""Tests for extensibility documentation completeness.

Validates that AGENTBEATS_REGISTRATION.md contains required sections
for evaluator extensibility and custom evaluator integration.
"""

from pathlib import Path


def test_extensibility_documentation_exists():
    """Test that extensibility documentation file exists."""
    docs_path = Path(__file__).parent.parent / "docs" / "AgentBeats" / "AGENTBEATS_REGISTRATION.md"
    assert docs_path.exists(), "AGENTBEATS_REGISTRATION.md must exist"


def test_extensibility_documentation_has_evaluator_interface_section():
    """Test that documentation explains evaluator interface pattern."""
    docs_path = Path(__file__).parent.parent / "docs" / "AgentBeats" / "AGENTBEATS_REGISTRATION.md"
    content = docs_path.read_text()

    assert "Evaluator Interface" in content, "Must document evaluator interface pattern"
    assert "evaluate" in content, "Must document evaluate method"


def test_extensibility_documentation_has_tier_structure():
    """Test that documentation explains tier-based evaluator structure."""
    docs_path = Path(__file__).parent.parent / "docs" / "AgentBeats" / "AGENTBEATS_REGISTRATION.md"
    content = docs_path.read_text()

    assert "Tier 1" in content, "Must document Tier 1 (Graph) evaluators"
    assert "Tier 2" in content, "Must document Tier 2 (LLM Judge + Latency) evaluators"
    assert "Tier 3" in content, "Must document Tier 3 (Text/Custom) evaluators"


def test_extensibility_documentation_has_integration_points():
    """Test that documentation describes integration points clearly."""
    docs_path = Path(__file__).parent.parent / "docs" / "AgentBeats" / "AGENTBEATS_REGISTRATION.md"
    content = docs_path.read_text()

    assert "Integration" in content or "Executor" in content, "Must describe integration points"
    assert "evaluate_all" in content or "pipeline" in content, "Must explain how to add evaluators"


def test_extensibility_documentation_has_example_evaluator():
    """Test that documentation provides example evaluator implementation."""
    docs_path = Path(__file__).parent.parent / "docs" / "AgentBeats" / "AGENTBEATS_REGISTRATION.md"
    content = docs_path.read_text()

    # Should have TextEvaluator as Tier 3 plugin example
    assert "TextEvaluator" in content or "Custom Evaluator" in content, "Must provide example evaluator"
    assert "class" in content and "evaluate" in content, "Must show example implementation code"


def test_extensibility_documentation_shows_executor_integration():
    """Test that documentation shows how to add new evaluator to Executor."""
    docs_path = Path(__file__).parent.parent / "docs" / "AgentBeats" / "AGENTBEATS_REGISTRATION.md"
    content = docs_path.read_text()

    assert "Executor" in content, "Must show Executor integration"
    assert "evaluate_all" in content or "_evaluate_" in content, "Must show evaluation methods"
