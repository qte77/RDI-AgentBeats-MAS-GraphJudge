"""STORY-033: Tests for docs/AgentBeats/CONFIGURATION.md existence and completeness."""

from pathlib import Path

CONFIGURATION_MD = Path(__file__).parent.parent / "docs" / "AgentBeats" / "CONFIGURATION.md"


def test_configuration_md_exists():
    """Acceptance: docs/AgentBeats/CONFIGURATION.md must be created."""
    assert CONFIGURATION_MD.exists(), "docs/AgentBeats/CONFIGURATION.md must exist"


def test_configuration_md_has_env_var_table():
    """Acceptance: Must include env var table with name, default, description, agent columns."""
    content = CONFIGURATION_MD.read_text()
    assert "| Name |" in content or "| Variable |" in content or "| Env Var |" in content
    assert "Default" in content
    assert "Description" in content
    assert "Agent" in content


def test_configuration_md_includes_green_settings():
    """Acceptance: Table must include all GreenSettings environment variables."""
    content = CONFIGURATION_MD.read_text()
    green_vars = [
        "GREEN_HOST",
        "GREEN_PORT",
        "GREEN_PURPLE_PORT",
        "GREEN_LOG_LEVEL",
        "GREEN_COORDINATION_ROUNDS",
        "GREEN_ROUND_DELAY_SECONDS",
        "GREEN_AGENT_VERSION",
        "GREEN_AGENT_DESCRIPTION",
        "GREEN_DOMAIN",
        "GREEN_MAX_SCORE",
        "GREEN_OUTPUT_FILE",
    ]
    for var in green_vars:
        assert var in content, f"GreenSettings var {var} missing from CONFIGURATION.md"


def test_configuration_md_includes_purple_settings():
    """Acceptance: Table must include all PurpleSettings environment variables."""
    content = CONFIGURATION_MD.read_text()
    purple_vars = [
        "PURPLE_HOST",
        "PURPLE_PORT",
        "PURPLE_LOG_LEVEL",
        "PURPLE_AGENT_NAME",
        "PURPLE_AGENT_DESCRIPTION",
        "PURPLE_AGENT_VERSION",
        "PURPLE_STATIC_PEERS",
        "PURPLE_GREEN_URL",
    ]
    for var in purple_vars:
        assert var in content, f"PurpleSettings var {var} missing from CONFIGURATION.md"


def test_configuration_md_includes_shared_vars():
    """Acceptance: Table must include shared validation_alias variables."""
    content = CONFIGURATION_MD.read_text()
    shared_vars = [
        "AGENT_UUID",
        "AGENT_NAME",
        "PURPLE_AGENT_URL",
    ]
    for var in shared_vars:
        assert var in content, f"Shared var {var} missing from CONFIGURATION.md"


def test_configuration_md_includes_llm_settings():
    """Acceptance: Table must include LLMSettings environment variables."""
    content = CONFIGURATION_MD.read_text()
    llm_vars = [
        "AGENTBEATS_LLM_API_KEY",
        "AGENTBEATS_LLM_BASE_URL",
        "AGENTBEATS_LLM_MODEL",
        "AGENTBEATS_LLM_TEMPERATURE",
    ]
    for var in llm_vars:
        assert var in content, f"LLMSettings var {var} missing from CONFIGURATION.md"


def test_configuration_md_includes_a2a_settings():
    """Acceptance: Table must include A2ASettings environment variables."""
    content = CONFIGURATION_MD.read_text()
    a2a_vars = [
        "AGENTBEATS_A2A_TIMEOUT",
        "AGENTBEATS_A2A_CONNECT_TIMEOUT",
    ]
    for var in a2a_vars:
        assert var in content, f"A2ASettings var {var} missing from CONFIGURATION.md"


def test_configuration_md_includes_usage_examples():
    """Acceptance: Documentation must include usage examples."""
    content = CONFIGURATION_MD.read_text()
    # Usage examples section should be present
    has_example_section = (
        "## Usage" in content
        or "## Example" in content
        or "```" in content
    )
    assert has_example_section, "CONFIGURATION.md must include usage examples"


def test_configuration_md_includes_troubleshooting():
    """Acceptance: Documentation must include troubleshooting guidance."""
    content = CONFIGURATION_MD.read_text()
    has_troubleshooting = (
        "Troubleshooting" in content
        or "troubleshoot" in content.lower()
        or "## Common" in content
        or "## FAQ" in content
    )
    assert has_troubleshooting, "CONFIGURATION.md must include troubleshooting guidance"
