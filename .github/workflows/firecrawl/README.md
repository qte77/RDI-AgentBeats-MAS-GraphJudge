# Firecrawl Agent Extraction

Extracts AI agent data from agentbeats.dev using Firecrawl's agent API.

## Setup

Add `FIRECRAWL_API_KEY` to repository secrets:

1. Settings → Secrets and variables → Actions
2. New repository secret: `FIRECRAWL_API_KEY`
3. Value: Your API key from <https://firecrawl.dev/>

## Schedule

Runs weekly on Sundays at midnight UTC.

## Manual Trigger

Actions tab → "AgentBeats Analysis Firecrawl" → Run workflow

## Output

Results: `docs/AgentsBeats/CompetitionAnalysis-Firecrawl.json`

## Files

- `call_firecrawl.py` - Python script using Firecrawl SDK
- `prompt.txt` - Extraction instructions for Firecrawl agent
- `schema.json` - Output schema (reference only)

## How It Works

1. Python SDK calls Firecrawl agent API with prompt, schema, URLs, and model (`spark-1-pro`)
2. SDK handles polling internally until job completes
3. Saves extracted data and commits to repo
