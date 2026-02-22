# Mino.ai Integration for AgentBeats Analysis

This directory contains scripts for extracting AI agent data from agentbeats.dev using the [Mino.ai](https://mino.ai) web agent API.

## Files

- `call_mino.py` - **Recommended**: Asynchronous version with polling (scalable, handles multiple URLs)
- `call_mino_sync.py` - Synchronous version (simpler, blocks until completion)
- `prompt.txt` - Natural language goal/prompt for the Mino.ai agent

## API Modes Comparison

| Mode | Script | Best For | Pros | Cons |
|------|--------|----------|------|------|
| **Async** | `call_mino.py` | Production, multiple URLs | Scalable, better error recovery, concurrent processing | Requires polling logic |
| **Sync** | `call_mino_sync.py` | Single URL, quick tests | Simple, immediate results | Blocks during execution, timeout risk |
| **Streaming** | _(not implemented)_ | Real-time monitoring | Live progress updates | Complex for CI/CD, connection management |

## Answers to Key Questions

### 1. Can we send multiple URLs at a time?

**No single batch endpoint**, but two approaches work:

- **Sequential**: Loop through URLs one at a time (used in both scripts)
- **Concurrent**: Submit multiple async requests, poll all simultaneously (can be added to `call_mino.py`)

Current implementation processes URLs sequentially. For true parallelism, submit all URLs to `run-async` first, collect run_ids, then poll all concurrently.

### 2. Wait for response or query periodically?

**Recommended: Async with polling** (`call_mino.py`)

Reasons:
- Better for GitHub Actions (no long-running HTTP connections)
- Handles timeouts gracefully
- Can process multiple URLs efficiently
- Easier error recovery

The async script:
- Submits run → gets `run_id`
- Polls every 5 seconds via `/runs/{run_id}`
- Exits on completion/failure or after 5 minute timeout

### 3. Output Format

Both scripts follow the same pattern as existing workflows:
- Output to `docs/AgentsBeats/CompetitionAnalysis-Mino.json`
- Auto-commit if changes detected
- JSON format matching Firecrawl/Claude outputs

## Setup

### 1. Get API Key

Sign up at https://mino.ai/api-keys (free tier available)

### 2. Add GitHub Secret

Add `MINO_API_KEY` to repository secrets:

```bash
gh secret set MINO_API_KEY
```

### 3. Customize Prompt

Edit `prompt.txt` to change what data the agent extracts.

### 4. Configure URLs

Edit the `URLS` list in either script:

```python
URLS = [
    "https://agentbeats.dev/",
    "https://example.com/agents",  # Add more URLs
]
```

### 5. Adjust Timeouts (optional)

In `call_mino.py`:
```python
POLL_INTERVAL = 5      # seconds between status checks
MAX_WAIT_TIME = 300    # total timeout (5 minutes)
```

In `call_mino_sync.py`:
```python
REQUEST_TIMEOUT = 180  # request timeout (3 minutes)
```

## Testing Locally

```bash
# Set API key
export MINO_API_KEY="your-key-here"

# Run async version
python3 .github/workflows/mino/call_mino.py

# Or sync version
python3 .github/workflows/mino/call_mino_sync.py
```

## Switching Between Versions

To use the synchronous version in the workflow, edit `.github/workflows/agentbeats-analysis-mino.yaml`:

```yaml
- name: Run Mino extraction
  env:
    MINO_API_KEY: ${{ secrets.MINO_API_KEY }}
  run: |
    python .github/workflows/mino/call_mino_sync.py  # Change this line
```

## Error Handling

Both scripts handle:
- Missing API key → exit with error
- API failures → raise and exit
- Timeouts → configurable limits
- JSON parsing → structured error messages

## Future Enhancements

- **True parallelism**: Submit all URLs to async API, then poll all `run_id`s concurrently
- **Retry logic**: Exponential backoff for transient failures
- **Streaming mode**: Real-time progress updates (using SSE endpoint)
- **Result validation**: Schema validation against expected output format
- **Incremental updates**: Only extract new/changed agents

## References

- [Mino.ai Quick Start](https://docs.mino.ai/quick-start)
- [Mino.ai API Documentation](https://docs.mino.ai)
- [Example workflow](.github/workflows/agentbeats-analysis-mino.yaml)
