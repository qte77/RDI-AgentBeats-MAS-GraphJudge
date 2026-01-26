---
title: Contribution Guidelines
version: 1.0
applies-to: Agents and humans
purpose: Developer setup, workflow, and contribution guidelines
---

## Onboarding

New to this codebase? Start here:

| Area       | File                            | Purpose              |
| ---------- | ------------------------------- | -------------------- |
| Principles | `.claude/rules/core-principles` | KISS/DRY/YAGNI       |
| Agents     | `AGENTS.md`                     | Agent behavior       |
| Stories    | `docs/PRD.md`                   | 17 user stories      |
| Commands   | `Makefile`                      | Dev commands         |
| Skills     | `.claude/skills/`               | Task-specific agents |
| Settings   | `.claude/settings.json`         | Permissions, tools   |

---

## Development Setup

### Prerequisites

- `uv` package manager

### Initial Setup

```bash
# Install dependencies
uv sync

# Verify installation
make validate
```

---

## Development Workflow

### Standard Development

```bash
# Format and lint code
make ruff

# Type check
make type_check

# Run tests
make test_all

# Run all quality gates
make validate
```

### Quality Gates

All code must pass before committing:

- **ruff**: Code formatting and linting
- **pyright**: Static type checking
- **pytest**: Unit and integration tests

---

## Ralph-Loop Workflow

Ralph-loop enables autonomous task execution from PRD.md.

### Initialize Ralph

```bash
# First time setup (creates prd.json from PRD.md)
make ralph_init

# Check status
make ralph_status
```

### Run Ralph-Loop

```bash
# Run with default iterations (10)
make ralph

# Run custom iterations
make ralph ITERATIONS=5

# Monitor progress
cat docs/ralph/progress.txt
```

### How It Works

1. Ralph reads `docs/ralph/prd.json` (user stories)
2. Finds next incomplete story
3. Executes via Claude Code
4. Runs `make validate`
5. Commits changes and updates status

---

## Commit Conventions

### When to Commit

- After completing a logical unit of work
- When `make validate` passes
- When explicitly requested by user or Ralph-loop

### Commit Message Format

```text
<type>(<scope>): <subject>

<body>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Add or update tests
- `docs`: Documentation changes
- `chore`: Tooling, dependencies, config

**Example:**

```text
feat(evaluation): add graph metrics calculation

Implement NetworkX-based graph analysis for agent coordination quality.
Includes centrality, clustering, and path metrics.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Code Guidelines

### Core Principles

All code must follow `.claude/rules/core-principles.md`:

- **KISS** (Keep It Simple, Stupid): Simplest solution that works
- **DRY** (Don't Repeat Yourself): Single source of truth
- **YAGNI** (You Aren't Gonna Need It): Implement only what's requested

### Agent-Specific Guidelines

See `AGENTS.md` for agent behavioral requirements and task execution protocols.

### Python Best Practices

See `docs/best-practices/python-best-practices.md` for comprehensive Python standards.

---

## Project Structure

```text
.claude/          # Claude Code configuration
├── agents/       # Agent definitions
├── rules/        # Core principles
├── scripts/      # Ralph-loop scripts
└── skills/       # Task-specific agents

docs/
├── PRD.md        # Product requirements (17 user stories)
├── ralph/        # Ralph-loop task tracking
└── best-practices/  # Language-specific guidelines

src/agentbeats/   # Main package
tests/            # Test suite
```

---

## Getting Help

- **Documentation**: See `README.md`, `docs/PRD.md`, `AGENTS.md`
- **Issues**: Report bugs or request features via GitHub Issues
- **Claude Code**: Run `claude --help` for CLI usage
