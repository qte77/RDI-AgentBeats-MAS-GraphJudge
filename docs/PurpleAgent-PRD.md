---
title: Product Requirements Document - Purple Agent (Baseline Participant)
version: 1.0
applies-to: Agents and humans
purpose: How, Technical requirements for the baseline Purple Agent test fixture
---

> See [PurpleAgent-UserStory.md](PurpleAgent-UserStory.md) for vision and value proposition.
>
> **Scope**: This PRD covers the **Purple Agent (Assessee)** - the baseline test fixture for E2E validation.
>
> **Implementation Location:**
>
> - **Purple Agent**: `src/purple/` → containerized by `Dockerfile.purple` → pushed as `purple-agent:latest` via `scripts/docker/push.sh`
>
> For Green Agent requirements, see [GreenAgent-PRD.md](GreenAgent-PRD.md).

## Project Overview

**Project Goal:** Provide a minimal A2A-compliant agent for E2E testing and reference implementation.

**Summary:** Simple test fixture that responds to A2A protocol requests, enabling Green Agent evaluation pipeline validation.

**Architecture:**

```text
┌─────────────────────────────────────────────────────┐
│                 AgentBeats Platform                  │
└─────────────────────────────────────────────────────┘
                          │ A2A Protocol
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│   Green Agent    │◄──────────►│  Purple Agent    │
│   (Assessor)     │  message/  │  (Assessee)      │
│   Port: 9009     │    send    │  Port: 9010      │
└──────────────────┘            └──────────────────┘
```

**Design Principles:** KISS, DRY, YAGNI - minimal implementation, test fixture only.

**Platform Compatibility:** A2A protocol compliance, Docker deployment.

---

## Functional Requirements

### Feature 1: A2A Protocol Server

**Description:** HTTP server implementing A2A protocol with AgentCard and JSON-RPC 2.0 endpoint.

**Acceptance Criteria:**

- [x] FastAPI-based HTTP server
- [x] AgentCard endpoint at `/.well-known/agent-card.json`
- [x] JSON-RPC 2.0 handler at `/` (POST)
- [x] Health check endpoint at `/health`
- [x] Handles `message/send` method
- [x] Returns valid JSON-RPC success/error responses
- [x] Configurable host/port via environment variables

**Technical Requirements:**

- FastAPI for HTTP server
- Pydantic for request/response validation
- uvicorn for ASGI server

**Files:**

- `src/purple/server.py`
- `src/purple/models.py`

---

### Feature 2: AgentCard Configuration

**Description:** AgentCard metadata declaration per A2A specification.

**Acceptance Criteria:**

- [x] Returns valid AgentCard JSON structure
- [x] Includes agentId (UUID)
- [x] Includes name and description
- [x] Declares A2A protocol capability
- [x] Lists available endpoints

**AgentCard Structure:**

```json
{
  "agentId": "<UUID>",
  "name": "Purple Agent (Test Fixture)",
  "description": "Simple A2A-compliant agent for E2E testing and validation",
  "capabilities": {
    "protocols": ["a2a"],
    "extensions": []
  },
  "endpoints": {
    "a2a": "/",
    "health": "/health"
  }
}
```

**Files:**

- `src/purple/server.py` (get_agent_card function)
- `src/purple/settings.py`

---

### Feature 3: Task Processing

**Description:** Simple task processing that echoes input for testing purposes.

**Acceptance Criteria:**

- [x] Extracts task description from JSON-RPC params
- [x] Returns processed result string
- [x] Validates required fields (task.description)
- [x] Returns appropriate error for missing fields

**Request Format:**

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "message/send",
  "params": {
    "task": {
      "description": "Task to process"
    }
  }
}
```

**Response Format:**

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "status": "completed",
    "response": "Purple Agent processed: Task to process"
  }
}
```

**Files:**

- `src/purple/agent.py`
- `src/purple/executor.py`

---

### Feature 4: Configuration Management

**Description:** Centralized configuration via pydantic-settings with environment variable support.

**Acceptance Criteria:**

- [x] PurpleSettings class with pydantic-settings
- [x] Environment variable prefix: `PURPLE_`
- [x] Configurable: host, port, card_url, agent_uuid
- [x] Default port: 9010
- [x] Auto-constructed card URL from host/port if not set

**Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `PURPLE_HOST` | Server bind host | `0.0.0.0` |
| `PURPLE_PORT` | Server bind port | `9010` |
| `PURPLE_CARD_URL` | AgentCard URL | `http://{host}:{port}` |
| `AGENT_UUID` | Agent identifier | Generated UUID |

**Files:**

- `src/purple/settings.py`

---

### Feature 5: CLI Interface

**Description:** Command-line interface for server startup.

**Acceptance Criteria:**

- [x] `--host` argument for bind host
- [x] `--port` argument for bind port
- [x] `--card-url` argument for AgentCard URL
- [x] Defaults from PurpleSettings

**Usage:**

```bash
# Default startup
python -m purple.server

# Custom configuration
python -m purple.server --host 0.0.0.0 --port 8001
```

**Files:**

- `src/purple/server.py` (parse_args, main functions)

---

### Feature 6: Docker Deployment

**Description:** Containerized deployment for platform compatibility.

**Acceptance Criteria:**

- [x] Dockerfile.purple builds successfully
- [x] Container runs without configuration changes
- [x] Binds to 0.0.0.0 (not localhost)
- [x] Platform: linux/amd64
- [x] Stateless operation

**Docker Configuration:**

```dockerfile
FROM python:3.13-slim
# ... build steps ...
ENTRYPOINT ["python", "-m", "purple.server"]
CMD ["--host", "0.0.0.0", "--port", "9010"]
```

**Files:**

- `Dockerfile.purple`
- `docker-compose.yml`

---

## Non-Functional Requirements

### Performance

- Response time: <100ms for typical requests
- Memory footprint: <100MB
- Startup time: <5 seconds

### Reliability

- Stateless: No persistent state between requests
- Deterministic: Same input produces same output
- Graceful error handling: Returns valid JSON-RPC errors

### Security

- No authentication required (test fixture)
- Input validation via Pydantic
- No arbitrary code execution

### Testability

- Unit tests for all components
- Integration tests with Green Agent
- E2E tests via docker-compose

---

## File Structure

```text
src/purple/
├── __init__.py       # Package initialization
├── agent.py          # Business logic
├── executor.py       # Task execution
├── messenger.py      # A2A messaging (placeholder)
├── models.py         # Pydantic models
├── server.py         # FastAPI HTTP server
└── settings.py       # Configuration
```

---

## Testing

### Unit Tests

```bash
uv run pytest tests/test_purple_*.py -v
```

### Integration Tests

```bash
# Start both agents
docker-compose up -d

# Verify Purple Agent
curl http://localhost:9010/.well-known/agent-card.json
curl http://localhost:9010/health

# Send test request
curl -X POST http://localhost:9010/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"task":{"description":"test"}}}'
```

### E2E Tests

```bash
bash scripts/docker/e2e_test.sh
```

---

## Deployment

### Local Development

```bash
# Install dependencies
uv sync

# Run server
uv run python -m purple.server
```

### Docker

```bash
# Build
docker build -f Dockerfile.purple -t purple-agent:local .

# Run
docker run -p 9010:9010 purple-agent:local
```

### GHCR

```bash
# Tag and push
docker tag purple-agent:local ghcr.io/$GITHUB_USERNAME/purple-agent:latest
docker push ghcr.io/$GITHUB_USERNAME/purple-agent:latest
```

---

## Related Documentation

- [PurpleAgent-UserStory.md](PurpleAgent-UserStory.md) - Vision and value proposition
- [GreenAgent-PRD.md](GreenAgent-PRD.md) - Green Agent requirements
- [GreenAgent-UserStory.md](GreenAgent-UserStory.md) - Green Agent vision
- [AgentBeats/SUBMISSION-GUIDE.md](AgentBeats/SUBMISSION-GUIDE.md) - Platform submission

---

**Last Updated**: 2026-01-31
