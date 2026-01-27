# Quickstart

Get GraphJudge running in 5 minutes.

---

## Prerequisites

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install dependencies
uv sync
```

---

## Local Development

```bash
# Run validation
make validate

# Start server
uv run src/green/server.py --port 9009

# Test endpoint (in another terminal)
curl http://localhost:9009/.well-known/agent-card.json
```

---

## Docker Deployment

```bash
# Build and start
docker-compose up -d

# Verify agents
curl http://localhost:8001/.well-known/agent-card.json  # Green
curl http://localhost:8002/.well-known/agent-card.json  # Purple

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Platform Deployment

See [AgentBeats/AGENTBEATS_REGISTRATION.md](AgentBeats/AGENTBEATS_REGISTRATION.md) for:

- Pushing to GitHub Container Registry
- Registering agents on agentbeats.dev
- Updating scenario.toml

---

## Environment Variables

```bash
# LLM Judge (optional - falls back to rule-based)
export AGENTBEATS_LLM_API_KEY="sk-..."
export AGENTBEATS_LLM_BASE_URL="https://api.openai.com/v1"  # default
export AGENTBEATS_LLM_MODEL="gpt-4o-mini"  # default
```

---

## More Info

- **Platform registration**: [AgentBeats/AGENTBEATS_REGISTRATION.md](AgentBeats/AGENTBEATS_REGISTRATION.md)
- **Requirements**: [GreenAgent-PRD.md](GreenAgent-PRD.md)
