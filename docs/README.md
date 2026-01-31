# Documentation Index

**Project**: Graph-Based Multi-Agent Coordination Benchmark

---

## Quick Navigation

### Start Here

1. **[ABSTRACT.md](ABSTRACT.md)** - TL;DR: USP and value proposition
2. **[GreenAgent-UserStory.md](GreenAgent-UserStory.md)** - Product vision, problem statement, scope
3. **[GreenAgent-PRD.md](GreenAgent-PRD.md)** - Technical requirements and story breakdown

### Implementation

1. **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes

### Platform Integration

1. **[AgentBeats/AGENTBEATS_REGISTRATION.md](AgentBeats/AGENTBEATS_REGISTRATION.md)** - Platform registration process

### Architecture

| Diagram | Focus |
|---------|-------|
| [ComponentDiagram.puml](arch_vis/ComponentDiagram.puml) | How is it composed? |
| [AgenticBenchArch.puml](arch_vis/AgenticBenchArch.puml) | How does evaluation work? |
| [TracingArchitecture.puml](arch_vis/TracingArchitecture.puml) | When do API calls happen? |

See [arch_vis/](arch_vis/) for PlantUML source files.

### Research & Design

1. **[AgentBeats/MULTI_AGENT_TRACING.md](AgentBeats/MULTI_AGENT_TRACING.md)** - Common module, tracing, plugin architecture (Feature 7)

### Reference

1. **[RESOURCES.md](RESOURCES.md)** - External links, tool docs

---

## Documentation Structure

```text
docs/
├── README.md (THIS FILE)
├── ABSTRACT.md (TL;DR)
├── GreenAgent-UserStory.md (vision, scope)
├── GreenAgent-PRD.md (requirements, stories)
├── QUICKSTART.md (developer setup)
├── RESOURCES.md (external links)
├── AgentBeats/
│   ├── AGENTBEATS_REGISTRATION.md
│   └── MULTI_AGENT_TRACING.md (Feature 7 design)
└── arch_vis/
    ├── ComponentDiagram.puml (how is it composed?)
    ├── AgenticBenchArch.puml (how does evaluation work?)
    └── TracingArchitecture.puml (when do API calls happen?)
```

---

## Development Workflow

```bash
# 1. Get running fast
Read: QUICKSTART.md

# 2. Understand the vision
Read: GreenAgent-UserStory.md → GreenAgent-PRD.md

# 3. Deploy to platform
Read: AgentBeats/AGENTBEATS_REGISTRATION.md
```

---

## Quick Reference

| Question | Document |
| ---------- | ---------- |
| TL;DR? | ABSTRACT.md |
| Full vision? | GreenAgent-UserStory.md |
| Requirements? | GreenAgent-PRD.md |
| Get started? | QUICKSTART.md |
| Architecture? | arch_vis/*.puml |
| Deploy? | AGENTBEATS_REGISTRATION.md |
| Tracing/plugins? | MULTI_AGENT_TRACING.md |

---

## TODO: Implementation Roadmap

### Testing & Quality

**Current Implementation**: Tests use HTTPX's `ASGITransport` for fast, isolated FastAPI testing.

- **ASGITransport**: Calls ASGI app handlers directly without HTTP server
  - **Speed**: ~0.7s test runs vs ~5s+ with real servers
  - **Reliability**: No port conflicts, no network dependencies
  - **Usage**: `AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`
  - See `tests/test_server.py` and `tests/test_purple_agent.py` for examples

**TODO**:

- [ ] **Test actual LLM connection (OpenAI standard)**
  - [ ] Green agent LLM judge connectivity tests
  - [ ] Purple agent LLM connectivity tests (if applicable)
  - [ ] Mock vs live API testing strategy
  - [ ] Fallback behavior verification

- [ ] **E2E testing with full evaluation pipeline**
  - [ ] Full Green-Purple integration flow
  - [ ] Tracing collection and graph construction
  - [ ] LLM-as-judge evaluation
  - [ ] AgentBeats output format validation
  - [ ] Latency metrics validation

- [ ] **Settings consolidation**
  - [ ] Audit codebase for hardcoded values that should be in settings.py
  - [ ] Move configuration to GreenSettings/PurpleSettings
  - [ ] Document all environment variables

- [ ] **Test organization and clarity**
  - [ ] Clean and clarify `docs/best-practices/testing-strategy.md`
  - [ ] Implement naming convention: `test_{green|purple}_<component>_<behavior>`
  - [ ] Separate core functionality tests (pytest) from edge case tests (hypothesis)
  - [ ] Organize tests: Core business logic, API contracts, integration points
  - [ ] Add property-based tests with Hypothesis for edge cases

- [ ] **Test coverage improvements**
  - [ ] Core functionality: Graph metrics, coordination scoring, evaluator pipelines
  - [ ] API contracts: A2A protocol, AgentCard endpoints, JSON-RPC handling
  - [ ] Edge cases: Empty traces, invalid inputs, numeric bounds (use Hypothesis)
  - [ ] Remove low-ROI tests (library behavior, trivial assertions)

### Platform Integration

- [ ] **Agent registration flow**
  - [ ] AgentBeats platform registration
  - [ ] Agent UUID assignment
  - [ ] Capability declaration

- [ ] **Milestone: AgentBeats submission**
  - [ ] Successful result submission to agentbeats.dev
  - [ ] JSON output schema compliance
  - [ ] SQL integration for leaderboard

### Documentation

- [ ] **Consolidate docs/ directory**
  - [ ] Audit and organize documentation files
  - [ ] Remove redundant or outdated documents
  - [ ] Standardize naming conventions
  - [ ] Create clear documentation hierarchy
  - [ ] Update cross-references between docs

- [x] **Update architecture visualizations**
  - [x] Refresh PlantUML diagrams in `arch_vis/`
  - [x] Add sequence diagrams for evaluation pipeline
  - [x] Document component interactions
  - [x] Add data flow diagrams (TracingArchitecture.puml)
  - [x] Ensure diagrams match current implementation

- [ ] **Local development workflow documentation**
  - [ ] Document how to trigger evaluation locally (not just server startup)
  - [ ] Add complete JSON-RPC request examples
  - [ ] Show expected response formats
  - [ ] Document Purple agent interaction for testing
  - [ ] Add troubleshooting guide

- [ ] **Clarify A2A contribution and agentification**
  - [ ] Document why/how this benchmark is agentified (per A2A philosophy)
  - [ ] Explain agent-to-agent coordination vs traditional evaluation
  - [ ] Reference: <https://docs.agentbeats.org/> and <https://docs.agentbeats.org/Blogs/blog-2/>
  - [ ] Articulate unique value proposition for A2A ecosystem

- [x] **Document trace-based evaluation approach**
  - [x] Explain why traces are used (observability, graph construction) - see A2A_TRACING_RESEARCH.md
  - [x] Document InteractionStep schema and parent-child relationships - see ARCHITECTURE_RESEARCH.md
  - [x] Show how traces map to coordination graphs - see PLUGIN_RESEARCH.md
  - [x] Contrast with traditional metrics-only evaluation - see research docs

---

## TODO: Open Design Decisions

### Trace Collection Strategy

**Current Status**: Fixed-rounds placeholder (`DEFAULT_COORDINATION_ROUNDS = 3`) marked as FIXME at `src/green/executor.py:25`.

**Design Document**: See `docs/trace-collection-strategy.md` for detailed analysis, options, and recommended hybrid approach.

**Status**: Design complete, awaiting implementation requirements (YAGNI - no PRD/user story yet).

### AgentCard URL Configuration

**Status**: ✓ **RESOLVED** - Both agents now support configurable URLs

Both agents now support URL configuration via environment variables or auto-construction from host/port settings.

**Implementation**:

- **Green agent**: `src/green/settings.py` with `get_card_url()` method
- **Purple agent**: `src/purple/settings.py` with `get_card_url()` method

**Usage**:

```bash
# Green agent - configurable via env var or auto-constructed
export GREEN_CARD_URL=https://green.example.com:9009
# or auto-construct: http://{GREEN_HOST}:{GREEN_PORT}

# Purple agent - configurable via env var or auto-constructed
export PURPLE_CARD_URL=https://purple.example.com:9010
# or auto-construct: http://{PURPLE_HOST}:{PURPLE_PORT}
```

### Output Path

**Status**: ✓ **RESOLVED** - Configurable with unified default behavior

**Unified behavior**: Agent writes to `output/results.json` in **both local and platform contexts** (no environment variable overrides needed).

**Implementation**: `src/green/settings.py` - `output_file` field with `GREEN_OUTPUT_FILE` env var support

**Default behavior (local & workflow)**:

```bash
# Always writes to output/results.json
python -m green.server
```

**Custom paths** (if needed):

```bash
export GREEN_OUTPUT_FILE=custom/path/results.json
python -m green.server
```

**Directory structure**:

- `output/` - Runtime evaluation outputs (gitignored, Docker volume mount)
  - Agent writes here in all contexts
  - Platform agentbeats-client reads from here
- `results/` - Leaderboard submissions (git-tracked)
  - Workflow copies `output/results.json` → `results/{timestamp}.json`
- `submissions/` - Full submission packages with provenance (git-tracked)
  - Workflow copies `output/provenance.json` → `submissions/{timestamp}.provenance.json`

**Platform workflow**:

1. Agent writes → `output/results.json` (runtime)
2. Workflow writes → `output/provenance.json` (metadata)
3. Workflow copies → `results/{name}.json` (leaderboard)
4. Workflow copies → `submissions/{name}.provenance.json` (full package)
5. Workflow creates PR with results/ and submissions/ files

**Previous**: Used hardcoded path, now fully configurable

### Dynamic Agent Discovery

Purple agent URL is configured via `PURPLE_AGENT_URL` environment variable, but true dynamic discovery (e.g., via service registry) is not implemented.

See `src/purple/server.py:121-122`.

### A2A Protocol Compliance

Current implementation uses non-standard `tasks.send` method. Should migrate to A2A standard `message/send`.

**A2A Protocol Specification**: <https://google.github.io/A2A/specification/>

**Files using non-standard `tasks.send`**:

- `src/green/server.py:176` - Green agent handler
- `src/purple/server.py:101` - Purple agent handler
- `scripts/docker/e2e_test.sh:152,166,180,268` - E2E test requests

**Required changes for A2A compliance**:

1. **Method**: Change from `tasks.send` to `message/send`
2. **Request params**: Use `params.message.parts[].text` instead of `params.task.description`
3. **Response format**: Return `status.state` and `artifacts[].parts[].text` structure

See `src/green/messenger.py` for A2A SDK client usage pattern.

### Provenance Generation

**Note**: Provenance is **workflow-generated**, not agent-generated.

`output/provenance.json` is auto-generated by the AgentBeats workflow (`.github/workflows/agentbeats-run-scenario.yml`) via `scripts/leaderboard/record_provenance.py`. This file contains build metadata (Docker image hashes, timestamps, etc.) for submission tracking.

**Local development**: Provenance file is not generated during local runs. It's only created during platform workflow execution.

### Scenario Configuration

`scenario.toml` has placeholder `agentbeats_id = ""`. Document required fields for registration.

See `docs/AgentBeats/AGENTBEATS_REGISTRATION.md`.
