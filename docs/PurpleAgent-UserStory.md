---
title: User Story - Purple Agent (Baseline Participant)
version: 1.0
applies-to: Agents and humans
purpose: Why and What, Product vision, value proposition for the baseline Purple Agent
---

> **Scope**: This document covers the **Purple Agent (Assessee)** - the baseline multi-agent system under test. The **Green Agent (Assessor)** - the benchmark system that evaluates coordination - is documented in [GreenAgent-UserStory.md](GreenAgent-UserStory.md).
>
> **Naming Convention**: Some AgentBeats docs use "White Agent" for assessee; this project uses "Purple Agent" (equivalent role).
>
> **Protocol**: This agent is built on the **A2A (Agent-to-Agent) Protocol** (a2aprotocol.ai), using JSON-RPC 2.0 for agent communication.

## Problem Statement

The Green Agent (Assessor) requires a baseline participant agent for:

1. **E2E Testing**: Validating the evaluation pipeline works correctly
2. **Reference Implementation**: Demonstrating A2A protocol compliance for third-party teams
3. **Benchmark Calibration**: Providing consistent baseline behavior for metric validation

Without a reference Purple Agent, benchmark creators cannot:

- Verify their Green Agent evaluation pipeline
- Demonstrate expected A2A protocol interactions
- Provide a working example for competition participants

## Target Users

1. **Benchmark developers**: Engineers building the Green Agent who need a test fixture for E2E validation
2. **Competition participants**: Teams entering AgentBeats who need a reference implementation of A2A protocol compliance
3. **Multi-agent system developers**: Engineers who want to understand the expected interface for Purple agents

## Value Proposition

The baseline Purple Agent provides:

- **A2A Protocol Compliance**: Fully compliant implementation demonstrating AgentCard, JSON-RPC 2.0, and task handling
- **Simple Reference**: Minimal implementation that's easy to understand and extend
- **E2E Testing Foundation**: Reliable test fixture for validating Green Agent evaluation
- **Documentation by Example**: Working code that demonstrates expected behavior

This baseline agent is intentionally simple. Production Purple agents (from competition participants) would implement sophisticated multi-agent coordination that the Green Agent evaluates.

## User Stories

### Benchmark Developer: Validate Evaluation Pipeline

**As a** benchmark developer,
**I want** a baseline Purple Agent for E2E testing,
**So that** I can verify the Green Agent evaluation pipeline works correctly.

**Acceptance Criteria:**

- [ ] Purple Agent exposes AgentCard at `/.well-known/agent-card.json`
- [ ] Responds to A2A JSON-RPC 2.0 `message/send` method
- [ ] Returns structured responses that Green Agent can evaluate
- [ ] Health endpoint available at `/health`
- [ ] Containerized via Docker for isolated testing

### Competition Participant: Reference Implementation

**As a** competition participant,
**I want** a reference Purple Agent implementation,
**So that** I understand the expected A2A protocol interface.

**Acceptance Criteria:**

- [ ] Clear, minimal code demonstrating A2A compliance
- [ ] AgentCard structure matches A2A specification
- [ ] JSON-RPC request/response format documented
- [ ] Easy to run locally for testing
- [ ] Source code serves as template for custom implementations

### Platform Operator: Reliable Test Fixture

**As a** platform operator,
**I want** a deterministic baseline agent,
**So that** I can calibrate benchmark scoring.

**Acceptance Criteria:**

- [ ] Consistent responses for identical inputs
- [ ] No external dependencies (LLM APIs, databases)
- [ ] Fast response times (<100ms typical)
- [ ] Stateless operation (no session state between requests)

## Success Criteria

1. **A2A Protocol Compliance**:
   - AgentCard accessible at `/.well-known/agent-card.json`
   - Handles `message/send` JSON-RPC method
   - Returns valid JSON-RPC responses

2. **E2E Testing**:
   - Green Agent can successfully call Purple Agent
   - Responses are parseable by Green Agent evaluation
   - Docker Compose orchestration works reliably

3. **Reference Quality**:
   - Code is clear and well-documented
   - Easy for third parties to understand and extend
   - Follows project code patterns

## Constraints

1. **Minimal Implementation**: Simple echo-style processing, not sophisticated AI
2. **No External Dependencies**: No LLM APIs, databases, or external services
3. **Stateless**: No persistent state between requests
4. **Deterministic**: Same input produces same output
5. **Fast**: Response time <100ms for typical requests

## Out of Scope

The following are explicitly excluded from the baseline Purple Agent:

1. **Sophisticated AI capabilities**: This is a test fixture, not a production agent
2. **Multi-agent coordination logic**: Complex coordination is what third-party Purple agents implement
3. **LLM integration**: No OpenAI or other LLM API calls
4. **Persistent storage**: No database or file system state
5. **Authentication/authorization**: Simple unauthenticated endpoint
6. **Production-grade error handling**: Basic error responses sufficient for testing

## Future Considerations

The baseline Purple Agent may be extended in future phases to:

- Demonstrate more complex A2A interactions
- Support multi-turn conversations
- Include configurable response patterns for testing edge cases
- Serve as a template generator for competition participants
