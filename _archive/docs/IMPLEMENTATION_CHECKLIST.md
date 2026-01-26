# Implementation Checklist

**Status**: Documentation complete, code implementation pending
**Last Updated**: 2026-01-26

> **Relationship to PRD**: This checklist provides technical implementation patterns and detailed setup instructions for [PRD.md](PRD.md) requirements. The PRD defines WHAT to build; this checklist defines HOW and WHEN.

---

## Pre-Implementation Requirements

### 1. Dockerfile Requirements

Both `Dockerfile.green` and `Dockerfile.purple` must include:

```dockerfile
# Multi-stage build for Python 3.13
FROM python:3.13-slim AS builder
# Specify platform for AgentBeats compatibility
ARG TARGETPLATFORM=linux/amd64

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install uv && uv sync --frozen

# Final stage
FROM python:3.13-slim
WORKDIR /app

# Copy installed dependencies
COPY --from=builder /app/.venv /app/.venv

# Copy source code
COPY src/ /app/src/

# Expose internal port
EXPOSE 8000

# Entry point with argparse support
ENTRYPOINT ["uv", "run", "src/agentbeats/server.py"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
```

**Critical Requirements**:
- Platform: `linux/amd64` (AgentBeats standard)
- Python: `3.13-slim` (project requirement)
- Port: Internal `8000` (mapped externally via docker-compose)
- Entry point: argparse-based, NOT uvicorn factory pattern
- Multi-stage: Optimize image size

**Validation**:
```bash
# Build and verify
docker build --platform linux/amd64 -f Dockerfile.green -t green-agent .
docker run -p 8001:8000 green-agent

# Test agent card
curl http://localhost:8001/.well-known/agent-card.json
```

### 2. Server Entry Point

**File**: `src/agentbeats/server.py`

```python
import argparse
import uvicorn
from agentbeats.agent_card import AGENT_CARD

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--card-url", default="http://localhost:8000")
    args = parser.parse_args()

    AGENT_CARD["url"] = args.card_url
    # app = create_app(agent_card=AGENT_CARD, executor=AgentExecutor())
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
```

### 3. docker-compose.yml

```yaml
version: '3.8'
services:
  green:
    build:
      context: .
      dockerfile: Dockerfile.green
      platform: linux/amd64
    ports: ["8001:8000"]
    environment:
      - AGENTBEATS_LLM_API_KEY=${AGENTBEATS_LLM_API_KEY}
    command: ["--host", "0.0.0.0", "--port", "8000"]
    networks: [agentbeats]

  purple:
    build:
      context: .
      dockerfile: Dockerfile.purple
      platform: linux/amd64
    ports: ["8002:8000"]
    command: ["--host", "0.0.0.0", "--port", "8000"]
    networks: [agentbeats]
    depends_on: [green]

networks:
  agentbeats:
```

### 4. A2A Messenger Implementation Pattern

**Key requirements**:
- Use `ClientFactory.connect()` from a2a-sdk
- Send `X-A2A-Extensions` header to activate traceability extension
- Capture `InteractionStep` for each agent call
- Store traces in list for Executor to process

```python
class Messenger:
    def __init__(self, green_agent_url: str):
        self.green_agent_url = green_agent_url
        self.trace_storage: list[InteractionStep] = []

    async def talk_to_agent(self, agent_url: str, message: dict, trace_id: str) -> InteractionStep:
        step_id = str(uuid.uuid4())
        start_time = datetime.now()

        # Activate A2A traceability extension
        headers = {"X-A2A-Extensions": "https://github.com/a2aproject/a2a-samples/extensions/traceability/v1"}

        try:
            client = await ClientFactory.connect(agent_url, headers=headers)
            response = await client.send_task(message)
            end_time = datetime.now()

            step = InteractionStep(
                step_id=step_id, trace_id=trace_id, call_type=CallType.AGENT,
                start_time=start_time, end_time=end_time,
                latency=int((end_time - start_time).total_seconds() * 1000),
                sender_url=self.green_agent_url, receiver_url=agent_url,
                message_content=message, task_id=response.task_id
            )
            self.trace_storage.append(step)
            return step
        except Exception as e:
            step = InteractionStep(
                step_id=step_id, trace_id=trace_id, call_type=CallType.AGENT,
                start_time=start_time, end_time=datetime.now(),
                error=str(e), sender_url=self.green_agent_url, receiver_url=agent_url
            )
            self.trace_storage.append(step)
            raise
```

### 5. Test Structure

Expected test files (initially create with `@pytest.mark.skip` stubs):

```
tests/
├── __init__.py
├── conftest.py                  # Shared fixtures
├── test_models.py               # InteractionStep, ResponseTrace validation
├── test_messenger.py            # A2A client, extension activation
├── test_executor.py             # Trace collection, evaluator orchestration
├── test_graph.py                # Graph metrics computation
├── test_llm_judge.py            # LLM API integration, fallback
├── test_latency.py              # Percentile calculations
└── integration/
    ├── __init__.py
    └── test_e2e_coordination.py # End-to-end benchmark execution
```

**Test Markers**:
```python
# pyproject.toml already defines:
markers = [
    "integration: marks tests as integration tests",
    "benchmark: marks tests as benchmark tests",
    "network: marks tests requiring network access",
]
```

**Example Stub**:
```python
# tests/test_messenger.py
import pytest

@pytest.mark.skip(reason="Implementation pending")
def test_messenger_sends_extension_header():
    """Verify X-A2A-Extensions header sent with requests."""
    pass

@pytest.mark.skip(reason="Implementation pending")
def test_messenger_captures_interaction_step():
    """Verify InteractionStep created for each agent call."""
    pass
```

---

## Implementation Order

### Phase 1: Foundation (Priority 1)
1. ✅ `src/agentbeats/models.py` - InteractionStep, ResponseTrace
2. ✅ `src/agentbeats/agent_card.py` - AGENT_CARD with extensions
3. ⏳ `src/agentbeats/server.py` - argparse entrypoint
4. ⏳ `Dockerfile.green`, `Dockerfile.purple` - Multi-stage builds
5. ⏳ Test stubs - All test files with `@pytest.mark.skip`

### Phase 2: Core Evaluation (Priority 2)
6. ⏳ `src/agentbeats/messenger.py` - A2A client with extensions
7. ⏳ `src/agentbeats/executor.py` - Trace collection orchestration
8. ⏳ `src/agentbeats/evals/graph.py` - NetworkX coordination analysis
9. ⏳ `src/agentbeats/evals/latency.py` - Percentile computation
10. ⏳ `src/agentbeats/evals/llm_judge.py` - OpenAI integration

### Phase 3: Testing & Integration (Priority 3)
11. ⏳ Unit tests - Remove `@pytest.mark.skip`, implement tests
12. ⏳ Integration test - End-to-end coordination evaluation
13. ⏳ Docker compose validation - `docker-compose up` test
14. ⏳ A2A conformance validation - Protocol compliance checks

---

## Validation Gates

### Gate 1: Foundation Complete
- [ ] Server starts with `uv run src/agentbeats/server.py`
- [ ] Agent card accessible at `http://localhost:8000/.well-known/agent-card.json`
- [ ] Docker builds successfully: `docker build -f Dockerfile.green .`
- [ ] All test stubs exist: `pytest --collect-only`

### Gate 2: Core Evaluation Complete
- [ ] Messenger captures InteractionStep for agent calls
- [ ] Executor collects traces into ResponseTrace
- [ ] Graph evaluator computes centrality metrics
- [ ] Latency evaluator computes percentiles
- [ ] LLM judge returns coordination assessment
- [ ] All unit tests pass: `uv run pytest -v`

### Gate 3: Integration Complete
- [ ] docker-compose up orchestrates green + purple agents
- [ ] End-to-end test passes: curl task submission → results
- [ ] A2A extensions activated (verify in traces)
- [ ] Platform compatibility validated (argparse, port 9009 support)

---

## Known Blockers

### Blocker 1: A2A SDK Installation
**Issue**: a2a-sdk may not be available on PyPI
**Resolution**: Check GitHub for installation instructions, may need git+https URL

### Blocker 2: LLM API Credentials
**Issue**: AGENTBEATS_LLM_API_KEY required for LLM judge
**Resolution**: Implement fallback to rule-based evaluation, document env setup

### Blocker 3: Purple Agent Implementation
**Issue**: Need baseline purple agent for testing
**Resolution**: Create minimal echo agent that responds to messages

---

## Documentation References

- **Architecture**: `docs/PRD.md` Features 1-5
- **Quick Commands**: `docs/AgentBeats/QUICKSTART.md` (get running fast)
- **Platform Registration**: `docs/AgentBeats/AGENTBEATS_REGISTRATION.md`
- **Domain Scope**: `docs/DOMAIN_FOCUS.md`

---

## Quick Start Commands

```bash
# Install dependencies
uv sync

# Run validation
make validate  # ruff, pyright, pytest

# Start server (after implementation)
uv run src/agentbeats/server.py --port 8000

# Build Docker images
docker build --platform linux/amd64 -f Dockerfile.green -t green-agent .
docker build --platform linux/amd64 -f Dockerfile.purple -t purple-agent .

# Run integration test
docker-compose up -d
curl http://localhost:8001/.well-known/agent-card.json
docker-compose down
```

---

## Success Criteria

Per `docs/UserStory.md`:

1. **A2A Protocol Compliance**: 100% interactions via A2A SDK ✅ (documented)
2. **Trace Capture Accuracy**: >95% of interactions captured (pending implementation)
3. **Dual Evaluation Coverage**: Graph metrics + LLM judge output (pending implementation)
4. **Local Testability**: Complete run in <2 minutes (pending implementation)
5. **Docker Deployment**: `docker-compose up` zero-config orchestration (pending implementation)
