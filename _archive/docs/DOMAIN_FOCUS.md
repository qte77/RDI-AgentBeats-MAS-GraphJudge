# Domain Focus: Graph-Based Coordination Benchmark

**Status**: Active Development
**Domain**: Multi-agent coordination pattern analysis
**Approach**: Graph theory + LLM-as-judge evaluation

---

## What This Project Does

Evaluates **HOW agents coordinate** through runtime interaction analysis:

1. **Capture** agent-to-agent interactions via A2A Traceability Extension
2. **Build** coordination graphs from interaction traces
3. **Analyze** collaboration patterns using NetworkX metrics
4. **Assess** semantic quality via LLM judge
5. **Report** coordination bottlenecks and efficiency scores

---

## What This Project Does NOT Do

❌ Evaluate individual agent capabilities (coding, reasoning, tool use)
❌ Measure task success rates or completion quality
❌ Assess domain-specific compliance or legal requirements
❌ Test single-agent performance benchmarks

---

## Core Architecture

```
Purple Agents (Multi-Agent System Under Test)
    ↓ A2A Protocol communication
Green Agent (Coordination Benchmark)
    ├─→ Messenger: Capture InteractionSteps
    ├─→ GraphEvaluator: NetworkX centrality analysis
    ├─→ LLMJudge: Semantic coordination assessment
    └─→ LatencyEvaluator: Performance percentiles
```

---

## Evaluation Metrics

### Tier 1: Graph Metrics (Quantitative)
- **Centrality**: Degree, betweenness, closeness
- **Efficiency**: Graph density, clustering coefficient
- **Bottlenecks**: High-centrality agents (>70% interactions)
- **Isolation**: Agents with zero interactions

### Tier 2: LLM Judge (Qualitative)
- Overall coordination score (0-1)
- Strengths/weaknesses in collaboration patterns
- Communication efficiency assessment
- Redundancy detection

### Tier 3: Comparative Metrics (System-Relative)
- **Latency Percentiles**: avg, p50, p95, p99 (milliseconds)
- **Bottleneck Detection**: Agents with disproportionately high response times
- **Cost/Token Tracking**: LLM call efficiency (when applicable)

**Important**: Tier 3 metrics are **relative** (same-system comparisons only). A 100ms response on laptop vs cloud is not comparable. Use these to identify coordination inefficiencies (e.g., "Agent A waits 10x longer than peers"), not absolute performance.

---

## Key Documents

### Primary (Green Agent - Assessor)
- [GreenAgent-UserStory.md](GreenAgent-UserStory.md) - Problem statement, value proposition
- [GreenAgent-PRD.md](GreenAgent-PRD.md) - Technical requirements, stories, evaluator pattern

### Quick Start
- [QUICKSTART.md](AgentBeats/QUICKSTART.md) - Get running in 5 minutes (commands only)
- [AGENTBEATS_REGISTRATION.md](AgentBeats/AGENTBEATS_REGISTRATION.md) - Platform deployment

### Reference
- [RESOURCES.md](AgentBeats/RESOURCES.md) - External links, research papers
- [CompetitionAnalysis.md](AgentBeats/CompetitionAnalysis.md) - Competitive landscape

---

## Archived

Consolidated or outdated documentation moved to `_archive/docs/`:
- `AgentBeats/Technical-Implementation-Guide.md` (tax compliance domain)
- `AgentBeats/Green-Agent-Metrics-Specification.md` (risk scoring domain)
- `AgentBeats/A2A-Extension-Integration.md` (patterns → IMPLEMENTATION_CHECKLIST.md)
- `AgentBeats/Local-Testing-and-Deployment.md` (commands → QUICKSTART.md)
- `AgentBeats/AgentBeats-Research.md` (outdated competition context)
- `AgentBeats/AgentBeats-Benchmark-Design-Principles.md` (outdated competition context)
- `DOCUMENTATION_SUMMARY.md` (meta-documentation)
- `GAP_ANALYSIS.md` (deleted - redundant)

**Reason**: Focus on single domain (graph coordination), avoid confusion.

---

## Implementation Status

**Completed**:
- ✅ A2A-compliant InteractionStep model
- ✅ AgentCard with extension declarations
- ✅ PRD aligned with A2A specifications
- ✅ Integration guide documentation

**In Progress**:
- 🔄 Messenger with extension activation (Task #4)
- 🔄 Executor with trace collection (Task #5)
- 🔄 Server entrypoint with argparse (Task #10)

**Next**:
- ⏳ Graph evaluator (Task #6)
- ⏳ Latency evaluator (Task #7)
- ⏳ LLM Judge (Task #8)

---

## Quick Start (When Implemented)

```bash
# Install dependencies
uv sync

# Run green agent (local dev)
uv run src/agentbeats/server.py --port 8000

# Test against purple agents via docker-compose
docker-compose up -d
curl -X POST http://localhost:8001/tasks/send \
  -H "Content-Type: application/json" \
  -d '{"participants": {"agent1": "http://purple:8000"}}'

# View coordination metrics
cat results/trace_analysis.json
```

**Port Configuration**:
- Local development: Green=8001:8000, Purple=8002:8000 (external:internal)
- AgentBeats platform: Standardized on port 9009

---

## Success Criteria

Per [GreenAgent-UserStory.md Success Criteria](GreenAgent-UserStory.md#success-criteria):

1. **A2A Protocol Compliance**: 100% interactions via A2A SDK ✅
2. **Trace Capture Accuracy**: >95% of interactions captured
3. **Dual Evaluation Coverage**: Graph metrics + LLM judge output
4. **Local Testability**: Complete run in <10 minutes
5. **Docker Deployment**: `docker-compose up` zero-config orchestration

---

## Questions?

- **Get started fast?**: See [QUICKSTART.md](AgentBeats/QUICKSTART.md) (5-minute setup)
- **Architecture?**: See [GreenAgent-PRD.md](GreenAgent-PRD.md) Features 1-6
- **Platform deployment?**: See [AGENTBEATS_REGISTRATION.md](AgentBeats/AGENTBEATS_REGISTRATION.md)
