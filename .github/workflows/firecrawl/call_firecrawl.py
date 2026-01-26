#!/usr/bin/env python3
"""
AgentBeats Competition Data Extraction Script
Extracts AI agent data from agentbeats.dev using Firecrawl agent API.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

from firecrawl import FirecrawlApp
from pydantic import BaseModel

OUTPUT_FILE = Path("docs/AgentsBeats/CompetitionAnalysis-Firecrawl.json")

URLS = ["https://agentbeats.dev/"]


class ExtractSchema(BaseModel):
    """Schema loaded dynamically from JSON file."""

    agents: list[dict[str, Any]]


def main():
    """Main execution function."""
    # Load prompt
    script_dir = Path(__file__).parent
    prompt = (script_dir / "prompt.txt").read_text()

    # Check API key
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Call Firecrawl agent API
    print("Calling Firecrawl agent API...", file=sys.stderr)
    app = FirecrawlApp(api_key=api_key)

    result = app.agent(
        urls=URLS,
        prompt=prompt,
        schema=ExtractSchema,
        model="spark-1-pro",
    )

    # Extract data from result
    if isinstance(result, dict) and "data" in result:
        data = result["data"]
    else:
        data = result

    # Save output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    # Print summary
    agent_count = len(data.get("agents", [])) if isinstance(data, dict) else 0
    print(f"✓ Extracted {agent_count} agents", file=sys.stderr)


if __name__ == "__main__":
    main()
