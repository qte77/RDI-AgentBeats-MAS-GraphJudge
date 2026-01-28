---
title: Testing Strategy
version: 1.0
applies-to: Agents and humans
purpose: Testing guidelines aligned with KISS/DRY/YAGNI principles
---

## Core Principles Applied to Testing

Following project principles from `AGENTS.md` and `.claude/rules/core-principles.md`:

| Principle | Testing Application |
|-----------|---------------------|
| **KISS** | Test behavior, not implementation details |
| **DRY** | No duplicate coverage across tests |
| **YAGNI** | Don't test library behavior (Pydantic, FastAPI) |

## What to Test

### High-Value Tests (Keep)

1. **Business logic** - Coordination quality scoring, graph metrics computation
2. **Integration points** - A2A protocol handling, evaluator pipelines
3. **Edge cases with real impact** - Empty traces, error propagation
4. **Contracts** - API response formats, model transformations

### Low-Value Tests (Avoid)

1. **Library behavior** - Pydantic validation, os.environ reading
2. **Trivial assertions** - `x is not None`, `isinstance(x, SomeClass)`
3. **Structure checks** - `hasattr()`, `callable()`
4. **Default values** - Unless defaults encode business rules
5. **Documentation content** - String contains checks

## Test Architecture

```
pytest (deterministic)     hypothesis (edge cases)
        │                          │
        ▼                          ▼
┌─────────────────┐      ┌─────────────────┐
│ Core behavior   │      │ Property-based  │
│ Known inputs    │      │ Generated inputs│
│ Expected outputs│      │ Invariants hold │
└─────────────────┘      └─────────────────┘
```

### Pytest: Core Deterministic Tests

Use for:
- Known input/output pairs
- Specific scenarios from requirements
- Integration flows
- Regression tests

```python
async def test_graph_evaluator_detects_bottleneck():
    """Known hub-spoke pattern should detect bottleneck."""
    traces = build_hub_spoke_traces(hub="coordinator", spokes=["a", "b", "c"])

    evaluator = GraphEvaluator()
    metrics = evaluator.evaluate(traces)

    assert metrics.has_bottleneck
    assert "coordinator" in metrics.bottlenecks
```

### Hypothesis: Edge Cases and Invariants

Use for:
- Input validation boundaries
- Numeric computations (scores, metrics)
- Data transformations
- Format conversions

## Hypothesis Test Candidates

### 1. Graph Metrics Computation

```python
from hypothesis import given, strategies as st

@given(
    density=st.floats(min_value=0.0, max_value=1.0),
    node_count=st.integers(min_value=1, max_value=100),
)
def test_graph_density_bounds(density: float, node_count: int):
    """Graph density always in [0, 1] regardless of input."""
    traces = generate_traces_with_density(density, node_count)
    metrics = GraphEvaluator().evaluate(traces)

    assert 0.0 <= metrics.graph_density <= 1.0
```

### 2. Score Normalization

```python
@given(
    raw_scores=st.lists(st.floats(min_value=0, max_value=1000), min_size=1),
    max_score=st.floats(min_value=0.1, max_value=100),
)
def test_normalized_score_bounds(raw_scores: list[float], max_score: float):
    """Normalized scores always in [0, max_score]."""
    for raw in raw_scores:
        normalized = normalize_score(raw, max_score)
        assert 0.0 <= normalized <= max_score
```

### 3. Latency Percentiles

```python
@given(
    latencies=st.lists(st.floats(min_value=0, max_value=10000), min_size=1),
)
def test_percentile_ordering(latencies: list[float]):
    """p50 <= p95 <= p99 <= max for any latency distribution."""
    metrics = compute_latency_metrics(latencies)

    assert metrics.p50_latency <= metrics.p95_latency
    assert metrics.p95_latency <= metrics.p99_latency
    assert metrics.p99_latency <= metrics.max_latency
```

### 4. AgentBeats Output Format

```python
@given(
    overall_score=st.floats(min_value=0.0, max_value=1.0),
    coordination_quality=st.sampled_from(["low", "medium", "high"]),
)
def test_agentbeats_output_valid(overall_score: float, coordination_quality: str):
    """AgentBeats output always valid JSON with required fields."""
    output = AgentBeatsOutputModel.from_green_output(
        GreenAgentOutput(
            overall_score=overall_score,
            reasoning="test",
            coordination_quality=coordination_quality,
            strengths=[],
            weaknesses=[],
        ),
        agent_id="test-agent",
    )

    data = output.to_dict()
    assert "participants" in data
    assert "results" in data
    assert len(data["results"]) >= 1
```

### 5. Trace ID Uniqueness

```python
@given(
    task_count=st.integers(min_value=1, max_value=50),
)
def test_trace_ids_unique(task_count: int):
    """Each task execution generates unique trace ID."""
    executor = Executor()
    trace_ids = set()

    for _ in range(task_count):
        traces = executor.execute_task_sync(...)  # simplified
        for trace in traces:
            assert trace.trace_id not in trace_ids
            trace_ids.add(trace.trace_id)
```

### 6. Settings Environment Variables

```python
@given(
    port=st.integers(min_value=1, max_value=65535),
    host=st.from_regex(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"),
)
def test_settings_accept_valid_network_config(port: int, host: str):
    """Settings accept any valid port and IP."""
    with patch.dict(os.environ, {"GREEN_PORT": str(port), "GREEN_HOST": host}):
        settings = GreenSettings()
        assert settings.port == port
        assert settings.host == host
```

## Implementation Notes

### Adding Hypothesis

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "hypothesis>=6.0",
]
```

### Test Organization

```
tests/
├── test_*.py              # Pytest deterministic tests
├── properties/            # Hypothesis property tests
│   ├── test_graph_props.py
│   ├── test_score_props.py
│   └── test_format_props.py
└── conftest.py            # Shared fixtures
```

### Running Tests

```bash
# All tests
make test

# Only property tests
pytest tests/properties/ -v

# With hypothesis statistics
pytest tests/properties/ --hypothesis-show-statistics
```

## Recent Cleanup Results

### Removed Low-ROI Tests (6 files, ~300 lines)

| File | Reason |
|------|--------|
| `test_green_settings.py` | Tested pydantic-settings library |
| `test_purple_settings.py` | Tested pydantic-settings library |
| `test_openai_dependency.py` | Tested pip install |
| `test_extensibility_docs.py` | Tested markdown content |
| `test_demo_script.py` | Tested markdown content |
| `test_purple_models.py` | Tested Pydantic validation |

### Fixed Pre-existing Test Issues

| Test | Issue | Fix |
|------|-------|-----|
| `test_server_writes_results_to_output_file` | Expected old format | Updated to AgentBeats format |
| `test_agent_extensions_include_*` | Expected string, got dict | Access `ext["uri"]` |
| `test_executor_sends_message_via_messenger` | Expected 1 call, got 3 | Multi-round coordination |

### Current State

- **204 tests passing**
- **0 pyright errors** in src/
- Test suite runs in ~5 seconds

## Guidelines for New Tests

1. **Ask: Does this test behavior or implementation?**
   - Behavior: Keep
   - Implementation: Skip

2. **Ask: Would this catch a real bug?**
   - Yes: Keep
   - No: Skip

3. **Ask: Is this testing our code or a library?**
   - Our code: Keep
   - Library: Skip

4. **For edge cases: Consider Hypothesis**
   - Numeric bounds
   - String formats
   - Collection sizes
   - State transitions
