---
title: Product Requirements Document - Graph-Based Coordination Benchmark
version: 1.0
applies-to: Agents and humans
purpose: Enhance evaluation system with real LLM integration, plugin architecture, and additional metrics
---

> See [UserStory.md](UserStory.md) for vision and value proposition.

## Project Overview

**Project Goal:** Evaluate multi-agent coordination quality through runtime graph analysis to measure HOW agents collaborate. This benchmark captures agent-to-agent interactions during task execution, builds coordination graphs, and applies both quantitative (graph metrics) and qualitative (LLM-based) evaluation.

**Core Innovation:** No existing AgentBeats benchmark analyzes coordination patterns through graph structure. This benchmark transforms abstract "collaboration quality" into concrete metrics grounded in graph theory.

**Architecture:**
- **Green Agent (Benchmark/Assessor)**: Captures interactions, builds graphs, computes metrics, orchestrates evaluation
- **Purple Agents (Participants)**: Multi-agent systems under test, communicate via A2A protocol
- **Evaluation Pipeline**: Trace capture → Graph analysis → LLM assessment → Latency metrics → Structured results

**Design Principles:** KISS, DRY, YAGNI - minimal changes, reuse existing patterns, defer complex abstractions.

**Platform Compatibility:** Built for AgentBeats platform with full A2A protocol compliance, Docker deployment, and standardized CLI interface.

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

#### Feature 1: A2A Protocol Communication

**Description:** Real agent-to-agent communication via A2A SDK for authentic coordination measurement. Replaces mock REST protocol with production-grade A2A JSON-RPC communication.

**Acceptance Criteria:**
- [ ] Messenger uses `ClientFactory.connect()` from a2a-sdk (not custom REST)
- [ ] Messages created via `create_text_message_object()`
- [ ] Response extracted from `TaskState.completed` events
- [ ] Client caching per agent URL implemented
- [ ] `Messenger.close()` cleanup method for cached clients
- [ ] InteractionStep model conforms to A2A Traceability Extension Step specification
- [ ] Model includes: step_id, trace_id, call_type, start_time, end_time, latency, error, parent_step_id
- [ ] AgentCard declares traceability + timestamp extension support
- [ ] Messenger sends `X-A2A-Extensions` activation headers
- [ ] CallType classification: AGENT for messenger, TOOL for LLM, HOST for graph
- [ ] Executor calls `await messenger.close()` after trace collection
- [ ] All tests pass: `uv run pytest tests/test_messenger.py tests/test_executor.py`

**Technical Requirements:**
- a2a-sdk[http-server]>=0.3.20
- Async iteration over `send_message()` events
- Proper error handling for A2A protocol errors

**Files:**
- `src/agentbeats/messenger.py`
- `src/agentbeats/executor.py`
- `tests/test_messenger.py`
- `tests/test_executor.py`

---

#### Feature 2: Graph-Based Coordination Analysis

**Description:** Build directed graphs from interaction traces and compute coordination quality metrics using graph theory.

**Acceptance Criteria:**
- [ ] Builds directed graph from TraceData (nodes = agents, edges = interactions)
- [ ] Computes centrality metrics: degree, betweenness, closeness
- [ ] Identifies bottlenecks (high betweenness centrality agents)
- [ ] Measures efficiency: graph density, clustering coefficient
- [ ] Detects isolated agents (degree = 0)
- [ ] Detects over-centralized patterns (single agent handles >70% interactions)
- [ ] Returns structured GraphMetrics with numerical scores

**Technical Requirements:**
- NetworkX for graph algorithms
- Deterministic metric computation (same input → same output)

**Files:**
- `src/agentbeats/evals/graph.py`
- `tests/test_graph.py`

---

#### Feature 3: LLM-Based Qualitative Evaluation

**Description:** Replace rule-based LLM Judge with real LLM API calls for semantic assessment of coordination quality.

**Acceptance Criteria:**
- [ ] Reads environment: `AGENTBEATS_LLM_API_KEY`, `AGENTBEATS_LLM_BASE_URL`, `AGENTBEATS_LLM_MODEL`
- [ ] Default base URL: `https://api.openai.com/v1`
- [ ] Default model: `gpt-4o-mini`
- [ ] Supports any OpenAI-compatible endpoint
- [ ] Prompt includes: TraceData serialization, evaluation criteria, JSON schema for LLMJudgment
- [ ] Requests: overall_score (0-1), reasoning, coordination_quality, strengths, weaknesses
- [ ] Falls back to rule-based if API unavailable (logs warning, not error)
- [ ] Uses temperature=0 for consistency
- [ ] Handles API errors gracefully (timeout, invalid JSON)

**Technical Requirements:**
- openai>=1.0
- Graceful degradation pattern
- JSON response parsing with validation

**Files:**
- `src/agentbeats/evals/llm_judge.py`
- `tests/test_llm_judge.py`

---

#### Feature 4: Latency Metrics Evaluation

**Description:** Track agent response time performance for comparative analysis within the same system environment. Latency metrics are **relative** (comparing agents on identical hardware), not absolute performance benchmarks.

**Acceptance Criteria:**
- [ ] Reads latency from InteractionStep.latency field (auto-calculated by A2A)
- [ ] Computes percentiles: avg, p50, p95, p99
- [ ] Identifies slowest agent by URL (relative to peers in same run)
- [ ] Follows existing evaluator pattern (like GraphEvaluator, LLMJudge)
- [ ] Executor includes `_evaluate_latency()` method (tier pattern)
- [ ] Results included as `tier2_latency` in Executor response
- [ ] Documentation warns: "Latency values only comparable within same system/run"

**Technical Requirements:**
- NumPy for percentile calculations
- Latency values in milliseconds (from A2A Step.latency field)

**Use Case:** Identify coordination bottlenecks (e.g., Agent A waits 10x longer than Agent B for responses), not absolute performance rating.

**Files:**
- `src/agentbeats/evals/latency.py`
- `src/agentbeats/executor.py`
- `tests/test_latency.py`

---

#### Feature 5: Platform Integration and Deployment

**Description:** AgentBeats platform compatibility with proper CLI interface, Docker configuration, and discovery endpoints.

> **Implementation Guide:** See [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) for detailed Dockerfile patterns, server entry point code, test structure, and validation gates.

**Acceptance Criteria:**
- [ ] CLI args: `--host`, `--port`, `--card-url` (argparse-based)
- [ ] Default port: 8000 (local dev uses 8001:8000, AgentBeats platform uses 9009)
- [ ] AgentCard accessible at `/.well-known/agent-card.json`
- [ ] Docker images: linux/amd64, Python 3.13-slim, multi-stage build
- [ ] ENTRYPOINT supports CLI arguments
- [ ] docker-compose.yml orchestrates green + purple agents
- [ ] Agents can reach each other via Docker network
- [ ] No hardcoded secrets (environment variables only)

**Technical Requirements:**
- uvicorn>=0.38.0
- Docker Compose v2+
- GHCR deployment workflow (GitHub Actions)

**Files:**
- `src/agentbeats/server.py` (entry point)
- `Dockerfile.green`
- `docker-compose.yaml`
- `.github/workflows/ghcr-push.yaml`

---

#### Feature 6: Extensibility Documentation

**Description:** Clear patterns and examples for adding custom evaluators without modifying core code.

**Acceptance Criteria:**
- [ ] Documentation explains evaluator interface pattern
- [ ] Tier-based structure documented (tier1, tier2)
- [ ] Integration points clearly described
- [ ] Example evaluator implementation provided
- [ ] Shows how to add new evaluator to Executor
- [ ] Explains when to use tier1 vs tier2

**Technical Requirements:**
- Markdown documentation
- Code examples with comments

**Files:**
- `docs/AgentBeats/Technical-Implementation-Guide.md`
- `docs/AgentBeats/AGENTBEATS_REGISTRATION.md`

---

## Non-Functional Requirements

**Performance:**
- All evaluations (graph + LLM + latency) complete in <30 seconds
- A2A task timeout: 300 seconds (5 minutes)
- Latency evaluation: <5 seconds
- **Note**: Latency metrics are relative (same-system comparisons), not cross-environment benchmarks

**A2A Protocol:**
- JSON-RPC 2.0 message format
- AgentCard at `/.well-known/agent-card.json`
- Standard error codes (-32700 to -32001)
- Task lifecycle: pending → running → completed/failed

**Platform:**
- Python 3.13 (uv package manager)
- Docker linux/amd64
- A2A Protocol v0.3+ (a2a-sdk>=0.3.20)

**Reproducibility:**
- Fresh state for each assessment
- Task ID namespace isolation
- No memory/file carryover between runs
- Same input traces → same graph metrics (deterministic)

**Code Quality:**
- Type checking passes: `make type_check`
- All tests pass: `make test_all`
- Formatting passes: `make ruff`
- Complete validation: `make validate`

---

## Out of Scope

1. **Real-time streaming evaluation**: Evaluation happens post-execution, not during task runtime
2. **Persistent metrics storage**: Results returned via A2A response only, no database
3. **Metrics visualization UI**: Output is structured JSON, no built-in dashboard
4. **Custom LLM fine-tuning**: Uses general-purpose LLMs with prompting only
5. **Performance profiling tools**: Basic latency metrics only, no deep profiling (scalene/py-spy)
6. **Plugin architecture with registry**: Defer complex abstractions, manual integration only
7. **BLEU score evaluator**: TextMetrics covers basic similarity, defer advanced NLP metrics
8. **Semantic similarity via embeddings**: Defer to future work
9. **Error pattern categorization**: Defer to future work

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->

### Story Breakdown - Phase 1: A2A Protocol Compliance (3 stories total)

**PREREQUISITE**: Must complete before real coordination measurement is possible.

**Story Numbering Convention**: Each story has TEST and IMPL sub-tasks. STORY-001 = STORY-001-TEST + STORY-001-IMPL. Total 3 stories (6 sub-tasks).

- **Feature 1** → **STORY-001**: Messenger with A2A SDK + extensions
  - STORY-001-TEST: Write A2A SDK messenger tests (extension activation, tracing)
  - STORY-001-IMPL: Implement messenger with A2A SDK + extensions (depends: STORY-001-TEST)
- **Feature 1** → **STORY-002**: InteractionStep model integration
  - STORY-002-TEST: Write InteractionStep model tests (A2A Step compliance) (depends: STORY-001-IMPL)
  - STORY-002-IMPL: Implement InteractionStep capture in messenger (depends: STORY-002-TEST)
- **Feature 1** → **STORY-003**: Executor with trace collection
  - STORY-003-TEST: Write Executor A2A cleanup tests (depends: STORY-002-IMPL)
  - STORY-003-IMPL: Implement Executor with trace collection + cleanup (depends: STORY-003-TEST)

### Story Breakdown - Phase 2: Real LLM Integration (5 stories total)

- **Feature 3** → STORY-004: Add OpenAI dependency (depends: STORY-003-IMPL)
- **Feature 3** → STORY-005-TEST: Write LLM client config tests (depends: STORY-004)
- **Feature 3** → STORY-005-IMPL: Implement LLM client config (depends: STORY-005-TEST)
- **Feature 3** → STORY-006-TEST: Write LLM prompt tests (depends: STORY-005-IMPL)
- **Feature 3** → STORY-006-IMPL: Implement LLM prompt (depends: STORY-006-TEST)
- **Feature 3** → STORY-007-TEST: Write LLM API fallback tests (depends: STORY-006-IMPL)
- **Feature 3** → STORY-007-IMPL: Implement LLM API with fallback (depends: STORY-007-TEST)

### Story Breakdown - Phase 3: Latency Metrics (2 stories total)

- **Feature 4** → STORY-008-TEST: Write latency evaluator tests (depends: STORY-007-IMPL)
- **Feature 4** → STORY-008-IMPL: Implement latency evaluator (depends: STORY-008-TEST)

### Story Breakdown - Phase 4: Integration Testing (1 story)

**Type**: integration

- STORY-009-INTEGRATION: Wire all evaluators in Executor pipeline (depends: STORY-003-IMPL, STORY-007-IMPL, STORY-008-IMPL)

**Acceptance Criteria:**
- [ ] Executor calls messenger.talk_to_agent() for each agent URL
- [ ] Messenger returns TraceData captured in executor results
- [ ] GraphEvaluator processes traces
- [ ] LLMJudge processes traces (or falls back)
- [ ] LatencyEvaluator processes traces
- [ ] E2E test: submit task → traces captured → all evaluations run → results returned

### Platform Compatibility Checklist

- [ ] CLI interface: `--host`, `--port`, `--card-url` (argparse)
- [ ] Entry point: argparse-based, not uvicorn factory pattern
- [ ] Default port: 8000 (local: 8001:8000, platform: 9009)
- [ ] Endpoints: `/.well-known/agent-card.json` accessible
- [ ] Validated against: AgentBeats `generate_compose.py`
- [ ] Docker ENTRYPOINT supports positional CLI args
- [ ] Agent card URL configurable (for proxies/load balancers)

### Dependency Graph

```
STORY-001-TEST
    ↓
STORY-001-IMPL
    ↓
STORY-002-TEST
    ↓
STORY-002-IMPL
    ↓
STORY-003-TEST
    ↓
STORY-003-IMPL
    ↓
STORY-004
    ↓
STORY-005-TEST
    ↓
STORY-005-IMPL
    ↓
STORY-006-TEST
    ↓
STORY-006-IMPL
    ↓
STORY-007-TEST
    ↓
STORY-007-IMPL
    ├────────────────┐
    ↓                ↓
STORY-008-TEST   STORY-GRAPH-IMPL (Feature 2: Implement graph evaluator)
    ↓                ↓
STORY-008-IMPL   ─┘
    ↓
    └─────→ STORY-009-INTEGRATION
```

### Verification After Each Phase

1. **Tests pass**: `make test_all`
2. **Type checking passes**: `make type_check`
3. **Formatting passes**: `make ruff`
4. **Manual validation**: Run green agent against purple agent, verify new metrics in output
5. **Platform validation**: Test with AgentBeats docker-compose pattern
