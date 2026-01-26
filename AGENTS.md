---
title: Agent Guidelines
version: 1.0
applies-to: all-agents
purpose: Agent behavioral guidelines and task execution protocol
---

## Quick Start

For development setup, commands, and workflow, see **CONTRIBUTING.md**.

This document covers agent-specific behavioral requirements.

---

## Agent Neutrality Requirements

All agents must maintain strict neutrality in technology decisions:

### Technology Agnosticism

- **No vendor lock-in**: Avoid assuming specific cloud providers, proprietary
  services, or closed ecosystems
- **Framework neutrality**: Choose frameworks based on project requirements,
  not personal preference
- **Evidence-based selection**: Justify technology choices with concrete
  requirements from PRD.md or user stories

### Decision Framework

1. **Read requirements first**: Extract constraints and preferences from
   PRD.md, user stories, or task descriptions
2. **Use existing choices**: When tech stack is already defined (e.g., in
   `pyproject.toml`, `package.json`), use it
3. **Propose alternatives only when**: Current stack blocks requirements or has
   documented deficiencies
4. **Document rationale**: Explain technology decisions with evidence, not
   opinions

### Prohibited Behaviors

- Recommending technologies not mentioned in requirements
- Assuming cloud deployment targets without specification
- Adding frameworks/libraries speculatively (violates YAGNI)
- Choosing tools based on "industry trends" or "best practices" without
  requirement-driven justification

---

## Task Execution Protocol

### Pre-Task Checklist

1. **Read scope documents**:
   - Primary: PRD.md user story or task description
   - Context: CLAUDE.md, existing code patterns
   - Standards: Python best practices (`.claude/skills/implementing-python/SKILL.md`)

2. **Validate scope**:
   - Does task match assigned story/issue?
   - Are acceptance criteria clear?
   - Do I have all required context?

3. **Identify existing patterns**:
   - Search for similar implementations
   - Reuse existing abstractions (DRY principle)
   - Match code style and conventions

### During Execution

- **Minimal changes**: Touch only files directly related to task
- **No speculative features**: Implement exactly what's requested (YAGNI)
- **Quality gates**: Run `make validate` before marking complete
- **Incremental commits**: Commit after each logical unit of work (when user
  requests)

### Completion Criteria

- [ ] All acceptance criteria met
- [ ] All quality gates pass (see CONTRIBUTING.md)
- [ ] No new technical debt introduced
- [ ] Documentation updated if APIs changed

---

## Compliance Checklist

Quick reference for mandatory agent behaviors:

- [ ] Follow all principles in `.claude/rules/core-principles.md` (KISS/DRY/YAGNI)
- [ ] Follow skill-specific guidance (`.claude/skills/*.md`)
- [ ] Commit only when explicitly requested by user or Ralph-loop
- [ ] Keep code comments minimal (code should be self-explanatory)
- [ ] Add docstrings only for public APIs
