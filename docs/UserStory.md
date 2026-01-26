---
title: User Story - AgentBeats Graph-Based Coordination Benchmark
version: 2.0
applies-to: Agents and humans
purpose: Product vision, value proposition, and success metrics
---

# User Story: Graph-Based Coordination Benchmark

## Problem Statement

Current AgentBeats benchmarks evaluate individual agent capabilities (coding, reasoning, tool use) but don't measure **how agents coordinate**. Multi-agent systems fail not because individual agents lack capability, but because coordination breaks down—centralized bottlenecks, communication inefficiencies, redundant work.

Existing evaluation approaches lack the ability to:
- Capture interaction patterns between agents during runtime
- Quantify coordination quality through structural analysis
- Distinguish effective collaboration from superficial task completion
- Provide actionable feedback on coordination bottlenecks

## Target Users

1. **Benchmark creators**: Researchers and developers building AgentBeats benchmarks who need to evaluate multi-agent coordination patterns
2. **Multi-agent system developers**: Engineers building agent frameworks who need objective metrics for coordination quality
3. **AgentBeats competition participants**: Teams competing in AgentBeats who want to understand their agents' collaboration effectiveness beyond task success rates

## Value Proposition

The Graph-Based Coordination Benchmark analyzes **how** agents collaborate, not just whether they succeed. By capturing agent-to-agent interactions and building runtime coordination graphs, the benchmark reveals:

- **Coordination patterns**: Centralization, distribution, bottlenecks
- **Communication efficiency**: Message patterns, redundancy, isolation
- **Structural quality**: Graph metrics (centrality, clustering, efficiency)
- **Qualitative assessment**: LLM-based evaluation of collaboration quality

**No existing AgentBeats benchmark analyzes coordination patterns through graph structure.**

This benchmark transforms abstract "collaboration quality" into concrete, measurable metrics grounded in graph theory and interaction analysis.

## User Stories

### Benchmark Creator: Submit Multi-Agent Tasks

**As a** benchmark creator,
**I want to** submit multi-agent coordination tasks via A2A protocol,
**So that** I can evaluate how agent systems collaborate on complex problems.

**Acceptance Criteria:**
- [ ] GreenAgent accepts task submissions via A2A `tasks/send` endpoint
- [ ] Supports configurable scenarios (agent URLs, task descriptions, expected interactions)
- [ ] Orchestrates multi-agent execution through A2A protocol
- [ ] Captures all agent-to-agent interactions during task execution
- [ ] Returns structured evaluation results via A2A response

### System Developer: Capture Interaction Traces

**As a** multi-agent system developer,
**I want** all agent-to-agent communications captured during benchmark execution,
**So that** I can analyze coordination patterns post-execution.

**Acceptance Criteria:**
- [ ] Messenger captures TraceData for each agent interaction
- [ ] TraceData includes: sender, receiver, message content, timestamp, task_id
- [ ] Uses A2A SDK ClientFactory for real protocol communication (not mock REST)
- [ ] Client caching per agent URL to reduce connection overhead
- [ ] Proper cleanup of A2A clients after execution

### Researcher: Analyze Coordination Graphs

**As a** researcher studying multi-agent systems,
**I want** graph metrics computed from interaction traces,
**So that** I can objectively measure coordination quality.

**Acceptance Criteria:**
- [ ] Builds directed graph from TraceData (nodes = agents, edges = interactions)
- [ ] Computes graph centrality metrics (degree, betweenness, closeness)
- [ ] Identifies coordination bottlenecks (high betweenness centrality agents)
- [ ] Measures communication efficiency (graph density, clustering coefficient)
- [ ] Detects isolated agents (degree = 0) and over-centralized patterns

### Competition Participant: Receive LLM-Based Evaluation

**As an** AgentBeats competition participant,
**I want** qualitative assessment of my agents' collaboration,
**So that** I understand semantic coordination quality beyond numerical metrics.

**Acceptance Criteria:**
- [ ] LLM Judge analyzes interaction traces using real LLM API (not rule-based mock)
- [ ] Evaluation includes: overall_score (0-1), reasoning, coordination_quality assessment
- [ ] Identifies strengths and weaknesses in collaboration patterns
- [ ] Falls back to rule-based evaluation if LLM API unavailable (with warning)
- [ ] Uses temperature=0 for consistent scoring across runs

### Platform Operator: Measure Performance

**As a** platform operator running benchmarks at scale,
**I want** latency metrics for agent response times,
**So that** I can evaluate performance alongside coordination quality.

**Acceptance Criteria:**
- [ ] Captures timestamps for all agent interactions
- [ ] Computes latency percentiles: avg, p50, p95, p99
- [ ] Identifies slowest agents by URL
- [ ] Reports performance metrics alongside coordination scores
- [ ] Latency evaluation completes in <5 seconds for typical workloads

### Extensibility: Add Custom Evaluators

**As a** benchmark maintainer,
**I want** clear patterns for adding custom evaluators,
**So that** I can extend evaluation criteria without modifying core code.

**Acceptance Criteria:**
- [ ] Evaluators follow consistent interface pattern
- [ ] Documentation explains evaluator structure and integration points
- [ ] New evaluators can be added without changing Executor core logic
- [ ] Tier-based evaluation structure (tier1, tier2) is documented
- [ ] Examples provided for common evaluator types

## Success Criteria

1. **A2A Protocol Compliance**: 100% of agent interactions use A2A SDK (verified by agent card accessibility at `/.well-known/agent-card.json`)
2. **Trace Capture Accuracy**: >95% of agent interactions successfully captured in TraceData (measured by comparing expected vs actual interaction count)
3. **Dual Evaluation Coverage**: Every benchmark run produces both graph metrics AND LLM judge output (or fallback warning if LLM unavailable)
4. **Local Testability**: Complete benchmark execution passes with `uv run` + `curl` verification in <2 minutes on standard hardware
5. **Docker Deployment Ready**: `docker-compose up` successfully orchestrates green agent + test purple agents with zero configuration changes

## Constraints

1. **Python 3.13**: Implementation must use Python 3.13 with uv package manager
2. **A2A Protocol**: All agent communication via A2A SDK (a2a-sdk>=0.3.20), JSON-RPC 2.0 format
3. **AgentBeats Platform Compatibility**:
   - CLI args: `--host`, `--port`, `--card-url`
   - Entry point: argparse-based (not uvicorn factory)
   - Default port: 9009 (AgentBeats default)
   - Endpoints: `/.well-known/agent-card.json` accessible
4. **Real-time Evaluation**: All evaluations (graph + LLM + latency) complete in <30 seconds
5. **Reproducibility**: Same input traces produce identical graph metrics (deterministic)

## Out of Scope

1. **Real-time streaming evaluation**: Evaluation happens post-execution, not during task runtime
2. **Persistent metrics storage**: Results returned via A2A response only, no database persistence
3. **Metrics visualization UI**: Output is structured JSON, no built-in visualization dashboard
4. **Custom LLM fine-tuning**: Uses general-purpose LLMs with prompting, no domain-specific fine-tuning
5. **Performance profiling tools**: Basic latency metrics only, no deep profiling (scalene/py-spy)
6. **Non-coordination benchmarks**: Focus exclusively on multi-agent coordination, not individual agent capabilities
