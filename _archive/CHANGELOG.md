<!-- markdownlint-disable MD024 no-duplicate-heading -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Types of changes**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## [Unreleased]

### Added

**Core GreenAgent Implementation**:

- A2A-compliant messenger with trace capture (`src/agentbeats/messenger.py`)
- Graph evaluator with NetworkX metrics (`src/agentbeats/evals/graph.py`)
- LLM judge evaluator for qualitative assessment (`src/agentbeats/evals/llm_judge.py`)
- Text metrics plugin for similarity scoring (`src/agentbeats/evals/text_metrics.py`)
- Agent orchestrator coordinating evaluation flow (`src/agentbeats/agent.py`)
- A2A server with CLI args support (`src/agentbeats/server.py`)
- Executor module for task lifecycle management (`src/agentbeats/executor.py`)
- Dockerfile for containerized deployment (linux/amd64)

**Baseline Purple Agent** (`examples/purple-agent/`):

- A2A-compliant demo agent for evaluation scenarios
- AgentCard endpoint at `/.well-known/agent-card.json`
- Docker containerization with CLI args (`--host`, `--port`, `--card-url`)
- Simple coordination response capabilities

**Platform Integration**:

- AgentBeats platform registration guide (`docs/PLATFORM_SETUP.md`)
- Leaderboard repository setup with DuckDB query (`docs/leaderboard_query.sql`)
- GitHub Container Registry deployment instructions
- Scenario configuration example (`docs/scenario.toml.example`)

**Reproducibility Framework**:

- Automated reproducibility testing script (`scripts/test_reproducibility.py`)
- Comprehensive variance analysis documenting 0% variance (`docs/REPRODUCIBILITY.md`)
- Statistical methodology with 5 independent evaluation runs
- Raw test data (`reproducibility-results/reproducibility-*.json`)

**Competition Submission**:

- Abstract (243 words) describing GreenAgent value proposition (`docs/ralph-results/ABSTRACT.md`)
- Demo video script with 3-minute outline (`docs/DEMO_SCRIPT.md`)
- Purple agent evaluation script (`scripts/evaluate_purple_agent.py`)

**Development Tooling**:

- Makefile targets: `run_agent`, `build_agent`, `test_agent`
- Ralph loop integration for autonomous development
- Comprehensive test suite with TDD approach
