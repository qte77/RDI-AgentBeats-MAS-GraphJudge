---
title: Product Requirements Document - Graph-Based Coordination Benchmark
version: 1.0
applies-to: Agents and humans
purpose: How, Enhance evaluation system with real LLM integration, plugin architecture, and additional metrics
---

> See [GreenAgent-UserStory.md](GreenAgent-UserStory.md) for vision and value proposition.
>
> **Scope**: This PRD covers the **Green Agent (Assessor)** implementation and the **Base Purple Agent** test fixture required for E2E validation.
>
> **Implementation Locations:**
>
> - **Green Agent**: `src/green/` → containerized by `Dockerfile.green` → pushed as `green-agent:latest` via `scripts/docker/push.sh`
> - **Base Purple Agent**: `src/purple/` → containerized by `Dockerfile.purple` → pushed as `purple-agent:latest` via `scripts/docker/push.sh`
>
> Full Purple Agent capabilities may be expanded in future phases.

## Project Overview

**Project Goal:** See [GreenAgent-UserStory.md](GreenAgent-UserStory.md) for full problem statement and value proposition.

**Summary:** Evaluate multi-agent coordination quality through runtime graph analysis, LLM assessment, and text similarity metrics.

**Architecture:**

- **Green Agent (Benchmark/Assessor)**: Captures interactions, builds graphs, computes metrics, orchestrates evaluation
  - Implementation: `src/green/` → `Dockerfile.green` → `green-agent:latest`
- **Purple Agents (Participants)**: Multi-agent systems under test, communicate via A2A protocol
  - Base implementation: `src/purple/` → `Dockerfile.purple` → `purple-agent:latest`
- **Evaluation Pipeline**: Trace capture → Graph analysis → LLM assessment → Latency metrics → Structured results

**Design Principles:** KISS, DRY, YAGNI - minimal changes, reuse existing patterns, defer complex abstractions.

**Platform Compatibility:** Built for AgentBeats platform with full A2A protocol compliance, Docker deployment, and standardized CLI interface.

---

## Functional Requirements

<!-- PARSER REQUIREMENT: Use exactly "#### Feature N:" format -->

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

- `src/green/messenger.py`
- `src/green/executor.py`
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

- `src/green/evals/graph.py`
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
- [ ] Multi-plugin data ingestion: Can receive outputs from Graph, Text, Latency evaluators for holistic assessment
- [ ] Task outcome assessment: Evaluates whether coordination led to successful task completion

**Technical Requirements:**

- openai>=1.0
- Graceful degradation pattern
- JSON response parsing with validation

**Files:**

- `src/green/evals/llm_judge.py`
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

- `src/green/evals/system.py`
- `src/green/executor.py`
- `tests/test_system.py`

---

#### Feature 5: Extensibility Documentation

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

- `docs/AgentBeats/AGENTBEATS_REGISTRATION.md` *(exists)*

---

#### Feature 6: E2E Testing Infrastructure

**Description:** Base Purple Agent (minimal test fixture) and ground truth dataset for validating the Green Agent evaluation pipeline. The Base Purple Agent is a simplified A2A-compliant agent implementation built into the `purple-agent` Docker image.

**Acceptance Criteria:**

- [ ] Base Purple Agent implemented as A2A-compliant test fixture
- [ ] Ground truth dataset with labeled test scenarios (`data/ground_truth.json`)
  - Source: Small subset of PeerRead dataset from HuggingFace (`allenai/PeerRead`)
  - Format: JSON with paper abstracts, reviews, and coordination task labels
  - Subset size: 10-20 diverse samples for reproducible E2E validation
- [ ] E2E tests validate both agents' AgentCards are accessible
- [ ] E2E tests verify Purple Agent generates expected outputs
- [ ] E2E tests verify Green Agent correctly classifies ground truth scenarios
- [ ] Comprehensive tests report accuracy metrics against ground truth
- [x] Container orchestration supports isolated testing *(docker-compose-local.yaml)*

**Technical Requirements:**

- Base Purple Agent follows RDI green-agent-template pattern
- Ground truth source: PeerRead dataset (HuggingFace `allenai/PeerRead`)
- Ground truth format: JSON with labeled coordination scenarios derived from peer review interactions
- Docker Compose orchestration for isolated testing
- Docker image: `ghcr.io/${GH_USERNAME}/purple-agent:latest` (built from `Dockerfile.purple`)

**Files:**

- `src/purple/` (Base Purple Agent implementation)
- `Dockerfile.purple` *(exists)*
- `data/ground_truth.json`
- `tests/e2e/`
- `docker-compose-local.yaml` *(exists)*

---

## Non-Functional Requirements

**Performance:**

- All evaluations (graph + LLM + latency) complete in <30 seconds
- A2A task timeout: 300 seconds (5 minutes)
- Latency evaluation: <5 seconds
- **Note**: Latency metrics are relative (same-system comparisons), not cross-environment benchmarks

**Statistical Validity:**

- Minimum 10 diverse scenarios recommended for statistically meaningful results
- Multiple evaluation runs supported to handle agent non-determinism
- Results include confidence indicators when sample size is small

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

```text
src/
├── green/              # Green Agent (assessor) - implement first
│   ├── agent.py        # Agent logic and orchestration
│   ├── executor.py     # Task execution and result processing
│   ├── messenger.py    # A2A communication layer
│   ├── server.py       # Server setup and endpoints
│   └── evals/          # Evaluation modules (graph, llm_judge, latency)
└── purple/             # Base Purple Agent (test fixture) - implement later
    ├── agent.py
    ├── executor.py
    ├── messenger.py
    └── server.py
data/
└── ground_truth.json   # Small subset of PeerRead dataset (HuggingFace allenai/PeerRead)
```

**Containerization:**

- Green Agent: `src/green/` → containerized by `Dockerfile.green` → pushed as `ghcr.io/${GH_USERNAME}/green-agent:latest`
- Purple Agent: `src/purple/` → containerized by `Dockerfile.purple` → pushed as `ghcr.io/${GH_USERNAME}/purple-agent:latest`

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

- `scripts/docker/e2e_test.sh` (quick): Basic smoke test with 2 test cases
- `scripts/docker/e2e_test.sh full`: Full ground truth validation with all scenarios
- Ground truth: `data/ground_truth.json` (PeerRead subset: 10-20 samples from HuggingFace `allenai/PeerRead`)

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

The following are explicitly excluded from this benchmark's scope:

1. **Individual agent capabilities evaluation**: Not evaluating coding, reasoning, tool use, or domain-specific task success (covered by other AgentBeats benchmarks)
2. **Task completion quality metrics**: Not measuring whether agents completed tasks correctly, only how they coordinated
3. **Real-time streaming evaluation**: Evaluation happens post-execution after all interactions captured
4. **Persistent storage or database**: Results returned via A2A response only, no historical storage
5. **Visualization UI or dashboards**: Output is structured JSON for programmatic consumption
6. **Non-coordination benchmarks**: Domain-specific compliance, legal requirements, or single-agent performance tests
7. **Agent implementation details**: Not evaluating internal agent architecture, model choice, or prompt engineering
8. **Human-agent interaction patterns**: Focus on agent-to-agent (A2A) coordination only

### Evaluator Extension Pattern

Simple interface for adding custom evaluators without complex plugin registry:

```python
# src/green/evals/base.py
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

1. Create `src/green/evals/my_evaluator.py` implementing `BaseEvaluator`
2. Import and call in `Executor._run_evaluations()`
3. Add result to response dict

**TextEvaluator (Tier 3)** serves as the reference implementation for this pattern.

---

## Known Blockers

1. **A2A SDK Installation**: a2a-sdk may not be on PyPI; check GitHub for git+https install URL
2. **LLM API Credentials**: `AGENTBEATS_LLM_API_KEY` required; fallback to rule-based evaluation implemented

---

## Notes for Ralph Loop

<!-- PARSER REQUIREMENT: Include story count in parentheses -->
<!-- PARSER REQUIREMENT: Use (depends: STORY-XXX, STORY-YYY) for dependencies -->

Story Breakdown (17 stories total):

- **Feature 1 (A2A Protocol Communication)** → STORY-001: Messenger with A2A SDK + extensions, STORY-002: InteractionStep model integration (depends: STORY-001), STORY-003: Executor with trace collection and cleanup (depends: STORY-002), STORY-004: Add OpenAI dependency to pyproject.toml (depends: STORY-003), STORY-005: Green Agent business logic (agent.py) (depends: STORY-004), STORY-006: Green Agent A2A HTTP server (server.py) (depends: STORY-005)
- **Feature 2 (Graph-Based Coordination Analysis)** → STORY-013: Graph evaluator test suite (depends: STORY-003), STORY-014: Graph-based coordination analysis implementation (depends: STORY-013)
- **Feature 3 (LLM-Based Qualitative Evaluation)** → STORY-007: LLM client configuration with environment variables (depends: STORY-006), STORY-008: LLM prompt engineering for coordination assessment (depends: STORY-007), STORY-009: LLM API integration with fallback to rule-based evaluation (depends: STORY-008)
- **Feature 4 (Latency Metrics Evaluation)** → STORY-010: Latency metrics evaluator (depends: STORY-009)
- STORY-011: Wire all evaluators in Executor pipeline (depends: STORY-003, STORY-010)
- **Feature 5 (Extensibility Documentation)** → STORY-012: Extensibility documentation and examples (depends: STORY-011)
- **Feature 6 (E2E Testing Infrastructure)** → STORY-015: Base Purple Agent implementation (depends: STORY-003), STORY-016: E2E test suite with ground truth validation (depends: STORY-015, STORY-011)
- STORY-017: Create demo video script (depends: STORY-011)

---

### Dependency Graph

```text
STORY-001 (Messenger with A2A SDK)
    ↓
STORY-002 (InteractionStep model)
    ↓
STORY-003 (Executor with trace collection)
    ├─────────────────┬─────────────┬─────────────────┐
    ↓                 ↓             ↓                 ↓
STORY-004      STORY-013      STORY-015         STORY-011
(OpenAI dep)   (Graph test)   (Purple Agent)    (Integration)
    ↓                 ↓                               ↑
STORY-005      STORY-014                              │
(Agent.py)     (Graph impl)                           │
    ↓                                                 │
STORY-006                                             │
(Server.py)                                           │
    ↓                                                 │
STORY-007                                             │
(LLM config)                                          │
    ↓                                                 │
STORY-008                                             │
(LLM prompt)                                          │
    ↓                                                 │
STORY-009                                             │
(LLM API)                                             │
    ↓                                                 │
STORY-010 ────────────────────────────────────────────┘
(Latency)
    ↓
STORY-011 (Integration) ──────────┬──────────────────┬──────────────┐
    ↓                             ↓                  ↓              ↓
STORY-012                   STORY-017          STORY-016        (merged)
(Extensibility docs)        (Demo script)      (E2E tests)          │
                                                    ↑               │
                                                    │               │
                                             STORY-015 ─────────────┘
                                             (Purple Agent)
```

### Verification After Each Phase

1. **Tests pass**: `make test_all`
2. **Type checking passes**: `make type_check`
3. **Formatting passes**: `make ruff`
4. **Manual validation**: Run green agent against purple agent, verify new metrics in output
5. **Platform validation**: Test with AgentBeats docker-compose pattern
