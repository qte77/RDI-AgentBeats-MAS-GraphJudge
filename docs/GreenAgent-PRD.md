---
title: Product Requirements Document - Graph-Based Coordination Benchmark
version: 1.0
applies-to: Agents and humans
purpose: How, Enhance evaluation system with real LLM integration, plugin architecture, and additional metrics
---

> See [GreenAgent-UserStory.md](GreenAgent-UserStory.md) for vision and value proposition.
>
> **Scope**: This PRD covers the **Green Agent (Assessor)** implementation only. The **Purple Agent (Assessee)** - multi-agent system under test - will be added in a future phase.

## Project Overview

**Project Goal:** See [GreenAgent-UserStory.md](GreenAgent-UserStory.md) for full problem statement and value proposition.

**Summary:** Evaluate multi-agent coordination quality through runtime graph analysis, LLM assessment, and text similarity metrics.

**Architecture:**

- **Green Agent (Benchmark/Assessor)**: Captures interactions, builds graphs, computes metrics, orchestrates evaluation
- **Purple Agents (Participants)**: Multi-agent systems under test, communicate via A2A protocol
- **Evaluation Pipeline**: Trace capture → Graph analysis → LLM assessment → Latency metrics → Structured results

**Design Principles:** KISS, DRY, YAGNI - minimal changes, reuse existing patterns, defer complex abstractions.

**Platform Compatibility:** Built for AgentBeats platform with full A2A protocol compliance, Docker deployment, and standardized CLI interface.

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "### Feature N:" format -->

### Feature 1: A2A Protocol Communication

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

**Description:** Build directed graphs from interaction traces and compute coordination quality metrics using graph theory. All metrics implemented as plugins that can be enabled/disabled independently.

**Acceptance Criteria:**
- [ ] Builds directed graph from TraceData (nodes = agents, edges = interactions)
- [ ] **Pluggable metric system**: Each graph metric is a separate plugin
- [ ] **Centrality metrics** (all pluggable):
  - degree centrality
  - betweenness centrality
  - closeness centrality
  - eigenvector centrality
  - PageRank
- [ ] **Structure metrics** (all pluggable):
  - graph density
  - clustering coefficient
  - connected components count
- [ ] **Path metrics** (all pluggable):
  - average path length
  - diameter
- [ ] Identifies bottlenecks (betweenness centrality >0.5)
- [ ] Detects isolated agents (degree = 0)
- [ ] Detects over-centralized patterns (single agent handles >70% interactions)
- [ ] Measures distribution quality (density >0.3 indicates healthy collaboration)
- [ ] Returns structured GraphMetrics with numerical scores

**Technical Requirements:**
- NetworkX for graph algorithms (see Non-Functional Requirements for alternatives)
- Deterministic metric computation (same input → same output)
- Plugin interface allows adding custom metrics without modifying core code

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
- [ ] Executor includes `_evaluate_latency()` method
- [ ] Results included in Executor response (part of Tier 2 assessment)
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
- [ ] Tier-based structure documented:
  - Tier 1: Graph (structural analysis via NetworkX)
  - Tier 2: LLM-Judge (qualitative) + Latency (performance)
  - Tier 3: Text (similarity metrics - plugin example)
- [ ] Integration points clearly described
- [ ] Example evaluator implementation provided (TextEvaluator as Tier 3 plugin)
- [ ] Shows how to add new evaluator to Executor

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

**Graph Analysis:**
- NetworkX for graph algorithms (industry standard, pure Python)
- Alternative: igraph for large-scale graphs if performance becomes an issue

**Agent Template Structure:**
Both Green and Purple agents follow RDI green-agent-template pattern in separate directories:
```
src/
├── green/              # Green Agent (assessor) - implement first
│   ├── agent.py        # Agent logic and orchestration
│   ├── executor.py     # Task execution and result processing
│   ├── messenger.py    # A2A communication layer
│   └── server.py       # Server setup and endpoints
└── purple/             # Purple Agent (assessee) - implement later
    ├── agent.py
    ├── executor.py
    ├── messenger.py
    └── server.py
data/
└── ground_truth.json   # Labeled test scenarios for validation
```
Reference: `github.com/RDI-Foundation/green-agent-template/tree/example/debate_judge/src`

**A2A Protocol Implementation Details:**
- SDK: A2A SDK (a2a-sdk>=0.3.20) for Agent, Task, and Message operations
- Agent Card: AgentCard at `/.well-known/agent-card.json` declaring AgentSkill and AgentCapabilities
- Task Operations: `tasks.send`, `tasks.query`, `tasks.update` methods
- Message Types: TextPart, DataPart content in A2A Message protocol
- Traceability: A2A Traceability Extension for distributed call tracing
- Error Handling: JSONRPCErrorResponse with proper error codes per A2A specification
- Authentication: OpenAPI auth mechanisms as defined in A2A protocol
- MCP Ready: Model Context Protocol for extensible tool/resource access
- Streaming: Optional push notifications for long-running evaluations

**AgentBeats CLI Interface:**
- CLI args: `--host`, `--port`, `--card-url` (argparse-based)
- Entry point: argparse-based (not uvicorn factory)
- Default port: 9009 (AgentBeats default)
- Task isolation via context_id tracking

**LLM Judge Implementation:**
- Uses temperature=0 for consistent scoring
- Falls back to rule-based if API unavailable (logs warning)

**Graph Metric Thresholds:**
- Bottleneck detection: Betweenness centrality >0.5 flags coordinator agents
- Isolation detection: Degree centrality = 0 identifies disconnected agents
- Distribution quality: Graph density >0.3 indicates healthy collaboration spread

**Testing Scripts:**
- `scripts/docker/test_e2e.sh`: Basic smoke test
- `scripts/docker/test_comprehensive.sh`: Full ground truth validation
- Ground truth: `data/ground_truth.json`

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
6. **Plugin registry/discovery**: Manual evaluator integration only (see Evaluator Extension Pattern below)
7. **Advanced NLP metrics**: BLEU, semantic embeddings deferred (TextEvaluator demonstrates plugin pattern with basic similarity)
8. **Error pattern categorization**: Defer to future work

### Evaluator Extension Pattern

Simple interface for adding custom evaluators without complex plugin registry:

```python
# src/agentbeats/evals/base.py
from abc import ABC, abstractmethod
from typing import Any
from ..models import TraceData

class BaseEvaluator(ABC):
    """Simple evaluator interface. Implement evaluate() to add new evaluators."""

    @abstractmethod
    async def evaluate(self, traces: list[TraceData]) -> dict[str, Any]:
        """Evaluate traces and return metrics dict."""
        pass
```

**Adding a new evaluator:**
1. Create `src/agentbeats/evals/my_evaluator.py` implementing `BaseEvaluator`
2. Import and call in `Executor._run_evaluations()`
3. Add result to response dict

**TextEvaluator (Tier 3)** serves as the reference implementation for this pattern.

---

## Known Blockers

1. **A2A SDK Installation**: a2a-sdk may not be on PyPI; check GitHub for git+https install URL
2. **LLM API Credentials**: `AGENTBEATS_LLM_API_KEY` required; fallback to rule-based evaluation implemented
3. **Purple Agent for Testing**: Need minimal echo agent; create baseline responder for integration tests

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

### Story Breakdown - Phase 1b: Graph Evaluation (2 stories total)

**Can run in parallel with Phase 2 after STORY-003-IMPL completes.**

- **Feature 2** → **STORY-GRAPH-TEST**: Write graph evaluator tests (depends: STORY-003-IMPL)
  - Test directed graph construction from TraceData
  - Test centrality metrics (degree, betweenness, closeness)
  - Test bottleneck detection
  - Test edge cases (empty traces, single agent, isolated agents)
- **Feature 2** → **STORY-GRAPH-IMPL**: Implement graph evaluator (depends: STORY-GRAPH-TEST)
  - Build DiGraph from TraceData (nodes=agents, edges=interactions)
  - Compute centrality metrics via NetworkX
  - Detect coordination patterns (bottlenecks, isolation, over-centralization)
  - Return structured GraphMetrics

**Files:**
- `src/agentbeats/evals/graph.py`
- `tests/test_graph.py`

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

- STORY-009-INTEGRATION: Wire all evaluators in Executor pipeline (depends: STORY-003-IMPL, STORY-GRAPH-IMPL, STORY-007-IMPL, STORY-008-IMPL)

**Acceptance Criteria:**
- [ ] Executor calls messenger.talk_to_agent() for each agent URL
- [ ] Messenger returns TraceData captured in executor results
- [ ] Tier 1: GraphEvaluator processes traces
- [ ] Tier 2: LLMJudge processes traces (or falls back)
- [ ] Tier 2: LatencyEvaluator processes traces
- [ ] E2E test: submit task → traces captured → all evaluations run → results returned

### Story Breakdown - Phase 5: Final Deliverables (2 stories total)

- **Feature 6** → STORY-010-DOCS: Write extensibility documentation (depends: STORY-009-INTEGRATION)
  - Document evaluator interface pattern (BaseEvaluator)
  - Document tier structure (Tier 1/2/3)
  - Provide TextEvaluator as Tier 3 plugin example
- **STORY-011-DEMO**: Create demo video (depends: STORY-009-INTEGRATION)
  - **Status**: Coming Soon
  - Record server startup and A2A endpoint verification
  - Show evaluation flow with trace capture
  - Display multi-tier results (graph, LLM judge, latency)
  - Max 3 minutes

### Platform Compatibility Checklist

- [ ] CLI interface: `--host`, `--port`, `--card-url` (argparse)
- [ ] Entry point: argparse-based, not uvicorn factory pattern
- [ ] Default port: 8000 (local: 8001:8000, platform: 9009)
- [ ] Endpoints: `/.well-known/agent-card.json` accessible
- [ ] Validated against: AgentBeats `generate_compose.py`
- [ ] Docker ENTRYPOINT supports positional CLI args
- [ ] Agent card URL configurable (for proxies/load balancers)

### Dependency Graph

```text
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
STORY-003-IMPL ─────────────────────┐
    ↓                               ↓
STORY-004                    STORY-GRAPH-TEST
    ↓                               ↓
STORY-005-TEST               STORY-GRAPH-IMPL
    ↓                               │
STORY-005-IMPL                      │
    ↓                               │
STORY-006-TEST                      │
    ↓                               │
STORY-006-IMPL                      │
    ↓                               │
STORY-007-TEST                      │
    ↓                               │
STORY-007-IMPL                      │
    ↓                               │
STORY-008-TEST                      │
    ↓                               │
STORY-008-IMPL ─────────────────────┘
    ↓
STORY-009-INTEGRATION
    ↓
STORY-010-DOCS
    ↓
STORY-011-DEMO (Coming Soon)
```

### Verification After Each Phase

1. **Tests pass**: `make test_all`
2. **Type checking passes**: `make type_check`
3. **Formatting passes**: `make ruff`
4. **Manual validation**: Run green agent against purple agent, verify new metrics in output
5. **Platform validation**: Test with AgentBeats docker-compose pattern
