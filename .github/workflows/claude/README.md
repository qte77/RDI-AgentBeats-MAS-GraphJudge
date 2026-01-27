# AgentBeats Automated Analysis

Analyzes agents from agentbeats.dev using Claude API every other day.

## Setup

Add `ANTHROPIC_API_KEY` to repository secrets:

1. Settings → Secrets and variables → Actions
2. New repository secret: `ANTHROPIC_API_KEY`
3. Value: Your API key from <https://console.anthropic.com/>

## Manual Trigger

Actions tab → "AgentBeats Analysis" → Run workflow

## Output

Results: `docs/AgentsBeats/CompetitionAnalysis-Claude.json`

## Files

- `call_claude.py` - Python script
- `prompt.txt` - Analysis instructions
- `schema.json` - Output schema
