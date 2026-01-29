---
title: TDD Best Practices
version: 1.0
based-on: Industry research 2025-2026
see-also: testing-strategy.md
---

## Test-Driven Development (TDD)

TDD is a development methodology where tests are written before implementation code, driving design and ensuring testability from the start.

## The Red-Green-Refactor Cycle

```
┌─────────────┐
│  1. RED     │  Write a failing test
│             │  (test what should happen)
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  2. GREEN   │  Write minimal code to pass
│             │  (make it work)
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  3. REFACTOR│  Improve code quality
│             │  (make it clean)
└─────┬───────┘
      │
      └──────> Repeat
```

## Core Practices

### 1. Write Tests First

**Why**: Enforces modular, decoupled code with clear interfaces

```python
# RED: Write failing test first
def test_green_executor_collects_trace_id():
    executor = Executor()
    traces = await executor.execute_task("task", messenger, url)
    assert all(trace.trace_id for trace in traces)
```

**Then** implement minimal code to pass.

### 2. Use Arrange-Act-Assert (AAA)

Structure every test in three phases:

```python
def test_graph_evaluator_detects_bottleneck():
    # ARRANGE - Set up test data
    traces = build_hub_spoke_traces(hub="coordinator", spokes=["a", "b", "c"])
    evaluator = GraphEvaluator()

    # ACT - Execute the behavior
    metrics = evaluator.evaluate(traces)

    # ASSERT - Verify the outcome
    assert metrics.has_bottleneck
    assert "coordinator" in metrics.bottlenecks
```

### 3. Keep Tests Atomic and Isolated

**One behavior per test**:
```python
# GOOD - Tests one thing
def test_executor_generates_unique_trace_ids():
    # Test only trace ID uniqueness

def test_executor_records_latency():
    # Test only latency recording
```

**Not this**:
```python
# BAD - Tests multiple things
def test_executor_everything():
    # Tests trace IDs, latency, parent links, etc.
```

### 4. Test Edge Cases Before Happy Paths

Cover failure modes first, then success:

```python
# 1. Edge cases first
def test_evaluator_handles_empty_traces():
    assert evaluator.evaluate([]) == default_metrics

def test_evaluator_handles_single_trace():
    assert evaluator.evaluate([trace]) == expected

# 2. Then happy path
def test_evaluator_computes_metrics():
    assert evaluator.evaluate(traces) == full_metrics
```

### 5. Descriptive Test Names

Name should describe the behavior being tested:

```python
# GOOD - Clear behavior
test_green_server_returns_404_for_unknown_endpoint()
test_purple_messenger_retries_on_connection_failure()

# BAD - Vague or implementation-focused
test_server_response()
test_messenger_method()
```

## Benefits of TDD

**Design quality**: Forces modular, testable code with clear interfaces

**Fast feedback**: Catches bugs immediately while context is fresh

**Refactoring confidence**: Tests enable safe code improvements

**Living documentation**: Tests describe how the system behaves

**Defect reduction**: Studies show 40-90% reduction in defect density

## TDD Anti-Patterns to Avoid

**Testing implementation details**:
```python
# BAD - Tests internal structure
def test_evaluator_uses_networkx():
    assert isinstance(evaluator._graph, nx.DiGraph)

# GOOD - Tests behavior
def test_evaluator_detects_bottlenecks():
    assert evaluator.evaluate(traces).has_bottleneck
```

**Overly complex tests**:
```python
# BAD - Test is harder to understand than code
def test_with_mocks_everywhere():
    with mock.patch(...) as m1:
        with mock.patch(...) as m2:
            # 50 lines of setup

# GOOD - Simple, clear test
def test_behavior_directly():
    result = function(input)
    assert result == expected
```

**Chasing 100% coverage**: Aim for meaningful coverage of behaviors, not line coverage percentage

## AI-Assisted TDD (2025-2026)

Modern TDD integrates AI for efficiency:

**AI drafts tests** (~70% of happy-path tests):
```python
# AI generates starter test
def test_new_feature():
    # AI-generated arrange/act/assert structure
```

**Human focuses on**:
- Edge cases AI might miss
- Business logic intent
- Complex scenarios
- Test quality and clarity

**Not AI replacement**: AI accelerates TDD but doesn't replace the Red-Green-Refactor discipline

## When to Use TDD

**Use TDD for**:
- Business logic (coordination scoring, graph metrics)
- Algorithms (latency calculations, percentiles)
- Data transformations (model conversions)
- Edge case handling (empty inputs, nulls)

**Consider alternatives for**:
- Simple CRUD operations
- UI layouts (use visual testing)
- Exploratory prototypes (add tests after)

## Integration with This Project

Current project uses TDD for:
- Green/Purple agent unit tests
- Evaluator pipeline tests
- Model transformation tests

See `tests/` directory for examples.

## References

- [Test-Driven Development Guide 2026](https://monday.com/blog/rnd/test-driven-development-tdd/)
- [AI-Powered TDD 2025](https://www.nopaccelerate.com/test-driven-development-guide-2025/)
- [TDD Practical Guide](https://brainhub.eu/library/test-driven-development-tdd)
