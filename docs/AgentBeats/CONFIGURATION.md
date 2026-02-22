# AgentBeats Configuration Reference

Complete environment variable reference for operators and contributors.

All configuration is handled via [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).
No manual `os.environ` lookups exist in the source — every variable below maps directly to a settings class field.

---

## Table of Contents

- [Shared Variables](#shared-variables)
- [Green Agent (GreenSettings)](#green-agent-greensettings)
- [Purple Agent (PurpleSettings)](#purple-agent-purplesettings)
- [LLM Settings (LLMSettings)](#llm-settings-llmsettings)
- [A2A Client Settings (A2ASettings)](#a2a-client-settings-a2asettings)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

---

## Shared Variables

These variables are read by **both** Green and Purple agents via `validation_alias`.
Set them once and they apply to whichever agent process reads them.

| Env Var | Default | Type | Description | Agent |
|---|---|---|---|---|
| `AGENT_UUID` | _(random UUID)_ | `str` (UUID) | Unique identifier for the agent. Auto-generated if not set. | Green, Purple |
| `AGENT_NAME` | `green-agent` | `str` | Display name for the agent. Purple overrides with `PURPLE_AGENT_NAME`. | Green |
| `PURPLE_AGENT_URL` | `http://0.0.0.0:9010` | `str` | URL Green uses to invoke the Purple agent. | Green |

---

## Green Agent (GreenSettings)

Prefix: `GREEN_`
Source: `src/green/settings.py`

| Env Var | Default | Type | Description | Agent |
|---|---|---|---|---|
| `GREEN_HOST` | `0.0.0.0` | `str` | Bind host for the Green agent HTTP server. | Green |
| `GREEN_PORT` | `9009` | `int` | Listen port for the Green agent HTTP server. | Green |
| `GREEN_PURPLE_PORT` | `9010` | `int` | Purple agent port used to construct the default `PURPLE_AGENT_URL`. | Green |
| `GREEN_LOG_LEVEL` | `info` | `str` | Uvicorn log level (`debug`, `info`, `warning`, `error`, `critical`). | Green |
| `GREEN_COORDINATION_ROUNDS` | `3` | `int` | Number of coordination rounds to run. Deprecated after STORY-031; has no effect when completion signals are active. | Green |
| `GREEN_ROUND_DELAY_SECONDS` | `0.1` | `float` | Delay in seconds between coordination rounds. | Green |
| `GREEN_AGENT_VERSION` | `1.0.0` | `str` | Agent version string published in the AgentCard. | Green |
| `GREEN_AGENT_DESCRIPTION` | _(long string)_ | `str` | Agent description published in the AgentCard. | Green |
| `GREEN_DOMAIN` | `graph-assessment` | `str` | Evaluation domain tag written to output results. | Green |
| `GREEN_MAX_SCORE` | `100.0` | `float` | Maximum possible score for evaluation output normalization. | Green |
| `GREEN_OUTPUT_FILE` | `output/results.json` | `str` (Path) | Path where evaluation results JSON is written. | Green |
| `GREEN_CARD_URL` | _(auto)_ | `str \| None` | Override for the AgentCard URL. Auto-constructed as `http://{GREEN_HOST}:{GREEN_PORT}` if not set. | Green |

---

## Purple Agent (PurpleSettings)

Prefix: `PURPLE_`
Source: `src/purple/settings.py`

| Env Var | Default | Type | Description | Agent |
|---|---|---|---|---|
| `PURPLE_HOST` | `0.0.0.0` | `str` | Bind host for the Purple agent HTTP server. | Purple |
| `PURPLE_PORT` | `9010` | `int` | Listen port for the Purple agent HTTP server. | Purple |
| `PURPLE_LOG_LEVEL` | `info` | `str` | Uvicorn log level (`debug`, `info`, `warning`, `error`, `critical`). | Purple |
| `PURPLE_AGENT_NAME` | `purple-agent` | `str` | Display name for the Purple agent. | Purple |
| `PURPLE_AGENT_DESCRIPTION` | `Simple A2A-compliant agent for E2E testing and validation` | `str` | Agent description published in the AgentCard. | Purple |
| `PURPLE_AGENT_VERSION` | `1.0.0` | `str` | Agent version string published in the AgentCard. | Purple |
| `PURPLE_STATIC_PEERS` | `[]` | `list[str]` (JSON) | JSON array of peer URLs for static peer discovery, e.g. `["http://host:9009"]`. | Purple |
| `PURPLE_GREEN_URL` | `http://localhost:9009` | `str` | URL Purple uses to report traces back to Green. | Purple |
| `PURPLE_CARD_URL` | _(auto)_ | `str \| None` | Override for the AgentCard URL. Auto-constructed as `http://{PURPLE_HOST}:{PURPLE_PORT}` if not set. | Purple |

---

## LLM Settings (LLMSettings)

Prefix: `AGENTBEATS_LLM_`
Source: `src/common/settings.py`

Used by the LLM judge (`src/green/evals/llm_judge.py`). If `AGENTBEATS_LLM_API_KEY` is unset, the judge falls back to rule-based scoring automatically.

| Env Var | Default | Type | Description | Agent |
|---|---|---|---|---|
| `AGENTBEATS_LLM_API_KEY` | `None` | `str \| None` | API key for the LLM service. Required to enable LLM-based evaluation. | Green |
| `AGENTBEATS_LLM_BASE_URL` | `https://api.openai.com/v1` | `str` | Base URL for any OpenAI-compatible API (OpenAI, Azure, local). | Green |
| `AGENTBEATS_LLM_MODEL` | `gpt-4o-mini` | `str` | Model identifier passed to the LLM API. | Green |
| `AGENTBEATS_LLM_TEMPERATURE` | `0.0` | `float` | Sampling temperature for LLM evaluation calls. | Green |

---

## A2A Client Settings (A2ASettings)

Prefix: `AGENTBEATS_A2A_`
Source: `src/common/settings.py`

Controls HTTP timeouts for all Agent-to-Agent (A2A) client connections.

| Env Var | Default | Type | Description | Agent |
|---|---|---|---|---|
| `AGENTBEATS_A2A_TIMEOUT` | `30.0` | `float` | Total request timeout in seconds for A2A calls. | Green, Purple |
| `AGENTBEATS_A2A_CONNECT_TIMEOUT` | `10.0` | `float` | TCP connect timeout in seconds for A2A calls. | Green, Purple |

---

## Usage Examples

### Minimal local run (two terminals)

**Terminal 1 — Purple agent:**

```bash
PURPLE_PORT=9010 python -m purple.server
```

**Terminal 2 — Green agent:**

```bash
GREEN_PORT=9009 \
PURPLE_AGENT_URL=http://localhost:9010 \
AGENTBEATS_LLM_API_KEY=sk-... \
python -m green.server
```

### Docker Compose override

```yaml
services:
  green:
    environment:
      GREEN_PORT: "9009"
      GREEN_OUTPUT_FILE: /data/results.json
      PURPLE_AGENT_URL: http://purple:9010
      AGENTBEATS_LLM_API_KEY: "${LLM_API_KEY}"
  purple:
    environment:
      PURPLE_PORT: "9010"
      PURPLE_GREEN_URL: http://green:9009
```

### Using a `.env` file

Copy the provided example and fill in your values:

```bash
cp .env.example .env
# edit .env as needed
```

Then source before running:

```bash
set -a && source .env && set +a
python -m green.server
```

### Enable LLM judge with a local model

```bash
AGENTBEATS_LLM_API_KEY=anything \
AGENTBEATS_LLM_BASE_URL=http://localhost:11434/v1 \
AGENTBEATS_LLM_MODEL=llama3.2 \
python -m green.server
```

---

## Troubleshooting

### Green cannot reach Purple (`ConnectionRefusedError`)

- Verify Purple is running and bound to `PURPLE_PORT`.
- Check that `PURPLE_AGENT_URL` matches the host and port Purple is listening on.
- In Docker, use service names (`http://purple:9010`), not `localhost`.

### LLM judge always returns rule-based scores

- `AGENTBEATS_LLM_API_KEY` is unset or empty. Set it to any non-empty value (even a placeholder for local models).
- Confirm `AGENTBEATS_LLM_BASE_URL` points to a reachable endpoint.

### Output file not written

- The directory referenced in `GREEN_OUTPUT_FILE` must exist before the agent starts.
- Default is `output/results.json` — create the `output/` directory if missing.

### Agents bind to wrong interface

- `GREEN_HOST` / `PURPLE_HOST` default to `0.0.0.0` (all interfaces). Set to `127.0.0.1` to restrict to loopback.
- `GREEN_CARD_URL` / `PURPLE_CARD_URL` are used for external discoverability; override them when binding to `0.0.0.0` but the public address is different.

### Port conflict

- Change `GREEN_PORT` or `PURPLE_PORT` to a free port and update the corresponding `PURPLE_AGENT_URL` / `PURPLE_GREEN_URL` on the other side.

### `GREEN_COORDINATION_ROUNDS` has no effect

- This setting is deprecated since STORY-031. The Green agent now terminates via A2A completion signals. Remove it from your configuration to avoid confusion.

### `AGENT_UUID` is different every restart

- By default a random UUID is generated each run. Set `AGENT_UUID` to a fixed value if you need stable agent identity across restarts (e.g. for leaderboard tracking).
