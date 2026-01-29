---
title: Testing Strategy
version: 3.0
applies-to: Agents and humans
purpose: High-level testing strategy aligned with KISS/DRY/YAGNI
see-also: tdd-best-practices.md, bdd-best-practices.md
---

## Core Principles

| Principle | Testing Application |
| ----------- | --------------------- |
| **KISS** | Test behavior, not implementation details |
| **DRY** | No duplicate coverage across tests |
| **YAGNI** | Don't test library behavior (Pydantic, FastAPI) |

## What to Test

**High-Value** (Test these):

1. Business logic - Coordination quality scoring, graph metrics computation
2. Integration points - A2A protocol handling, evaluator pipelines
3. Edge cases with real impact - Empty traces, error propagation, boundary conditions
4. Contracts - API response formats, model transformations

**Low-Value** (Avoid these):

1. Library behavior - Pydantic validation, `os.environ` reading, framework internals
2. Trivial assertions - `x is not None`, `isinstance(x, SomeClass)`, `hasattr()`, `callable()`
3. Default values - Unless defaults encode business rules
4. Documentation content - String contains checks

## Testing Approach

### Three-Tier Strategy

```text
TDD (unit)           BDD (acceptance)      Property (edge cases)
     │                      │                      │
     ▼                      ▼                      ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│ Red-Green    │    │ Given-When   │    │ Hypothesis       │
│ -Refactor    │    │ -Then        │    │ Invariants       │
│ Unit tests   │    │ Scenarios    │    │ Generated inputs │
└──────────────┘    └──────────────┘    └──────────────────┘
```

**TDD** - Unit tests, fast feedback, design driver (see `tdd-best-practices.md`)

**BDD** - Acceptance criteria, stakeholder communication, living docs (see `bdd-best-practices.md`)

**Property Testing** - Hypothesis for numeric bounds, invariants, edge cases

### Priority Test Areas

1. **Core business logic** - Graph metrics, coordination scoring, evaluator pipelines
2. **API contracts** - A2A protocol, AgentCard format, JSON-RPC handling
3. **Edge cases** - Empty/null inputs, boundary values, numeric stability
4. **Integration points** - Green-Purple E2E, LLM connectivity, AgentBeats output

## Test Organization

```text
tests/
├── unit/                  # TDD unit tests (pytest)
│   ├── test_green_*.py
│   └── test_purple_*.py
├── acceptance/            # BDD scenarios (pytest-bdd or behave)
│   ├── features/*.feature
│   └── step_defs/
├── properties/            # Property tests (hypothesis)
│   ├── test_graph_props.py
│   └── test_score_props.py
└── conftest.py           # Shared fixtures
```

## Naming Conventions

**Format**: `test_{agent}_{component}_{behavior}`

```python
# Unit tests
test_green_executor_collects_interaction_traces()
test_purple_messenger_sends_a2a_messages()

# Property tests
test_graph_density_bounds()
test_percentile_ordering()
```

**Benefits**: Clear ownership, easier filtering (`pytest -k test_green_`), better organization

## Decision Checklist

Before writing a test, ask:

1. Does this test **behavior** (keep) or **implementation** (skip)?
2. Would this catch a **real bug** (keep) or is it **trivial** (skip)?
3. Is this testing **our code** (keep) or **a library** (skip)?
4. Which approach: **TDD** (unit), **BDD** (acceptance), or **Property** (edge cases)?

## References

- TDD practices: `docs/best-practices/tdd-best-practices.md`
- BDD practices: `docs/best-practices/bdd-best-practices.md`
- Current test suite: `tests/` (204 passing tests, ~5s runtime)
