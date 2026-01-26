"""Tests for Docker container build and functionality."""

import pytest


@pytest.mark.integration
def test_dockerfile_exists():
    """Verify Dockerfile exists at project root."""
    from pathlib import Path

    dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
    assert dockerfile_path.exists(), "Dockerfile must exist at project root"

    # Read and verify basic structure
    content = dockerfile_path.read_text()
    assert "FROM" in content, "Dockerfile must contain FROM instruction"
    assert "linux/amd64" in content, "Dockerfile must target linux/amd64 architecture"
    assert "ENTRYPOINT" in content, "Dockerfile must define ENTRYPOINT"
    assert "agentbeats.server" in content, "Dockerfile must run agentbeats.server module"
    assert "EXPOSE 9009" in content, "Dockerfile must expose port 9009"


@pytest.mark.integration
def test_dockerignore_exists():
    """Verify .dockerignore exists for optimized builds."""
    from pathlib import Path

    dockerignore_path = Path(__file__).parent.parent / ".dockerignore"
    assert dockerignore_path.exists(), ".dockerignore must exist at project root"

    content = dockerignore_path.read_text()
    # Verify it excludes common unnecessary files
    assert "tests/" in content or "tests" in content, ".dockerignore should exclude tests"
    assert ".git" in content, ".dockerignore should exclude .git directory"
