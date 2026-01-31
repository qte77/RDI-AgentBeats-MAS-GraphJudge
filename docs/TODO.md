# GraphJudge - TODO

**Project**: Graph-Based Multi-Agent Coordination Benchmark

> **See also:**
> - [GreenAgent-PRD.md](GreenAgent-PRD.md) - Product requirements and feature specifications
> - [GreenAgent-UserStory.md](GreenAgent-UserStory.md) - Vision and value proposition
> - [AgentBeats/SUBMISSION-GUIDE.md](AgentBeats/SUBMISSION-GUIDE.md) - Platform submission requirements
> - [AgentBeats/RESOURCES.md](AgentBeats/RESOURCES.md) - Platform links, A2A protocol references

---

## Testing & Quality

**Current Implementation**: Tests use HTTPX's `ASGITransport` for fast, isolated FastAPI testing.

- **ASGITransport**: Calls ASGI app handlers directly without HTTP server
  - **Speed**: ~0.7s test runs vs ~5s+ with real servers
  - **Reliability**: No port conflicts, no network dependencies
  - **Usage**: `AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`
  - See `tests/test_server.py` and `tests/test_purple_agent.py` for examples

### TODO

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

---

## Platform Integration

- [ ] **Agent registration flow**
  - [ ] AgentBeats platform registration
  - [ ] Agent UUID assignment
  - [ ] Capability declaration

- [ ] **Milestone: AgentBeats submission**
  - [ ] Successful result submission to agentbeats.dev
  - [ ] JSON output schema compliance
  - [ ] SQL integration for leaderboard

---

## Documentation

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
  - [x] Explain why traces are used (observability, graph construction) - see research/MULTI_AGENT_TRACING.md
  - [x] Document InteractionStep schema and parent-child relationships
  - [x] Show how traces map to coordination graphs
  - [x] Contrast with traditional metrics-only evaluation

---

## Open Design Decisions

### Trace Collection Strategy

**Status**: Design complete, awaiting implementation (YAGNI).

Fixed-rounds placeholder at `src/green/executor.py:25`. See `docs/research/trace-collection-strategy.md`.

### A2A Protocol Compliance

✅ **COMPLETED**: Migrated from `tasks.send` to A2A standard `message/send`.

**Spec**: <https://google.github.io/A2A/specification/>

**Updated Files**:
- ✅ `src/green/server.py:260` - Using `message/send`
- ✅ `src/purple/server.py:78` - Using `message/send`
- ✅ `scripts/docker/e2e_test.sh` - Updated all test requests
- ✅ Documentation updated (UserStory, PRD, Demo Script)

### Scenario Configuration

`scenario.toml` has placeholder `agentbeats_id`. See `docs/AgentBeats/AGENTBEATS_REGISTRATION.md`.

---

## Configuration Reference

| Feature | Green Agent | Purple Agent |
|---------|-------------|--------------|
| Settings | `src/green/settings.py` | `src/purple/settings.py` |
| Card URL | `GREEN_CARD_URL` or auto-construct | `PURPLE_CARD_URL` or auto-construct |
| Host/Port | `GREEN_HOST`/`GREEN_PORT` (9009) | `PURPLE_HOST`/`PURPLE_PORT` (9010) |
| Output | `GREEN_OUTPUT_FILE` → `output/results.json` | N/A |

**Output directories**: `output/` (runtime, gitignored) → `results/` (leaderboard) → `submissions/` (provenance)

**Provenance**: Workflow-generated via `scripts/leaderboard/record_provenance.py`, not agent-generated.

---

**Last Updated**: 2026-01-31
