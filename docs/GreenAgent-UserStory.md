---
title: User Story - AgentBeats Graph-Based Coordination Benchmark
version: 2.0
applies-to: Agents and humans
purpose: Why and What, Product vision, value proposition, and success metrics
---

> **Scope**: This document covers the **Green Agent (Assessor)** - the benchmark system that evaluates coordination. The **Purple Agent (Assessee)** - the multi-agent system under test - will be documented separately.
>
> **Naming Convention**: Some AgentBeats docs use "White Agent" for assessee; this project solely  uses "Purple Agent" (equivalent role).
>
> **Protocol**: This benchmark is built on the **A2A (Agent-to-Agent) Protocol** (a2aprotocol.ai), using JSON-RPC 2.0 for agent communication and the A2A Traceability Extension for distributed call tracing. Compliant with **AgentBeats AAA** (docs.agentbeats.org, docs.agentbeats.org/Blogs/blog-2) requirements for assessor agents.

## Problem Statement

Current AgentBeats benchmarks primarily evaluate individual agent capabilities (coding, reasoning, tool use) rather than measuring **how agents coordinate**. Manual analysis of multi-agent interactions requires significant time and effort per benchmark run to identify coordination failures. Multi-agent systems often fail not from individual agent capability gaps, but from coordination breakdowns—centralized bottlenecks, communication inefficiencies, redundant work—and these patterns remain invisible without systematic analysis.

Existing evaluation approaches lack the ability to:

- Capture interaction patterns between agents during runtime
- Quantify coordination quality through structural analysis
- Distinguish effective collaboration from superficial task completion
- Provide actionable feedback on coordination bottlenecks

Without automated coordination analysis, many multi-agent failures stem from undiscovered collaboration issues rather than individual agent deficiencies.

## Target Users

1. **Benchmark creators**: Researchers and developers building AgentBeats benchmarks who need to reduce lengthy manual trace analysis to rapid automated evaluation per benchmark run
2. **Multi-agent system developers**: Engineers building agent frameworks who need objective metrics to identify coordination bottlenecks that cause most multi-agent system failures
3. **AgentBeats competition participants**: Teams competing in AgentBeats who want to understand their agents' collaboration effectiveness beyond task success rates and gain actionable insights for improvement

## Value Proposition

GraphJudge transforms multi-agent interactions into coordination graphs and evaluates collaboration quality through graph theory, LLM assessment, and performance analysis. Built on the A2A (Agent-to-Agent) protocol standard with JSON-RPC 2.0 and the A2A Traceability Extension, the Graph-Based Coordination Benchmark analyzes **how** agents collaborate, not just whether they succeed, reducing coordination analysis time from lengthy manual trace inspection to rapid automated evaluation.

By capturing agent-to-agent interactions via A2A protocol and building runtime coordination graphs, the benchmark reveals:

- **Coordination patterns**: Centralization, distribution, bottlenecks
- **Communication efficiency**: Message patterns, redundancy, isolation
- **Structural quality**: Graph metrics (centrality, clustering, efficiency)
- **Qualitative assessment**: LLM-based evaluation of collaboration quality

**This benchmark uniquely applies graph theory to analyze coordination patterns in multi-agent systems.**

This benchmark transforms abstract "collaboration quality" into concrete, measurable metrics grounded in graph theory and interaction analysis, delivering actionable insights that identify coordination-related failures invisible to traditional task-completion metrics.

**Outcome Validity**: High coordination scores genuinely reflect successful multi-agent collaboration, not superficial pattern matching. Graph metrics alone are insufficient—they must be validated against task outcomes to ensure coordination quality correlates with actual task success.

**Plugin Architecture**:

- **Primary**: Graph evaluator (coordination structure analysis)
- **Provided Plugins**: LLM-as-Judge (semantic quality, can ingest other plugin outputs), Latency (system performance, extensible), Text metrics (conventional NLP metrics)
- **Design Principle**: Graph metrics reveal *how* agents coordinated; LLM-as-Judge can synthesize insights from multiple plugin outputs (Graph, Text, Latency) to verify coordination led to *successful* task completion

## User Stories

### Benchmark Creator: Submit Multi-Agent Tasks

**As a** benchmark creator,
**I want to** submit multi-agent coordination tasks via A2A protocol,
**So that** I can evaluate how agent systems collaborate on complex problems.

**Acceptance Criteria:**

- [ ] GreenAgent exposes AgentCard at `/.well-known/agent-card.json` declaring evaluation capabilities
- [ ] Accepts task submissions via A2A JSON-RPC 2.0 protocol (`tasks.send` method)
- [ ] Supports configurable scenarios (agent URLs, task descriptions, expected interactions)
- [ ] Orchestrates multi-agent execution through A2A protocol Task lifecycle management
- [ ] Captures all agent-to-agent interactions during task execution via A2A Traceability Extension
- [ ] Returns structured evaluation results via A2A JSONRPCSuccessResponse with evaluation metrics

### System Developer: Capture Interaction Traces

**As a** multi-agent system developer,
**I want** all agent-to-agent communications captured during benchmark execution,
**So that** I can analyze coordination patterns post-execution.

**Acceptance Criteria:**

- [ ] Captures all agent-to-agent communications via A2A Traceability Extension
- [ ] Trace data captures sufficient information to reconstruct interaction sequence and analyze coordination patterns
- [ ] Uses production A2A protocol (not mock implementations)
- [ ] Efficient connection management per A2A best practices

### Researcher: Analyze Coordination Graphs

**As a** researcher studying multi-agent systems,
**I want** graph metrics computed from interaction traces,
**So that** I can objectively measure coordination quality.

**Acceptance Criteria:**

- [ ] Constructs coordination graph representation from captured A2A interaction traces
- [ ] **Pluggable metric system**: Each graph metric is a separate plugin that can be enabled/disabled
- [ ] Default metrics (all pluggable):
  - **Centrality metrics**: degree, betweenness, closeness, eigenvector, PageRank
  - **Structure metrics**: graph density, clustering coefficient, connected components
  - **Path metrics**: average path length, diameter
- [ ] Identifies coordination bottlenecks (high betweenness centrality agents)
- [ ] Detects isolated agents (degree = 0) and over-centralized patterns

### Competition Participant: Receive LLM-Based Evaluation

**As an** AgentBeats competition participant,
**I want** qualitative assessment of my agents' collaboration,
**So that** I understand semantic coordination quality beyond numerical metrics.

**Acceptance Criteria:**

- [ ] LLM Judge analyzes interaction traces for semantic quality assessment
- [ ] **Multi-plugin data ingestion**: Can optionally receive outputs from other evaluators (Graph metrics, Text metrics, Latency metrics) to inform holistic assessment
- [ ] Evaluation uses defined rubric: task alignment, communication clarity, workload distribution, bottleneck avoidance
- [ ] **Task outcome assessment**: Evaluates whether coordination led to successful task completion (not just "good-looking" patterns)
- [ ] When other plugin data available, LLM synthesizes graph structure insights + text quality + performance metrics for comprehensive evaluation
- [ ] Evaluation includes: overall_score (0-1), reasoning, coordination_quality, task_success indicator
- [ ] Identifies strengths and weaknesses in collaboration patterns
- [ ] Graceful fallback if LLM unavailable
- [ ] Consistent, reproducible scoring across runs

### Platform Operator: Measure Performance

**As a** platform operator running benchmarks at scale,
**I want** latency metrics for agent response times,
**So that** I can evaluate performance alongside coordination quality.

**Acceptance Criteria:**

- [ ] Captures timestamps for all agent interactions
- [ ] **Primary focus: Latency metrics** for simplicity: avg, p50, p95, p99
- [ ] Identifies slowest agents by URL
- [ ] **Extensible architecture**: System metrics evaluator can be extended to include throughput, memory usage, or other performance indicators in future
- [ ] Plugin interface supports adding new system metrics without modifying core evaluation logic
- [ ] Reports performance metrics alongside coordination scores
- [ ] Latency evaluation completes in <5 seconds for typical workloads

### Extensibility: Plugin-Based Evaluation System

**As a** benchmark maintainer,
**I want** a plugin architecture for evaluators with clear extension patterns,
**So that** I can extend evaluation criteria without modifying core code.

**Acceptance Criteria:**

- [ ] Evaluators follow consistent interface pattern (BaseEvaluator)
- [ ] **Two-level plugin architecture**:
  - **Level 1 - Evaluator Plugins**: Graph, LLM-Judge, Latency, Text (each can be enabled/disabled)
  - **Level 2 - Metric Plugins** (within Graph evaluator): Each metric (degree, betweenness, PageRank, etc.) is independently pluggable
- [ ] Plugin system with primary and secondary evaluators:
  - **Primary Plugin**: Graph evaluator (coordination structure—required)
  - **Provided Plugins**: LLM-Judge (semantic quality, can ingest other plugin outputs), Latency (performance, extensible to other system metrics), Text (NLP metrics)
  - **Custom Plugins**: User-defined evaluators via BaseEvaluator interface
- [ ] **Cross-plugin data flow**: LLM-Judge evaluator can optionally receive outputs from Graph, Text, and Latency evaluators for holistic assessment
- [ ] Graph metric plugins wrapped in consistent plugin interface (library choice in Constraints)
- [ ] Outcome correlation: Graph metrics can be cross-validated with task success via LLM-Judge or custom outcome evaluator
- [ ] New evaluators/metrics can be added without changing Executor core logic
- [ ] Latency evaluator extensible to additional system metrics (throughput, memory) via plugin pattern
- [ ] Documentation explains evaluator structure, integration points, and cross-plugin data flow
- [ ] TextEvaluator provided as plugin reference implementation

### E2E Testing: Validate with Base Purple Agent

**As a** benchmark developer,
**I want** a base Purple Agent and ground truth dataset for end-to-end testing,
**So that** I can validate the Green Agent evaluation pipeline works correctly.

**Acceptance Criteria:**

- [ ] Base Purple Agent implemented as A2A-compliant test fixture
- [ ] Ground truth dataset with labeled test scenarios for validation
- [ ] E2E tests validate both agents' AgentCards are accessible
- [ ] E2E tests verify Purple Agent generates expected outputs
- [ ] E2E tests verify Green Agent correctly classifies ground truth scenarios
- [ ] Comprehensive tests report accuracy metrics against ground truth
- [ ] Container orchestration supports isolated testing

### Demo Video Script: Showcase Evaluation Flow

**As a** competition judge,
**I want** a demo video script documenting the evaluation system flow,
**So that** I can understand the full evaluation flow and guide video production.

**Acceptance Criteria:**

- [ ] Script output: `docs/demo-video-script.md` (~3 minutes of content)
- [ ] Scene 1: Server startup and A2A endpoint verification
- [ ] Scene 2: Evaluation flow with trace capture
- [ ] Scene 3: Multi-tier results display (graph, LLM judge, latency)
- [ ] Includes narration text, screen actions, and timing cues

## Success Criteria

1. **A2A Protocol Compliance** (AgentBeats AAA ready):
   - 100% of agent interactions use A2A SDK with JSON-RPC 2.0 format
   - AgentCard accessible and valid per A2A specification at `/.well-known/agent-card.json`
   - All Task lifecycle operations follow A2A protocol specification
   - A2A Traceability Extension successfully captures distributed call traces
   - Any A2A-compatible agent can participate without custom integration
2. **Trace Capture Accuracy**: High accuracy of A2A Message interactions successfully captured (measured by comparing expected vs actual interaction count from A2A Traceability Extension)
3. **Dual Evaluation Coverage**: Every benchmark run produces both graph metrics AND LLM judge output (or fallback warning if LLM unavailable)
4. **Graph Metrics Quality**: Pluggable metrics successfully identify coordination patterns:
   - **Centrality plugins**: degree, betweenness, closeness, eigenvector, PageRank
   - **Structure plugins**: density, clustering coefficient, connected components
   - **Path plugins**: average path length, diameter
   - Bottleneck detection: High betweenness centrality flags coordinator agents
   - Isolation detection: Zero degree centrality identifies disconnected agents
   - Distribution quality: Graph density indicates collaboration spread
   - Outcome correlation: Graph metrics correlate with task success
5. **Statistical Validity**: Evaluation design accounts for benchmark noise:
   - Minimum 10 diverse scenarios recommended for statistically meaningful results and to enable graph metrics validation against text-based evaluation
   - Multiple evaluation runs supported to handle agent non-determinism
   - Results include confidence indicators when sample size is small
6. **Local Testability**: Complete benchmark execution verifiable rapidly on standard hardware
7. **Docker Deployment Ready**: Container orchestration runs green + purple agents with zero configuration changes
8. **E2E Validation**: End-to-end tests pass with base Purple Agent and ground truth dataset

## Constraints

1. **Python 3.13**: Implementation uses Python 3.13 runtime
2. **Agent Template Structure**: Green and Purple agents follow RDI green-agent-template pattern (see PRD for details)
3. **A2A Protocol Compliance**: Full compliance with a2aprotocol.ai specification including JSON-RPC 2.0, AgentCard, Traceability Extension, and MCP readiness
4. **AgentBeats Platform Compatibility**: Compatible with AgentBeats AAA platform requirements (see PRD for CLI interface details)
5. **Real-time Evaluation**: All evaluations complete rapidly
6. **Reproducibility**: Same trace input produces identical graph metrics (deterministic)
7. **Non-Determinism Aware**: LLM evaluation supports aggregation across multiple runs
8. **Security**: Least privilege operation—input validation, content sanitization, no arbitrary code execution
9. **Testing Infrastructure**: Base Purple Agent and ground truth dataset required for validation

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
