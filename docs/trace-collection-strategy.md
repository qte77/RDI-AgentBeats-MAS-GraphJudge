---
title: Trace Collection Strategy
status: Design Decision - Not Yet Implemented
related: src/green/executor.py:20-28
---

## Current State

The executor uses a **fixed-rounds placeholder** approach for testing:

- `DEFAULT_COORDINATION_ROUNDS = 3`
- `ROUND_DELAY_SECONDS = 0.1`
- Implemented at `src/green/executor.py:26-28`

This is marked with TODO/FIXME as insufficient for real multi-agent coordination.

## The Problem

Fixed rounds don't reflect real coordination behavior:

- **No adaptivity**: Simple tasks waste cycles, complex tasks get cut off
- **No completion detection**: Can't tell when coordination actually finishes
- **Arbitrary timing**: 0.1s delays don't match real coordination patterns

## Strategy Options

### 1. Task Completion Signal (Preferred for Production)

Purple agent sends explicit "done" indicator when coordination complete.

**Pros**:

- Most accurate - stops exactly when coordination finishes
- No wasted collection cycles
- No risk of premature termination

**Cons**:

- Requires A2A protocol extension or status field usage
- Agents must implement completion signaling

### 2. Timeout-Based (Safety Mechanism)

Collect for maximum N seconds (e.g., 30s).

**Pros**:

- Prevents infinite collection
- Simple to implement
- Good safety fallback

**Cons**:

- May miss late interactions if timeout too short
- Wastes time if timeout too long

### 3. Idle Detection (Adaptive)

Stop after N seconds of no new messages (e.g., 5s idle threshold).

**Pros**:

- Adapts naturally to task complexity
- No protocol changes needed
- Works with any agent implementation

**Cons**:

- May terminate during legitimate coordination pauses
- Requires tuning idle threshold

### 4. Message Count Threshold

Stop after N total interactions observed.

**Pros**:

- Simple to implement

**Cons**:

- Arbitrary like fixed rounds
- No adaptivity to task complexity

## Recommended Approach

**Hybrid strategy** combining:

1. **Task completion signals** (primary detection)
2. **Timeout** (safety limit)
3. **Idle detection** (adaptive fallback)

```python
# Pseudocode
while not (task_complete or timeout_exceeded or idle_too_long):
    collect_traces()
```

Configuration example:

```python
TraceCollectionConfig(
    max_timeout_seconds=30,      # Safety limit
    idle_threshold_seconds=5,    # Adaptive fallback
    use_completion_signals=True  # Primary mechanism
)
```

## Implementation Considerations

### Protocol Changes

To support task completion signals:

- Option A: Add `status: "complete"` field to A2A responses
- Option B: Define new message type for coordination completion
- Option C: Use HTTP status codes (e.g., 204 No Content for "done")

### Backward Compatibility

Hybrid approach gracefully degrades:

- If agent supports completion signals → use them
- If not → fall back to idle detection + timeout
- Current fixed-rounds behavior is special case (timeout=0, idle=0, rounds=3)

### Configuration

Make strategy configurable per execution:

```python
executor = Executor(
    collection_strategy=TraceCollectionStrategy.HYBRID,
    config=TraceCollectionConfig(...)
)
```

## Impact on Evaluation

**Current fixed-rounds is adequate for**:

- Testing graph construction logic
- Validating evaluation metrics computation
- Unit and integration tests

**Production deployment requires adaptive strategy for**:

- Diverse multi-agent coordination patterns
- Tasks with varying complexity
- Real-world timing and message volumes

## Next Steps (When Implementing)

1. Define A2A protocol extension for completion signals
2. Implement hybrid collection strategy in `Executor`
3. Add configuration model `TraceCollectionConfig`
4. Update Purple agent to send completion signals
5. Add tests for each strategy component
6. Document configuration in environment setup guide

## References

- Current implementation: `src/green/executor.py:20-28`
- Executor execution loop: `src/green/executor.py:42-109`
- Related: AgentBeats evaluation requirements
