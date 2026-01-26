# Purple Agent

Simple A2A-compatible demo agent for AgentBeats evaluation scenarios.

## Overview

Purple Agent is a minimal demonstration agent that implements the A2A (Agent-to-Agent) protocol. It serves as a baseline agent that can be evaluated by the AgentBeats GreenAgent assessor.

## Features

- A2A protocol compliance
- Simple coordination response capability
- Docker containerization
- Standard CLI arguments (`--host`, `--port`, `--card-url`)

## Quick Start

### Local Development

```bash
# Install dependencies
uv sync

# Run the agent
uv run python -m purpleagent.server

# Run on custom port
uv run python -m purpleagent.server --port 9010
```

### Docker

```bash
# Build the image
docker build -t purple-agent .

# Run the container
docker run -p 9010:9010 purple-agent

# Run with custom configuration
docker run -p 8080:8080 purple-agent --port 8080 --card-url http://localhost:8080
```

## A2A Endpoints

### Agent Card

```bash
curl http://localhost:9010/.well-known/agent-card.json
```

Returns agent metadata including capabilities and skills.

### Task Execution

The agent accepts A2A task requests and responds with simple coordination messages.

## Evaluation by GreenAgent

This purple agent can be evaluated by the AgentBeats GreenAgent:

1. Start the purple agent: `docker run -p 9010:9010 purple-agent`
2. Start the green agent: `docker run -p 9009:9009 green-agent`
3. Submit evaluation request to green agent with purple agent URL

## Architecture

```
src/purpleagent/
├── __init__.py       # Package initialization
└── server.py         # A2A server and executor

Dockerfile            # Container configuration
pyproject.toml        # Python dependencies
```

## Dependencies

- `a2a-sdk[http-server]>=0.3.20` - A2A protocol implementation
- `uvicorn>=0.38.0` - ASGI server
- `pydantic>=2.12.5` - Data validation
- Python >= 3.13

## License

BSD-3-Clause
