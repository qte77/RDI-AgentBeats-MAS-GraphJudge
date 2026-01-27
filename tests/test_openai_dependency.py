"""Tests for STORY-004: OpenAI dependency configuration.

Validates:
- openai>=1.0 is present in pyproject.toml
- Dependency installs successfully
- OpenAI client can be imported
"""

import subprocess
import tomllib
from pathlib import Path


def test_openai_in_pyproject():
    """Verify openai>=1.0 is declared in pyproject.toml dependencies."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    dependencies = pyproject["project"]["dependencies"]
    openai_dep = [dep for dep in dependencies if dep.startswith("openai")]

    assert len(openai_dep) == 1, "openai dependency not found in pyproject.toml"
    assert openai_dep[0] == "openai>=1.0", f"Expected 'openai>=1.0', got '{openai_dep[0]}'"


def test_openai_installs_successfully():
    """Verify dependency installs successfully with uv sync."""
    result = subprocess.run(
        ["uv", "sync", "--frozen"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"uv sync failed: {result.stderr}"


def test_openai_import():
    """Verify OpenAI client can be imported from openai package."""
    try:
        from openai import OpenAI  # noqa: F401
    except ImportError as e:
        raise AssertionError(f"Failed to import OpenAI: {e}") from e
