# Limitations & Scope Boundaries

> **Last Updated**: 2026-01-31
> **Phase**: 1 (Green Agent Focus)
> **Purpose**: Document current limitations, deferred features, and out-of-scope items

This document clearly defines what GraphJudge does NOT currently include, ensuring alignment with Phase 1 competition requirements and preventing over-engineering.

---

## Executive Summary

**Current Scope**: Green Agent (Benchmark/Evaluator) + Baseline Purple Agent (Test Fixture)

**Design Philosophy**: KISS, DRY, YAGNI - Minimal changes, reuse existing patterns, defer complex abstractions

**Phase 1 Deliverables**: Core graph-based evaluation with proven reproducibility

**Deferred to Phase 2**: Advanced features (ART training, self-evolution, PeerRead plugin)

---

## Phase 1 Scope Boundaries

### In Scope (Phase 1 - Current)

✅ **Green Agent Core**:
- A2A protocol communication (JSON-RPC 2.0)
- Three-tier evaluation pipeline (graph, LLM, latency)
- AgentCard endpoint and traceability extension
- Docker deployment (linux/amd64)
- Comprehensive test suite

✅ **Purple Agent Baseline**:
- A2A compliance for testing
- Basic coordination demonstration
- E2E validation fixture

✅ **Documentation**:
- Competition abstract
- Submission guide and registration guide
- README with quick start
- PRD for green and purple agents

### Out of Scope (Phase 1)

❌ **Not Included in Phase 1**:
- Advanced purple agent capabilities
- ART (Adaptive Reasoning Trees) training
- Self-evolving green agent
- Multi-benchmark federation
- Real-time dashboard/UI
- Advanced text similarity (PeerRead plugin beyond basic demo)

---

## Current Limitations

### 1. Green Agent Limitations

#### 1.1 LLM Dependency

**Limitation**: Tier 2 LLM evaluation requires external API (OpenAI)

**Impact**:
- Requires API key for full evaluation
- Network dependency for semantic assessment
- Potential cost for evaluation runs

**Mitigation**:
- LLM evaluation is optional (Tier 1 graph metrics standalone)
- Mock LLM responses for testing (`tests/test_green_llm_*.py`)
- Platform provides API key injection via `scenario.toml`

**Future Enhancement** (Phase 2):
- Support local LLM models (Ollama, LM Studio)
- Cached LLM responses for reproducibility
- Cost optimization via prompt batching

**Status**: ⏳ Deferred to Phase 2

---

#### 1.2 Graph Metrics Limited to NetworkX

**Limitation**: Graph analysis constrained by NetworkX capabilities

**Impact**:
- No real-time graph updates
- Limited to static post-hoc analysis
- No temporal graph evolution tracking

**Mitigation**:
- NetworkX provides industry-standard metrics
- Sufficient for coordination quality assessment
- Deterministic and reproducible

**Future Enhancement** (Phase 2):
- Temporal graph analysis (graph snapshots over time)
- Dynamic graph metrics (change detection)
- Graph ML features (GNN embeddings)

**Status**: ⏳ Deferred to Phase 2

---

#### 1.3 No Ground Truth Dataset

**Limitation**: No pre-labeled coordination quality dataset for validation

**Impact**:
- LLM judge output not validated against human annotations
- Coordination quality thresholds empirically chosen

**Mitigation**:
- Graph metrics are objective (NetworkX validation)
- LLM prompts reviewed for bias and clarity
- E2E tests validate pipeline correctness

**Future Enhancement** (Phase 2):
- Human annotation study for LLM judge calibration
- Ground truth coordination patterns from research papers
- Inter-rater reliability metrics

**Status**: ⏳ Deferred to Phase 2

---

#### 1.4 Latency Metrics Only

**Limitation**: Performance evaluation limited to latency (no throughput, CPU, memory)

**Impact**:
- Cannot detect resource exhaustion issues
- No cost-per-evaluation tracking

**Mitigation**:
- Latency is most critical SLA metric
- Percentile analysis (p50, p95, p99) covers edge cases
- Docker resource limits can be set externally

**Future Enhancement** (Phase 2):
- CPU/memory profiling
- Throughput metrics (tasks per second)
- Cost analysis (API calls, compute time)

**Status**: ⏳ Deferred to Phase 2

---

#### 1.5 Single Evaluation Per Run

**Limitation**: No batch evaluation or multi-scenario testing

**Impact**:
- Must run green agent multiple times for different scenarios
- No aggregation across evaluation runs

**Mitigation**:
- AgentBeats platform handles batch orchestration
- Stateless design enables parallel runs
- Each run is reproducible (0% variance)

**Future Enhancement** (Phase 2):
- Batch evaluation API endpoint
- Scenario configuration files
- Aggregated leaderboard statistics

**Status**: ⏳ Deferred to Phase 2

---

### 2. Purple Agent Limitations

#### 2.1 Baseline Only (No Advanced Coordination)

**Limitation**: Purple agent implements minimal coordination logic

**Impact**:
- Demonstrates basic A2A compliance only
- Not competitive in coordination complexity
- Used as test fixture, not showcase agent

**Mitigation**:
- Phase 1 focuses on green agent (competition requirement)
- Purple agent sufficient for E2E validation
- Advanced purple agents can be developed in Phase 2

**Alignment with Competition**:
> "This phase of the implementation has to focus on the green agent. Enhanced features can be moved to purple agent phase if matching or to outlook/roadmap/todo."

**Status**: ✅ **Intentionally Limited** (Phase 1 Compliance)

---

#### 2.2 No Multi-Agent Purple Orchestration

**Limitation**: Single purple agent, not a multi-agent system

**Impact**:
- Cannot demonstrate complex multi-agent coordination patterns
- Green agent evaluates inter-agent interactions (requires multiple purples)

**Mitigation**:
- Phase 2 purple agents can form multi-agent systems
- Green agent designed to evaluate any A2A-compatible agents
- Third-party agents can participate in evaluation

**Future Enhancement** (Phase 2):
- Multi-purple agent scenarios (3-5 agents)
- Role-based coordination (leader, worker, reviewer)
- Competitive purple agents for leaderboard

**Status**: ⏳ Deferred to Phase 2

---

### 3. Platform Integration Limitations

#### 3.1 AgentBeats Registration Pending

**Limitation**: `agentbeats_id` not yet assigned

**Impact**:
- Cannot deploy to AgentBeats platform immediately
- `scenario.toml` has placeholder IDs

**Mitigation**:
- Configuration structure ready (`scenario.toml`)
- Docker images ready for GHCR push
- Registration guide documented (AGENTBEATS_REGISTRATION.md)

**Next Steps**:
1. Push Docker images to GHCR
2. Register on agentbeats.dev
3. Update `scenario.toml` with assigned IDs
4. Commit and push

**Status**: ⏳ **Pending Registration** (Ready for Deployment)

---

#### 3.2 No Real-Time Leaderboard Integration

**Limitation**: No live leaderboard updates or visualization

**Impact**:
- Results not displayed on AgentBeats platform automatically
- Manual submission required for leaderboard entry

**Mitigation**:
- AgentBeats platform provides leaderboard infrastructure
- Structured output format enables automatic parsing
- JSON schema defined for platform integration

**Future Enhancement** (Phase 2):
- Webhook for automatic leaderboard updates
- GraphQL API for result queries
- Dashboard UI for coordination visualizations

**Status**: ⏳ Deferred to Phase 2

---

### 4. Scalability Limitations

#### 4.1 No Distributed Evaluation

**Limitation**: Single-container evaluation (no horizontal scaling)

**Impact**:
- Evaluation speed limited by single instance
- Large multi-agent systems may exceed container resources

**Mitigation**:
- Stateless design enables multiple parallel instances
- Docker Compose can orchestrate multiple containers
- AgentBeats platform handles orchestration

**Future Enhancement** (Phase 2):
- Kubernetes deployment for horizontal scaling
- Distributed graph computation (Apache Spark)
- Sharded evaluation for large agent systems

**Status**: ⏳ Deferred to Phase 2

---

#### 4.2 No Trace Persistence

**Limitation**: Traces stored in memory only (no database)

**Impact**:
- Traces lost after container restart
- Cannot replay historical evaluations
- No long-term trend analysis

**Mitigation**:
- Stateless operation (competition requirement)
- Each evaluation run produces structured output
- Platform can persist results externally

**Future Enhancement** (Phase 2):
- Optional PostgreSQL backend for trace storage
- Trace replay API for debugging
- Historical trend visualization

**Status**: ⏳ Deferred to Phase 2

---

## Deferred Features (Phase 2 Outlook)

### 1. ART (Adaptive Reasoning Trees) Training

**Description**: Train reasoning trees on interaction traces to detect coordination anti-patterns

**Value**:
- Automated pattern recognition
- Transfer learning across domains
- Reduced LLM dependency

**Dependencies**:
- Large-scale trace dataset (1000+ evaluation runs)
- Ground truth coordination quality labels
- ML infrastructure (WeightWatcher or PerforatedAI)

**Status**: 🔜 **Phase 2 Outlook**

**References**:
- [WeightWatcher](https://github.com/calculatedcontent/weightwatcher)
- [PerforatedAI](https://github.com/PerforatedAI/PerforatedAI)

---

### 2. Self-Evolving Green Agent

**Description**: Green agent improves evaluation criteria based on feedback

**Value**:
- Adaptive to new coordination patterns
- Domain-specific tuning
- Community-driven benchmark evolution

**Dependencies**:
- DGM (Dynamic Graph Metrics) framework
- User feedback mechanism
- A/B testing infrastructure

**Status**: 🔮 **Phase 3 Outlook**

**References**:
- [DGM Paper](https://arxiv.org/abs/2410.04444)

---

### 3. PeerRead Text Similarity Plugin

**Description**: Advanced text similarity for semantic coordination analysis (Tier 3)

**Value**:
- Detect redundant communication
- Measure information flow efficiency
- Validate LLM judge outputs

**Dependencies**:
- PeerRead dataset
- Sentence transformers (SBERT)
- Vector similarity index

**Status**: 🔜 **Phase 2 Outlook**

**Current State**: Basic text evaluator interface defined (AGENTBEATS_REGISTRATION.md:353-410)

---

### 4. Multi-Benchmark Federation

**Description**: Federated evaluation across multiple green agents

**Value**:
- Cross-benchmark coordination analysis
- Universal agent ranking
- Meta-evaluation of evaluation quality

**Dependencies**:
- AgentBeats federation protocol
- Standardized output schema
- Trust and provenance framework

**Status**: 🔮 **Phase 3 Outlook**

---

## Known Technical Debt

### 1. Common Module Extraction

**Issue**: Shared code between green and purple agents not yet in `src/common/`

**Impact**:
- Minor code duplication in messenger, models
- Not critical for Phase 1 (separate Docker images)

**Mitigation Plan**:
- Phase 2: Extract common A2A utilities to `src/common/`
- Update Dockerfiles to include common module
- Reduce duplicate code

**Status**: ⏳ **Deferred to Phase 2**

**References**:
- `Dockerfile.green:29-30` (TODO comment)
- `Dockerfile.green:52-53` (TODO comment)

---

### 2. Mock vs. Real A2A Testing

**Issue**: Some tests use mocks instead of real A2A SDK calls

**Impact**:
- Reduced integration test coverage
- Potential edge cases missed

**Mitigation Plan**:
- Phase 2: Replace mocks with real A2A test agents
- Increase E2E test scenarios
- Add A2A protocol fuzzing tests

**Status**: ⏳ **Deferred to Phase 2**

---

### 3. Error Handling Coverage

**Issue**: Some evaluator errors return `{"error": str(e)}` without detailed context

**Impact**:
- Debugging difficulty for complex failures
- Limited observability

**Mitigation Plan**:
- Phase 2: Structured error types (Pydantic)
- Error taxonomy (network, validation, computation)
- Detailed error context (stack traces, input data)

**Status**: ⏳ **Deferred to Phase 2**

**Current Implementation**:
```python
# src/green/agent.py:81-93
try:
    return await self.graph_evaluator.evaluate(traces)
except Exception as e:
    return {"error": str(e)}  # TODO: Structured error types
```

---

## Out-of-Scope Items (Not Planned)

### 1. Real-Time Streaming Evaluation

**Reason**: Contradicts reproducibility requirement (clean state per run)

**Alternative**: Batch evaluation with deterministic results

**Status**: ❌ **Not Planned**

---

### 2. Agent Optimization Recommendations

**Reason**: Evaluation benchmark, not optimization tool

**Alternative**: Users interpret graph metrics for optimization

**Status**: ❌ **Not Planned**

---

### 3. Multi-Language Support (Non-Python Agents)

**Reason**: A2A protocol handles multi-language (language-agnostic)

**Alternative**: Any A2A-compatible agent (Java, Rust, etc.) can be evaluated

**Status**: ✅ **Already Supported** (via A2A protocol)

---

### 4. GUI/Dashboard (Phase 1)

**Reason**: Competition requires Docker CLI, not web UI

**Alternative**: AgentBeats platform provides visualization

**Status**: ⏳ **Deferred to Phase 2** (Optional Enhancement)

---

## Testing Limitations

### 1. Limited Purple Agent Diversity

**Limitation**: Single purple agent implementation

**Impact**:
- Cannot validate green agent against diverse coordination patterns
- Potential edge cases untested

**Mitigation**:
- E2E tests cover basic coordination scenarios
- Graph evaluator validated with synthetic ground truth
- Community purple agents will provide diversity (Phase 2)

**Status**: ⏳ **Deferred to Phase 2**

---

### 2. No Performance Benchmarking

**Limitation**: No standardized performance benchmarks (ops/sec, latency SLA)

**Impact**:
- Cannot compare green agent performance across versions
- Scalability limits unknown

**Mitigation**:
- Docker resource limits provide baseline
- Platform provides performance infrastructure
- Latency metrics track evaluation overhead

**Status**: ⏳ **Deferred to Phase 2**

---

### 3. No Load Testing

**Limitation**: Not tested under concurrent evaluation requests

**Impact**:
- Behavior under load unknown
- Potential race conditions undetected

**Mitigation**:
- Stateless design minimizes concurrency issues
- Single-container deployment (no distributed state)
- Platform handles load balancing

**Status**: ⏳ **Deferred to Phase 2**

---

## Documentation Limitations

### 1. No API Reference

**Limitation**: No OpenAPI/Swagger documentation

**Impact**:
- API exploration requires code reading
- Third-party integration more difficult

**Mitigation**:
- Pydantic models provide JSON schema
- A2A protocol defines standard endpoints
- Code docstrings document API behavior

**Status**: ⏳ **Deferred to Phase 2**

---

### 2. No Video Tutorials (Besides Demo)

**Limitation**: Only demo video (max 3 minutes)

**Impact**:
- Limited onboarding resources for new users
- Complex concepts (graph metrics) require video explanation

**Mitigation**:
- QUICKSTART.md provides step-by-step guide
- README.md has clear architecture diagrams
- Demo video covers core workflow

**Status**: ⏳ **Deferred to Phase 2** (Tutorial Series)

---

## Compliance with Phase 1 Requirements

**Competition Guidance**:
> "We want to make sure to be aligned with the source and not to overengineer. This phase of the implementation has to focus on the green agent. Enhanced features can be moved to purple agent phase if matching or to outlook/roadmap/todo."

**Our Compliance**: ✅ **Fully Aligned**

**Evidence**:
1. ✅ Green agent core complete (evaluation pipeline, A2A, Docker)
2. ✅ Purple agent minimal baseline (test fixture only)
3. ✅ Advanced features deferred to Phase 2 (ART, self-evolution, PeerRead)
4. ✅ Roadmap transparency (README.md documents phases)
5. ✅ No over-engineering (KISS, DRY, YAGNI principles)

**Deferred Features Clearly Documented**:
```markdown
# README.md:60-71
- ✅ Phase 1: A2A + Graph + Basic eval (current)
- 🔜 Phase 2 (outlook): ART training on traces
- 🔮 Phase 3 (outlook): Self-evolving GreenAgent

**Note**: Time constraints limited full implementation of advanced features
planned in Phase 2 and 3. Current release focuses on core graph-based
evaluation with proven reproducibility.
```

---

## Conclusion

**Scope Clarity**: ✅ **Well-Defined** (Phase 1 deliverables vs. future enhancements)

**Over-Engineering Risk**: ✅ **Mitigated** (KISS, DRY, YAGNI principles)

**Phase 1 Compliance**: ✅ **Fully Aligned** (green agent focus, minimal purple)

**Transparency**: ✅ **Documented** (limitations, deferrals, roadmap)

**Key Takeaways**:
1. Current scope focuses on green agent core (competition requirement)
2. Advanced features deferred to Phase 2 (no over-engineering)
3. Limitations documented for community contribution
4. Roadmap provides clear path for future enhancements

---

## References

- Competition Alignment: [docs/AgentBeats/COMPETITION-ALIGNMENT.md](COMPETITION-ALIGNMENT.md)
- Roadmap: [README.md](../../README.md#roadmap)
- Phase 2 Outlook: [docs/TODO.md](../TODO.md)
- Green Agent PRD: [docs/GreenAgent-PRD.md](../GreenAgent-PRD.md)
