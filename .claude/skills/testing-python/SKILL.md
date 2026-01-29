---
name: testing-python
description: Writes tests following TDD/BDD/Property testing best practices. Use when writing unit tests, integration tests, or BDD scenarios.
argument-hint: [test-scope or component-name]
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# Python Testing

**Target**: $ARGUMENTS

Writes **focused, behavior-driven tests** following project testing strategy.

## Testing Strategy

See `docs/best-practices/`:
- **testing-strategy.md** - Overall strategy, what to test, decision checklist
- **tdd-best-practices.md** - TDD methodology (Red-Green-Refactor)
- **bdd-best-practices.md** - BDD methodology (Given-When-Then)

## Quick Decision Tree

**Default: Use TDD for all tests**

```
Writing a test?
├─ Unit test / Business logic → TDD (Red-Green-Refactor) ← DEFAULT
├─ Edge cases / Numeric bounds → Property Testing (Hypothesis)
└─ Acceptance criteria / Stakeholder docs → BDD (optional, future)
```

**Current project uses TDD** for 204 passing tests.

## TDD Workflow (Unit Tests)

**Red-Green-Refactor cycle**:

1. **RED** - Write failing test first
   ```python
   def test_green_executor_generates_unique_trace_ids():
       executor = Executor()
       traces = await executor.execute_task(...)
       trace_ids = [t.trace_id for t in traces]
       assert len(trace_ids) == len(set(trace_ids))  # All unique
   ```

2. **GREEN** - Write minimal code to pass

3. **REFACTOR** - Improve while keeping tests green

**Structure**: Arrange-Act-Assert (AAA)
```python
def test_graph_evaluator_detects_bottleneck():
    # ARRANGE
    traces = build_hub_spoke_traces(hub="coordinator", spokes=["a", "b", "c"])
    evaluator = GraphEvaluator()

    # ACT
    metrics = evaluator.evaluate(traces)

    # ASSERT
    assert metrics.has_bottleneck
    assert "coordinator" in metrics.bottlenecks
```

## BDD Workflow (Optional - Future Use)

**Note**: BDD not currently used in this project. Consider for acceptance testing if needed.

**Given-When-Then scenarios**:

```gherkin
# tests/acceptance/features/evaluation.feature (FUTURE)
Feature: Green Agent Evaluation
  Scenario: Detect coordination bottleneck
    Given a hub-spoke coordination pattern
      And coordinator agent "green-hub"
      And worker agents "worker-1", "worker-2", "worker-3"
    When the evaluator analyzes interaction traces
    Then it should detect a bottleneck
      And "green-hub" should be identified as the bottleneck
```

See `docs/best-practices/bdd-best-practices.md` for full methodology.

## Property Testing (Edge Cases)

**Hypothesis for invariants**:

```python
from hypothesis import given, strategies as st

@given(latencies=st.lists(st.floats(0, 10000), min_size=1))
def test_percentile_ordering(latencies: list[float]):
    """p50 ≤ p95 ≤ p99 ≤ max for any latency distribution."""
    m = compute_latency_metrics(latencies)
    assert m.p50_latency <= m.p95_latency <= m.p99_latency <= m.max_latency
```

## What to Test (KISS/DRY/YAGNI)

**High-Value**:
- Business logic (coordination scoring, graph metrics)
- Integration points (A2A protocol, evaluator pipelines)
- Edge cases (empty traces, boundary conditions)
- Contracts (API formats, model transformations)

**Low-Value** (Avoid):
- Library behavior (Pydantic validation, framework internals)
- Trivial assertions (`x is not None`, `isinstance()`)
- Implementation details (internal structure, private methods)

## Naming Convention

**Format**: `test_{agent}_{component}_{behavior}`

```python
test_green_executor_collects_interaction_traces()
test_purple_messenger_sends_a2a_messages()
test_graph_density_bounds()  # Property test
```

## Execution Steps

1. **Write TDD test** (default approach):
   - RED: Write failing test
   - GREEN: Minimal code to pass
   - REFACTOR: Improve while green

2. **Run tests**:
   ```bash
   make test              # All tests (current: 204 passing)
   pytest tests/ -v       # All tests with verbose output
   pytest -k test_green_  # Filter by pattern
   ```

3. **Fix failures** and iterate

4. **Verify coverage** (behavior coverage, not line coverage)

**Optional approaches** (when appropriate):
- Property testing for edge cases: `pytest tests/properties/ -v`
- BDD scenarios (future): `pytest tests/acceptance/ -v`

## Test Organization

**Current** (TDD focus):
```
tests/
├── test_*.py             # TDD unit tests (204 passing)
└── conftest.py           # Shared fixtures
```

**Future expansion** (when needed):
```
tests/
├── unit/                 # TDD unit tests (organize when >300 tests)
├── properties/           # Hypothesis property tests (add when needed)
├── acceptance/           # BDD scenarios (optional)
└── conftest.py          # Shared fixtures
```

## Quality Gates

Before completing:
- [ ] All tests pass (`make test`)
- [ ] Tests follow TDD Red-Green-Refactor cycle
- [ ] Tests use Arrange-Act-Assert structure
- [ ] Tests follow naming convention (`test_{agent}_{component}_{behavior}`)
- [ ] Tests are behavior-focused (not implementation)
- [ ] No library behavior tested
- [ ] No trivial assertions
