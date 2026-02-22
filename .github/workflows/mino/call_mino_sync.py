#!/usr/bin/env python3
"""
AgentBeats Competition Data Extraction Script (Synchronous version)
Extracts AI agent data from agentbeats.dev using Mino.ai web agent.

This is a simpler synchronous version that waits for completion.
Good for single URLs or when you don't need concurrent processing.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

OUTPUT_FILE = Path("docs/AgentsBeats/CompetitionAnalysis-Mino.json")
BASE_URL = "https://mino.ai/v1/automation"

# URLs to analyze
URLS = ["https://agentbeats.dev/"]

# Request timeout (Mino.ai recommends longer timeouts for sync requests)
REQUEST_TIMEOUT = 180  # 3 minutes


def run_sync_automation(api_key: str, url: str, goal: str) -> dict[str, Any]:
    """
    Execute synchronous automation and wait for completion.

    Args:
        api_key: Mino.ai API key
        url: Target URL to analyze
        goal: Natural language goal for the agent

    Returns:
        Automation result
    """
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "url": url,
        "goal": goal,
    }

    print(f"Running synchronous automation for {url}...", file=sys.stderr)
    print(f"  (This may take up to {REQUEST_TIMEOUT}s)", file=sys.stderr)

    response = requests.post(
        f"{BASE_URL}/run-sync",
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    return response.json()


def main():
    """Main execution function."""
    # Load prompt
    script_dir = Path(__file__).parent
    prompt_file = script_dir / "prompt.txt"

    if not prompt_file.exists():
        print(f"Error: {prompt_file} not found", file=sys.stderr)
        sys.exit(1)

    goal = prompt_file.read_text().strip()

    # Check API key
    api_key = os.environ.get("MINO_API_KEY")
    if not api_key:
        print("Error: MINO_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Process all URLs sequentially
    print(f"Processing {len(URLS)} URL(s) with Mino.ai (sync)...", file=sys.stderr)
    results = []

    for url in URLS:
        try:
            result = run_sync_automation(api_key, url, goal)
            results.append(result.get("result", {}))
            print(f"✓ Completed {url}", file=sys.stderr)
        except requests.exceptions.Timeout:
            print(f"Error: Request timed out after {REQUEST_TIMEOUT}s for {url}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error processing {url}: {e}", file=sys.stderr)
            sys.exit(1)

    # Combine results
    final_result = results[0] if len(results) == 1 else {"results": results}

    # Save output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(final_result, indent=2, ensure_ascii=False) + "\n")

    # Print summary
    print(f"✓ Successfully extracted data from {len(URLS)} URL(s)", file=sys.stderr)
    print(f"✓ Output saved to {OUTPUT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
