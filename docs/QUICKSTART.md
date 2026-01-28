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

### Reference Table

| Variable | Default | Description |
|----------|---------|-------------|
| **Green Agent (Evaluator)** | | |
| `GREEN_HOST` | `0.0.0.0` | Server bind host |
| `GREEN_PORT` | `9009` | Server port |
| `GREEN_CARD_URL` | `http://{host}:{port}` | AgentCard URL (auto-constructed if not set) |
| `GREEN_OUTPUT_FILE` | `output/results.json` | Evaluation results output path |
| `AGENT_UUID` | `green-agent` | Agent identifier |
| `PURPLE_AGENT_URL` | `http://localhost:8002` | Purple agent URL for testing |
| **Purple Agent (Test Fixture)** | | |
| `PURPLE_HOST` | `0.0.0.0` | Server bind host |
| `PURPLE_PORT` | `9010` | Server port |
| `PURPLE_CARD_URL` | `http://{host}:{port}` | AgentCard URL (auto-constructed if not set) |
| **LLM Judge (Optional)** | | |
| `AGENTBEATS_LLM_API_KEY` | `None` | OpenAI-compatible API key (falls back to rule-based if not set) |
| `AGENTBEATS_LLM_BASE_URL` | `https://api.openai.com/v1` | LLM API base URL |
| `AGENTBEATS_LLM_MODEL` | `gpt-4o-mini` | Model identifier |

### Example Usage

```bash
# LLM Judge (optional - falls back to rule-based)
export AGENTBEATS_LLM_API_KEY="sk-..."
export AGENTBEATS_LLM_BASE_URL="https://api.openai.com/v1"  # default
export AGENTBEATS_LLM_MODEL="gpt-4o-mini"  # default

# Green Agent customization (optional)
export GREEN_OUTPUT_FILE="custom/path/results.json"
export GREEN_CARD_URL="https://my-domain.com:9009"

# Purple Agent (test fixture, rarely needs customization)
export PURPLE_PORT="8080"
```

---

## Results

After running an evaluation, results are written to:

```bash
# View results
cat output/results.json | jq

# Results directory structure
output/          # Runtime outputs (gitignored)
  results.json   # Evaluation results
results/         # Leaderboard submissions (git-tracked)
submissions/     # Full packages with provenance (git-tracked)
```

---

## More Info

- **Platform registration**: [AgentBeats/AGENTBEATS_REGISTRATION.md](AgentBeats/AGENTBEATS_REGISTRATION.md)
- **Requirements**: [GreenAgent-PRD.md](GreenAgent-PRD.md)
