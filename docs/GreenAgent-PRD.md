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

##### 6.1 Base Purple Agent (Test Fixture)

**Acceptance Criteria:**

- [x] Base Purple Agent implemented as A2A-compliant test fixture
- [x] AgentCard at `/.well-known/agent-card.json`
- [x] JSON-RPC 2.0 handler for `message/send`
- [x] Returns valid responses for evaluation tasks
- [x] Configurable via environment variables (`PURPLE_HOST`, `PURPLE_PORT`)

##### 6.2 Ground Truth Dataset

**Acceptance Criteria:**

- [x] Ground truth dataset with labeled test scenarios (`data/ground_truth.json`)
  - Source: Small subset of PeerRead dataset from HuggingFace (`allenai/PeerRead`)
  - Format: JSON with interaction patterns and expected metrics
  - Subset size: 12 diverse samples for reproducible E2E validation
- [x] Scenarios cover: high_coordination, low_coordination, bottleneck, medium_coordination, partial_isolation
- [x] Each scenario includes: `interaction_pattern` (agents, edges) and `expected_metrics`

##### 6.3 E2E Tests (Ground Truth Validation)

**Acceptance Criteria:**

- [x] E2E tests validate both agents' AgentCards are accessible
- [x] E2E tests verify Purple Agent generates expected outputs
- [x] E2E tests verify Green Agent correctly classifies ground truth scenarios
- [x] Comprehensive tests report accuracy metrics against ground truth
- [x] Container orchestration supports isolated testing *(docker-compose-local.yaml)*

##### 6.4 AgentBeats Submission E2E Test (Full Platform Integration)

**Description:** Validates the complete AgentBeats submission flow including agent registration, scenario execution via `agentbeats-client`, and `output/results.json` generation for leaderboard submission.

**AgentBeats Submission Flow:**

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions Workflow                          │
│              .github/workflows/agentbeats-run-scenario.yml              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  1. scenario.toml → generate_compose.py → docker-compose.yml            │
│     - Resolves agentbeats_id → docker image via agentbeats.dev API      │
│     - Generates a2a-scenario.toml for agentbeats-client                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  2. docker compose up                                                   │
│  ┌───────────────┐   ┌───────────────┐   ┌────────────────────────┐    │
│  │  Green Agent  │   │ Purple Agent  │   │   agentbeats-client    │    │
│  │  (Assessor)   │◄─►│ (Participant) │   │   (Orchestrator)       │    │
│  │  Port: 9009   │   │  Port: 9009   │   │                        │    │
│  └───────┬───────┘   └───────────────┘   └───────────┬────────────┘    │
│          │                                           │                  │
│          │  A2A Protocol (JSON-RPC 2.0)              │ Reads            │
│          │  - message/send                           │ a2a-scenario.toml│
│          │  - Trace collection                       │                  │
│          │  - Graph evaluation                       │                  │
│          ▼                                           ▼                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    output/results.json                          │   │
│  │  {                                                              │   │
│  │    "participants": {"agent": "<uuid>"},                         │   │
│  │    "results": [{                                                │   │
│  │      "score": 80.0,                                             │   │
│  │      "domain": "graph-assessment",                              │   │
│  │      "task_rewards": {                                          │   │
│  │        "overall_score": 0.8,                                    │   │
│  │        "graph_density": 0.5,                                    │   │
│  │        "coordination_quality": 0.33                             │   │
│  │      },                                                         │   │
│  │      "detail": { graph_metrics, latency_metrics, ... }          │   │
│  │    }]                                                           │   │
│  │  }                                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  3. Submit to AgentBeats Leaderboard                                    │
│     - Copy results to submissions/ and results/ directories             │
│     - Create PR to upstream repository                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Acceptance Criteria:**

**Agent Registration:**
- [ ] Green Agent registered at agentbeats.dev with valid `agentbeats_id`
- [ ] Purple Agent registered at agentbeats.dev with valid `agentbeats_id`
- [ ] `scenario.toml` contains valid `agentbeats_id` for both agents
- [ ] Docker images accessible at `ghcr.io/${GH_USERNAME}/green-agent:latest` and `purple-agent:latest`

**Scenario Configuration:**
- [ ] `scenario.toml` properly configures `[green_agent]` and `[[participants]]`
- [ ] `generate_compose.py` successfully resolves images from agentbeats.dev API
- [ ] Generated `docker-compose.yml` includes all required services
- [ ] Generated `a2a-scenario.toml` contains correct endpoints

**E2E Execution:**
- [ ] Green Agent receives task from `agentbeats-client`
- [ ] Green Agent sends A2A `message/send` to Purple Agent
- [ ] Green Agent captures `InteractionStep` traces during communication
- [ ] Green Agent computes `GraphMetrics` via NetworkX from traces
- [ ] Green Agent returns structured evaluation results

**Results Output (`output/results.json`):**
- [ ] File created at `output/results.json`
- [ ] Contains `participants` object with agent UUIDs
- [ ] Contains `results` array with evaluation data
- [ ] Each result includes: `score`, `domain`, `pass_rate`, `max_score`, `time_used`
- [ ] Each result includes `task_rewards`: `overall_score`, `graph_density`, `coordination_quality`
- [ ] Each result includes `detail`: `graph_metrics`, `latency_metrics`, `reasoning`

**Workflow Validation:**
- [ ] `.github/workflows/agentbeats-run-scenario.yml` executes successfully
- [ ] Provenance recorded via `record_provenance.py`
- [ ] Submission branch created with results

**results.json Schema:**

```json
{
  "participants": {
    "agent": "<participant-uuid>"
  },
  "results": [
    {
      "pass_rate": 80.0,
      "time_used": 0.0,
      "max_score": 100.0,
      "domain": "graph-assessment",
      "score": 80.0,
      "task_rewards": {
        "overall_score": 0.8,
        "graph_density": 0.5,
        "coordination_quality": 0.33
      },
      "detail": {
        "overall_score": 0.8,
        "reasoning": "Evaluation summary",
        "coordination_quality": "high|medium|low|bottleneck",
        "strengths": [],
        "weaknesses": [],
        "graph_metrics": {
          "graph_density": 0.5,
          "has_bottleneck": false,
          "isolated_agents": [],
          "coordination_quality": "medium"
        },
        "latency_metrics": {
          "avg": 1250.0,
          "p50": 1000.0,
          "p95": 2000.0,
          "p99": 2500.0
        }
      }
    }
  ]
}
```

**Leaderboard SQL Query (DuckDB):**

The AgentBeats leaderboard uses DuckDB to parse `results.json` files. The following query extracts metrics for the coordination benchmark:

```sql
-- AgentBeats Coordination Benchmark Leaderboard Query
-- Parses output/results.json for graph-based coordination metrics
SELECT
    json_extract_string(
        to_json(participants),
        '$.' || list_extract(json_keys(to_json(participants)), 1)
    ) AS participant_id,
    ROUND(res.pass_rate, 1) AS "Pass Rate",
    ROUND(res.score, 1) AS "Score",
    res.domain AS "Domain",
    ROUND(res.task_rewards.overall_score * 100, 1) AS "Overall %",
    ROUND(res.task_rewards.graph_density * 100, 1) AS "Density %",
    CASE
        WHEN res.task_rewards.coordination_quality >= 0.66 THEN 'High'
        WHEN res.task_rewards.coordination_quality >= 0.33 THEN 'Medium'
        ELSE 'Low'
    END AS "Coordination",
    res.detail.coordination_quality AS "Quality",
    res.detail.graph_metrics.has_bottleneck AS "Bottleneck",
    COALESCE(list_length(res.detail.graph_metrics.isolated_agents), 0) AS "Isolated",
    ROUND(res.detail.latency_metrics.avg, 0) AS "Avg Latency (ms)",
    ROUND(res.detail.latency_metrics.p95, 0) AS "P95 Latency (ms)"
FROM results
CROSS JOIN UNNEST(results) AS r(res)
ORDER BY "Score" DESC, "Pass Rate" DESC;
```

**Query Output Columns:**

| Column | Source | Description |
|--------|--------|-------------|
| `participant_id` | `participants.agent` | Evaluated agent UUID |
| `Pass Rate` | `results[].pass_rate` | Percentage of passed evaluations |
| `Score` | `results[].score` | Overall score (0-100) |
| `Domain` | `results[].domain` | "graph-assessment" |
| `Overall %` | `task_rewards.overall_score` | LLM judge overall score |
| `Density %` | `task_rewards.graph_density` | Graph density metric |
| `Coordination` | `task_rewards.coordination_quality` | High/Medium/Low classification |
| `Quality` | `detail.coordination_quality` | Raw quality string |
| `Bottleneck` | `detail.graph_metrics.has_bottleneck` | Bottleneck detected |
| `Isolated` | `detail.graph_metrics.isolated_agents` | Count of isolated agents |
| `Avg Latency (ms)` | `detail.latency_metrics.avg` | Average response time |
| `P95 Latency (ms)` | `detail.latency_metrics.p95` | 95th percentile latency |

**Technical Requirements:**

- `agentbeats-client` container (v1.0.0) orchestrates the evaluation
- Green Agent must respond to tasks initiated by `agentbeats-client`
- Results must be written to `/app/output/results.json` (mounted volume)
- All agents must pass healthchecks before `agentbeats-client` starts

**Green Agent Evaluation Modes:**

The Green Agent supports two evaluation modes, both producing the same `output/results.json` format:

| Mode | Trigger | Use Case | Trace Source |
|------|---------|----------|--------------|
| **Ground Truth** | `task.interaction_pattern` provided | Unit tests, accuracy validation | JSON → InteractionStep |
| **Live A2A** | No `interaction_pattern` | Production, E2E tests | Actual A2A communication |

**Live A2A Evaluation Flow (Production Mode):**

```text
agentbeats-client                    Green Agent                     Purple Agent
      │                                   │                                │
      │  POST / (message/send)            │                                │
      │  {"task": {"description": "..."}} │                                │
      │──────────────────────────────────►│                                │
      │                                   │                                │
      │                                   │  POST / (message/send)         │
      │                                   │  A2A JSON-RPC request          │
      │                                   │───────────────────────────────►│
      │                                   │                                │
      │                                   │  ◄─── InteractionStep created  │
      │                                   │       (trace capture)          │
      │                                   │                                │
      │                                   │  JSON-RPC response             │
      │                                   │◄───────────────────────────────│
      │                                   │                                │
      │                                   │  GraphEvaluator.evaluate()     │
      │                                   │  - NetworkX builds DiGraph     │
      │                                   │  - Computes centrality metrics │
      │                                   │  - Detects bottlenecks         │
      │                                   │                                │
      │                                   │  LLMJudge.evaluate()           │
      │                                   │  - Semantic quality assessment │
      │                                   │                                │
      │                                   │  LatencyEvaluator.evaluate()   │
      │                                   │  - p50, p95, p99 percentiles   │
      │                                   │                                │
      │                                   │  Write output/results.json     │
      │                                   │  (AgentBeatsOutputModel)       │
      │                                   │                                │
      │  JSON-RPC response               │                                │
      │  {"result": {"status": "completed", "evaluation": {...}}}         │
      │◄──────────────────────────────────│                                │
```

**Key Implementation Details:**

1. **Trace Capture** (`src/green/messenger.py`):
   - `Messenger.send_message()` creates `InteractionStep` for each A2A call
   - Captures: `step_id`, `trace_id`, `call_type`, `start_time`, `end_time`, `latency`

2. **Graph Analysis** (`src/green/evals/graph.py`):
   - `GraphEvaluator._build_graph()` creates `nx.DiGraph` from traces
   - Nodes = agents (step_id), Edges = interactions (parent_step_id → step_id)
   - Computes: degree/betweenness/closeness centrality, density, clustering

3. **Results Generation** (`src/green/server.py`):
   - `_process_evaluation_request()` orchestrates full evaluation
   - `AgentBeatsOutputModel.from_evaluation_results()` formats output
   - Writes to `settings.output_file` (default: `output/results.json`)

**E2E Test Requirements:**

- [ ] Test Live A2A mode: Green → Purple actual communication
- [ ] Test trace capture during real `message/send` exchange
- [ ] Test NetworkX graph built from captured traces (not JSON patterns)
- [ ] Test `output/results.json` written with correct schema
- [ ] Test via `docker-compose-local.yaml` (no mocking)
- [ ] Test via GitHub Actions workflow (full submission simulation)

**Files:**

- `scenario.toml` - AgentBeats scenario configuration
- `.github/workflows/agentbeats-run-scenario.yml` *(exists)*
- `scripts/leaderboard/generate_compose.py` *(exists)*
- `scripts/leaderboard/record_provenance.py` *(exists)*
- `output/results.json` - Generated evaluation results
- `Dockerfile.green` *(exists)*
- `Dockerfile.purple` *(exists)*
- `docker-compose-local.yaml` *(exists)*
- `tests/e2e/test_live_a2a_evaluation.py` *(new - validates Live A2A mode)*

---

#### Feature 7: Shared Infrastructure and Trace Collection

**Description:** Shared infrastructure (common module) for code reuse between Green and Purple agents, plus Green Agent endpoints for receiving trace reports from Purple agents.

**Acceptance Criteria:**

- [ ] Common module with shared models (CallType, InteractionStep, JSONRPC)
- [ ] Common LLMSettings shared between Green and Purple
- [ ] Common Messenger eliminates code duplication
- [ ] TraceReporter for async fire-and-forget trace reporting
- [ ] PeerDiscovery supports static peers + Green registry
- [ ] Green `/traces` endpoint receives async trace reports
- [ ] Green `/register` and `/peers` endpoints for agent registry
- [ ] All existing tests continue to pass
- [ ] New tests for common module and trace infrastructure

**Technical Requirements:**

- httpx for async HTTP client
- Backward compatible re-exports
- Fire-and-forget trace reporting (non-blocking)

**Files:**

- `src/common/__init__.py`
- `src/common/models.py`
- `src/common/settings.py`
- `src/common/messenger.py`
- `src/common/llm_client.py`
- `src/common/trace_reporter.py`
- `src/common/peer_discovery.py`
- `src/green/trace_store.py`
- `src/green/server.py` (add endpoints)

**Note:** Purple Agent extensions (LLM capability, trace reporting integration, role system) are defined in [PurpleAgent-PRD.md](PurpleAgent-PRD.md).

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

Story Breakdown (23 stories total):

- **Feature 1 (A2A Protocol Communication)** → STORY-001: Messenger with A2A SDK + extensions, STORY-002: InteractionStep model integration (depends: STORY-001), STORY-003: Executor with trace collection and cleanup (depends: STORY-002), STORY-004: Add OpenAI dependency to pyproject.toml (depends: STORY-003), STORY-005: Green Agent business logic (agent.py) (depends: STORY-004), STORY-006: Green Agent A2A HTTP server (server.py) (depends: STORY-005)
- **Feature 2 (Graph-Based Coordination Analysis)** → STORY-013: Graph evaluator test suite (depends: STORY-003), STORY-014: Graph-based coordination analysis implementation (depends: STORY-013)
- **Feature 3 (LLM-Based Qualitative Evaluation)** → STORY-007: LLM client configuration with environment variables (depends: STORY-006), STORY-008: LLM prompt engineering for coordination assessment (depends: STORY-007), STORY-009: LLM API integration with fallback to rule-based evaluation (depends: STORY-008)
- **Feature 4 (Latency Metrics Evaluation)** → STORY-010: Latency metrics evaluator (depends: STORY-009)
- STORY-011: Wire all evaluators in Executor pipeline (depends: STORY-003, STORY-010)
- **Feature 5 (Extensibility Documentation)** → STORY-012: Extensibility documentation and examples (depends: STORY-011)
- **Feature 6 (E2E Testing Infrastructure)** → STORY-015: Base Purple Agent implementation (depends: STORY-003), STORY-016: E2E test suite with ground truth validation + baseline tracing (depends: STORY-015, STORY-011)
- STORY-017: Create demo video script (depends: STORY-011)
- **Feature 7 (Shared Infrastructure + Trace Collection)** → STORY-018: Common module with shared models (depends: STORY-003), STORY-019: Common LLM settings and client factory (depends: STORY-018), STORY-020: Common messenger (depends: STORY-018), STORY-021: Trace reporter for async trace collection (depends: STORY-018), STORY-022: Peer discovery (depends: STORY-018), STORY-023: Green trace collector endpoints (depends: STORY-011, STORY-021)

**Note:** Purple Agent stories (STORY-024 to STORY-029) are defined in [PurpleAgent-PRD.md](PurpleAgent-PRD.md).

**Enhancement:** Feature 6.4 (E2E Baseline Tracing Test) can be implemented after STORY-023 (Green trace collector endpoints) completes, as it validates the full trace collection flow.

---

### Dependency Graph

```text
STORY-001 (Messenger with A2A SDK)
    ↓
STORY-002 (InteractionStep model)
    ↓
STORY-003 (Executor with trace collection)
    ├─────────────────┬─────────────┬─────────────────┬─────────────────┐
    ↓                 ↓             ↓                 ↓                 ↓
STORY-004      STORY-013      STORY-015         STORY-011        STORY-018
(OpenAI dep)   (Graph test)   (Purple Agent)    (Integration)    (Common models)
    ↓                 ↓                               ↑                 │
STORY-005      STORY-014                              │     ┌──────────┼──────────┬──────────┐
(Agent.py)     (Graph impl)                           │     ↓          ↓          ↓          ↓
    ↓                                                 │ STORY-019  STORY-020  STORY-021  STORY-022
STORY-006                                             │ (LLM cfg)  (Messenger)(TraceRep) (PeerDisc)
(Server.py)                                           │                          │
    ↓                                                 │                          │
STORY-007                                             │                          │
(LLM config)                                          │                          │
    ↓                                                 │                          │
STORY-008                                             │                          │
(LLM prompt)                                          │                          │
    ↓                                                 │                          │
STORY-009                                             │                          │
(LLM API)                                             │                          │
    ↓                                                 │                          │
STORY-010 ────────────────────────────────────────────┘                          │
(Latency)                                             │                          │
    ↓                                                 ↓                          │
STORY-011 (Integration) ──────────┬──────────────────┬──────────────┬────────────┘
    ↓                             ↓                  ↓              │
STORY-012                   STORY-017          STORY-016           │
(Extensibility docs)        (Demo script)      (E2E tests)         │
                                                    ↑              │
                                                    │              ↓
                                             STORY-015       STORY-023
                                             (Purple Agent)  (Green traces)
```

##### Feature 7 Dependency Graph (Detail)

```text
STORY-003 (Executor - PASSED)
    │
    ▼
STORY-018 (Common models)
    ├────────────┬────────────┬────────────┐
    ▼            ▼            ▼            ▼
STORY-019    STORY-020    STORY-021    STORY-022
(LLM settings)(Messenger) (TraceReporter)(PeerDiscovery)

STORY-011 (Integration - PASSED)
    │
    └──────────────┐
                   ▼
             STORY-023 (Green trace endpoints)
                   ↑
                   │
             STORY-021 (TraceReporter)
```

**Note:** Purple Agent stories (STORY-024 to STORY-029) continue from STORY-023 and are documented in [PurpleAgent-PRD.md](PurpleAgent-PRD.md).

### Verification After Each Phase

1. **Tests pass**: `make test_all`
2. **Type checking passes**: `make type_check`
3. **Formatting passes**: `make ruff`
4. **Manual validation**: Run green agent against purple agent, verify new metrics in output
5. **Platform validation**: Test with AgentBeats docker-compose pattern
