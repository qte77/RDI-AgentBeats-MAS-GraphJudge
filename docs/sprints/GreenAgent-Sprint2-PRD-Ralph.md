---
title: Product Requirements Document - Green Agent Sprint 2
version: 2.0
applies-to: Agents and humans
purpose: Sprint 2 - Adaptive trace collection, settings consolidation, extensibility docs, real integration tests
---

> See [GreenAgent-UserStory.md](../GreenAgent-UserStory.md) for vision and value proposition.
>
> **Scope**: Sprint 2 builds on Sprint 1 (STORY-001 to STORY-023). Purple Agent Sprint 1 stories
> (STORY-024 to STORY-029) are defined in [PurpleAgent-Sprint1-PRD-Ralph.md](PurpleAgent-Sprint1-PRD-Ralph.md).
>
> **Implementation Locations:**
>
> - **Green Agent**: `src/green/` → `Dockerfile.green` → `green-agent:latest`
> - **Common Module**: `src/common/` → shared by both agents

## Project Overview

**Project Goal:** See [GreenAgent-UserStory.md](../GreenAgent-UserStory.md) for full problem statement.

**Summary:** Sprint 2 completes the adaptive trace collection infrastructure, consolidates
configuration, adds extensibility documentation, and introduces integration-gated tests for
real A2A and LLM connectivity.

**Key Changes from Sprint 1:**

- Replaces fixed-rounds placeholder (`DEFAULT_COORDINATION_ROUNDS = 3`) with adaptive
  collection using idle detection, completion signals, and timeout safety.
- Consolidates all hardcoded values into pydantic-settings classes.
- Creates the missing `docs/AgentBeats/AGENTBEATS_REGISTRATION.md` (gap from STORY-012).
- Adds network/integration-marked tests that run real LLM and A2A calls.

**Design Principles:** KISS, DRY, YAGNI - minimal changes, reuse existing patterns.

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: Adaptive Trace Collection Configuration

**Description:** Replace the fixed-rounds placeholder at `src/green/executor.py` with a
configurable, adaptive trace collection strategy. The design is specified in
`docs/research/trace-collection-strategy.md`. Implementation uses a hybrid approach:
idle detection as the primary signal, completion signals when available, and a hard timeout
as a safety backstop.

**Acceptance Criteria:**

- [ ] `TraceCollectionConfig` Pydantic model with fields: `max_timeout_seconds` (default 30), `idle_threshold_seconds` (default 5), `use_completion_signals` (default True)
- [ ] `TraceCollectionConfig` added to `src/common/models.py` and exported from `src/common/__init__.py`
- [ ] `GreenSettings` includes `trace_collection: TraceCollectionConfig` nested field
- [ ] Executor replaces `DEFAULT_COORDINATION_ROUNDS` fixed loop with adaptive collection loop
- [ ] Idle detection: collection stops when no new trace received within `idle_threshold_seconds`
- [ ] Timeout safety: hard stop after `max_timeout_seconds` regardless of activity
- [ ] Completion signal: when `use_completion_signals=True`, honours `status="complete"` in A2A response metadata
- [ ] Default config produces behaviour equivalent to current fixed-rounds baseline
- [ ] All tests pass: `uv run pytest tests/test_green_executor_traces.py tests/test_green_executor_pipeline.py`

**Technical Requirements:**

- `asyncio.wait_for` and `asyncio.sleep` for non-blocking idle detection
- Backward compatible: existing tests must pass without changes to test code

**Files:**

- `src/common/models.py`
- `src/common/__init__.py`
- `src/green/settings.py`
- `src/green/executor.py`
- `tests/test_green_executor_traces.py`
- `tests/test_green_executor_pipeline.py`

---

#### Feature 2: Settings Audit and Configuration Documentation

**Description:** Audit both agents for hardcoded configuration values, move them into
pydantic-settings classes, and produce a canonical environment variable reference document
for operators and contributors.

**Acceptance Criteria:**

- [ ] Audit `src/green/` and `src/purple/` for hardcoded values outside settings classes
- [ ] All audited values moved to `GreenSettings` or `PurpleSettings` with env var overrides
- [ ] `GreenSettings` covers: host, port, output file path, LLM config, A2A config, trace collection config, coordination rounds (deprecated after Feature 1)
- [ ] `PurpleSettings` covers: host, port, agent UUID, static peers, green agent URL
- [ ] `docs/AgentBeats/CONFIGURATION.md` created with full env var table (name, default, description, agent)
- [ ] Settings test coverage updated: `uv run pytest tests/test_green_settings.py tests/test_purple_settings.py`
- [ ] All tests pass

**Technical Requirements:**

- `pydantic-settings` for env var parsing (already a dependency)
- Markdown table format for configuration reference

**Files:**

- `src/green/settings.py`
- `src/purple/settings.py`
- `docs/AgentBeats/CONFIGURATION.md`
- `tests/test_green_settings.py`
- `tests/test_purple_settings.py`

---

#### Feature 3: Extensibility Documentation

**Description:** Create `docs/AgentBeats/AGENTBEATS_REGISTRATION.md` to document the
evaluator plugin architecture, tier system, and provide a worked example of adding a
custom evaluator. Resolves the gap identified from STORY-012 (file referenced but never
created).

**Acceptance Criteria:**

- [ ] `docs/AgentBeats/AGENTBEATS_REGISTRATION.md` file created
- [ ] Documents `BaseEvaluator` ABC interface pattern with typed Python code example
- [ ] Documents tier-based structure: Tier 1 (Graph/structural), Tier 2 (LLM + Latency), Tier 3 (custom plugins)
- [ ] Documents `GraphMetricPlugin` ABC as second-level extension point within graph evaluator
- [ ] Step-by-step guide: create evaluator file, implement `evaluate()`, register in `Executor._run_evaluations()`
- [ ] Reference implementation: `TextEvaluator` (Tier 3) shown as worked example
- [ ] Integration points clearly described with file paths and line number references

**Technical Requirements:**

- Markdown documentation only
- Code examples must be copy-paste accurate (no pseudocode)

**Files:**

- `docs/AgentBeats/AGENTBEATS_REGISTRATION.md`

---

#### Feature 4: Real A2A and LLM Integration Tests

**Description:** Add integration-gated and network-gated tests that validate live A2A
communication and real LLM API calls without mocks. Tests are skipped in standard CI
(no API key, no external services) but can be run locally or in dedicated integration pipelines.

**Acceptance Criteria:**

- [ ] `tests/test_green_llm_live.py` created with `@pytest.mark.network` marker
- [ ] Live LLM tests skip automatically when `AGENTBEATS_LLM_API_KEY` env var is unset
- [ ] Live LLM tests call real OpenAI-compatible endpoint with `temperature=0` and verify `LLMJudgment` response structure
- [ ] `tests/e2e/test_live_a2a_evaluation.py` created with `@pytest.mark.integration` marker
- [ ] Live A2A tests launch Green and Purple via `httpx.AsyncClient` with `ASGITransport` (no Docker required)
- [ ] Live A2A tests verify `InteractionStep` traces captured during real `message/send` exchange
- [ ] Live A2A tests verify `output/results.json` written with correct `AgentBeatsOutputModel` schema
- [ ] Standard test run unaffected: `uv run pytest tests/ -m "not network and not integration"` passes

**Technical Requirements:**

- `pytest.mark.network` for LLM gating (already registered in `pyproject.toml`)
- `pytest.mark.integration` for A2A gating (already registered in `pyproject.toml`)
- `httpx.AsyncClient` with `ASGITransport` for ASGI-level integration (no ports needed)

**Files:**

- `tests/test_green_llm_live.py`
- `tests/e2e/test_live_a2a_evaluation.py`

---

## Non-Functional Requirements

**Platform:** Python 3.13, uv, pytest-asyncio `auto` mode

**Quality gates (required before each story is marked complete):**

- `make validate` (ruff + type_check + test_all)

**Test Markers (defined in pyproject.toml):**

- `integration`: requires live agent processes — skip in standard CI
- `network`: requires external API credentials — skip in standard CI
- `benchmark`: performance benchmarks

**Backward Compatibility:**

- All Sprint 1 tests must continue to pass unchanged
- Default `TraceCollectionConfig` must reproduce Sprint 1 behaviour

---

## Out of Scope

The following are explicitly deferred to future sprints:

1. ART (Adaptive Reasoning Trees) training on captured traces
2. PeerRead text similarity plugin (Tier 3 TextEvaluator implementation)
3. Temporal graph analysis and time-series metrics
4. Batch evaluation API
5. Local LLM support (Ollama, LM Studio)
6. OpenAPI/Swagger documentation generation
7. CPU/memory profiling and throughput metrics

---

## Known Blockers

1. **LLM API Key**: `AGENTBEATS_LLM_API_KEY` required for STORY-035 live tests; standard CI skips these tests automatically.
2. **Purple Agent Sprint 1**: STORY-024 to STORY-029 (Purple LLM + role system) are defined separately in `PurpleAgent-Sprint1-PRD-Ralph.md` and must be completed to enable full P2P coordination scenarios.

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->

Story Breakdown (7 stories total):

- **Feature 1 (Adaptive Trace Collection Configuration)** → STORY-030: TraceCollectionConfig model, STORY-031: Hybrid trace collection strategy in Executor (depends: STORY-030)
- **Feature 2 (Settings Audit and Configuration Documentation)** → STORY-032: Settings audit and consolidation, STORY-033: Environment variable configuration guide (depends: STORY-032)
- **Feature 3 (Extensibility Documentation)** → STORY-034: Create AGENTBEATS_REGISTRATION.md evaluator guide
- **Feature 4 (Real A2A and LLM Integration Tests)** → STORY-035: Live LLM connectivity tests, STORY-036: Real A2A E2E integration tests (depends: STORY-035)

---

### Dependency Graph

```text
STORY-030 (TraceCollectionConfig model)
    ↓
STORY-031 (Hybrid trace collection in Executor)

STORY-032 (Settings audit and consolidation)
    ↓
STORY-033 (Environment variable configuration guide)

STORY-034 (AGENTBEATS_REGISTRATION.md)   [independent]

STORY-035 (Live LLM connectivity tests)
    ↓
STORY-036 (Real A2A E2E integration tests)
```

### Verification After Each Story

1. **Tests pass**: `make test_all`
2. **Type checking passes**: `make type_check`
3. **Formatting passes**: `make ruff`
4. **Complete validation**: `make validate`
5. **Integration tests (optional local)**: `uv run pytest tests/ -m "network or integration" -v`
