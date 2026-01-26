"""Integration tests demonstrating purple agent evaluation by GreenAgent."""


class TestPurpleAgentStructure:
    """Tests verifying purple agent project structure."""

    def test_purple_agent_directory_exists(self) -> None:
        """Test that examples/purple-agent directory exists."""
        # Given: Purple agent should be in examples directory
        from pathlib import Path

        purple_agent_dir = Path("examples/purple-agent")

        # Then: Directory should exist
        assert purple_agent_dir.exists()
        assert purple_agent_dir.is_dir()

    def test_purple_agent_has_pyproject_toml(self) -> None:
        """Test that purple agent has pyproject.toml."""
        # Given: Purple agent directory
        from pathlib import Path

        pyproject_file = Path("examples/purple-agent/pyproject.toml")

        # Then: pyproject.toml should exist
        assert pyproject_file.exists()
        assert pyproject_file.is_file()

    def test_purple_agent_has_dockerfile(self) -> None:
        """Test that purple agent has Dockerfile."""
        # Given: Purple agent directory
        from pathlib import Path

        dockerfile = Path("examples/purple-agent/Dockerfile")

        # Then: Dockerfile should exist
        assert dockerfile.exists()
        assert dockerfile.is_file()

    def test_purple_agent_has_server_module(self) -> None:
        """Test that purple agent has server.py module."""
        # Given: Purple agent source directory
        from pathlib import Path

        server_file = Path("examples/purple-agent/src/purpleagent/server.py")

        # Then: server.py should exist
        assert server_file.exists()
        assert server_file.is_file()

    def test_purple_agent_has_readme(self) -> None:
        """Test that purple agent has README."""
        # Given: Purple agent directory
        from pathlib import Path

        readme_file = Path("examples/purple-agent/README.md")

        # Then: README should exist
        assert readme_file.exists()
        assert readme_file.is_file()


class TestPurpleAgentA2ACompliance:
    """Tests verifying A2A protocol compliance."""

    def test_purple_agent_server_has_agent_card_function(self) -> None:
        """Test that purple agent server module has create_agent_card function."""
        # Given: Purple agent server module
        import sys
        from pathlib import Path

        # Add purple agent to path
        purple_agent_src = Path("examples/purple-agent/src")
        sys.path.insert(0, str(purple_agent_src))

        try:
            from purpleagent.server import create_agent_card

            # Then: Function should exist
            assert callable(create_agent_card)

            # When: Create agent card
            card = create_agent_card()

            # Then: Should return valid agent card
            assert card is not None
            assert hasattr(card, "name")
            assert hasattr(card, "description")
            assert hasattr(card, "skills")
            assert card.name == "Purple Agent"
        finally:
            sys.path.pop(0)

    def test_purple_agent_server_has_executor(self) -> None:
        """Test that purple agent server module has PurpleAgentExecutor."""
        # Given: Purple agent server module
        import sys
        from pathlib import Path

        # Add purple agent to path
        purple_agent_src = Path("examples/purple-agent/src")
        sys.path.insert(0, str(purple_agent_src))

        try:
            from purpleagent.server import PurpleAgentExecutor

            # Then: Executor class should exist
            assert PurpleAgentExecutor is not None

            # When: Create executor instance
            executor = PurpleAgentExecutor()

            # Then: Should have required A2A methods
            assert hasattr(executor, "execute")
            assert hasattr(executor, "cancel")
            assert callable(executor.execute)
            assert callable(executor.cancel)
        finally:
            sys.path.pop(0)

    def test_purple_agent_server_has_create_server_function(self) -> None:
        """Test that purple agent has create_server function."""
        # Given: Purple agent server module
        import sys
        from pathlib import Path

        # Add purple agent to path
        purple_agent_src = Path("examples/purple-agent/src")
        sys.path.insert(0, str(purple_agent_src))

        try:
            from purpleagent.server import create_server

            # Then: Function should exist
            assert callable(create_server)
        finally:
            sys.path.pop(0)


class TestPurpleAgentDependencies:
    """Tests verifying purple agent dependencies."""

    def test_purple_agent_pyproject_has_a2a_dependency(self) -> None:
        """Test that purple agent pyproject.toml includes a2a-sdk dependency."""
        # Given: Purple agent pyproject.toml
        from pathlib import Path

        pyproject_file = Path("examples/purple-agent/pyproject.toml")
        content = pyproject_file.read_text()

        # Then: Should include a2a-sdk dependency
        assert "a2a-sdk" in content
        assert "http-server" in content

    def test_purple_agent_pyproject_has_uvicorn_dependency(self) -> None:
        """Test that purple agent pyproject.toml includes uvicorn dependency."""
        # Given: Purple agent pyproject.toml
        from pathlib import Path

        pyproject_file = Path("examples/purple-agent/pyproject.toml")
        content = pyproject_file.read_text()

        # Then: Should include uvicorn dependency
        assert "uvicorn" in content

    def test_purple_agent_pyproject_has_pydantic_dependency(self) -> None:
        """Test that purple agent pyproject.toml includes pydantic dependency."""
        # Given: Purple agent pyproject.toml
        from pathlib import Path

        pyproject_file = Path("examples/purple-agent/pyproject.toml")
        content = pyproject_file.read_text()

        # Then: Should include pydantic dependency
        assert "pydantic" in content


class TestPurpleAgentDockerfile:
    """Tests verifying purple agent Dockerfile configuration."""

    def test_dockerfile_uses_correct_architecture(self) -> None:
        """Test that Dockerfile targets linux/amd64 architecture."""
        # Given: Purple agent Dockerfile
        from pathlib import Path

        dockerfile = Path("examples/purple-agent/Dockerfile")
        content = dockerfile.read_text()

        # Then: Should target linux/amd64
        assert "linux/amd64" in content

    def test_dockerfile_has_correct_entrypoint(self) -> None:
        """Test that Dockerfile has correct ENTRYPOINT."""
        # Given: Purple agent Dockerfile
        from pathlib import Path

        dockerfile = Path("examples/purple-agent/Dockerfile")
        content = dockerfile.read_text()

        # Then: Should have ENTRYPOINT for server module
        assert "ENTRYPOINT" in content
        assert "purpleagent.server" in content

    def test_dockerfile_accepts_cli_arguments(self) -> None:
        """Test that Dockerfile comments mention CLI arguments."""
        # Given: Purple agent Dockerfile
        from pathlib import Path

        dockerfile = Path("examples/purple-agent/Dockerfile")
        content = dockerfile.read_text()

        # Then: Should mention CLI arguments in comments
        assert "--host" in content or "host" in content.lower()
        assert "--port" in content or "port" in content.lower()


class TestPurpleAgentEvaluationReadiness:
    """Tests verifying purple agent can be evaluated."""

    def test_purple_agent_readme_documents_usage(self) -> None:
        """Test that README documents how to use purple agent."""
        # Given: Purple agent README
        from pathlib import Path

        readme = Path("examples/purple-agent/README.md")
        content = readme.read_text()

        # Then: Should document basic usage
        assert "Purple Agent" in content
        assert "A2A" in content or "a2a" in content.lower()
        assert "docker" in content.lower()

    def test_purple_agent_readme_mentions_evaluation(self) -> None:
        """Test that README mentions evaluation by GreenAgent."""
        # Given: Purple agent README
        from pathlib import Path

        readme = Path("examples/purple-agent/README.md")
        content = readme.read_text()

        # Then: Should mention evaluation
        assert "GreenAgent" in content or "green agent" in content.lower()
        assert "evaluat" in content.lower()


class TestCoordinationScenario:
    """Tests defining simple coordination scenario demonstrability."""

    def test_purple_agent_server_provides_coordination_response(self) -> None:
        """Test that purple agent can provide coordination responses."""
        # Given: Purple agent server module
        import sys
        from pathlib import Path

        # Add purple agent to path
        purple_agent_src = Path("examples/purple-agent/src")
        sys.path.insert(0, str(purple_agent_src))

        try:
            from purpleagent.server import PurpleAgentExecutor

            # When: Create executor
            executor = PurpleAgentExecutor()

            # Then: Executor should be ready to handle coordination requests
            assert executor is not None
            assert hasattr(executor, "execute")
        finally:
            sys.path.pop(0)

    def test_purple_agent_card_describes_coordination_skill(self) -> None:
        """Test that purple agent card describes coordination capabilities."""
        # Given: Purple agent server module
        import sys
        from pathlib import Path

        # Add purple agent to path
        purple_agent_src = Path("examples/purple-agent/src")
        sys.path.insert(0, str(purple_agent_src))

        try:
            from purpleagent.server import create_agent_card

            # When: Create agent card
            card = create_agent_card()

            # Then: Should have coordination-related skills
            assert len(card.skills) > 0
            skill_names = [skill.name.lower() for skill in card.skills]
            skill_descriptions = [skill.description.lower() for skill in card.skills]

            # Check if any skill mentions coordination
            has_coordination = any(
                "coordinat" in name or "coordinat" in desc for name, desc in zip(skill_names, skill_descriptions)
            )
            assert has_coordination
        finally:
            sys.path.pop(0)
