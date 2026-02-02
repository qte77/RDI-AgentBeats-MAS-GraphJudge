#!/usr/bin/env python3
"""
AgentBeats Competition Data Extraction Script
Extracts AI agent data from agentbeats.dev using Mino.ai web agent.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests

OUTPUT_FILE = Path("docs/AgentsBeats/CompetitionAnalysis-Mino.json")
BASE_URL = "https://mino.ai/v1/automation"

# URLs to analyze
URLS = ["https://agentbeats.dev/"]

# Polling configuration
POLL_INTERVAL = 5  # seconds
MAX_WAIT_TIME = 300  # 5 minutes


def submit_async_run(api_key: str, url: str, goal: str) -> str:
    """
    Submit an async automation run to Mino.ai.

    Args:
        api_key: Mino.ai API key
        url: Target URL to analyze
        goal: Natural language goal for the agent

    Returns:
        run_id for polling
    """
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "url": url,
        "goal": goal,
    }

    response = requests.post(
        f"{BASE_URL}/run-async",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("run_id")


def get_run_status(api_key: str, run_id: str) -> dict[str, Any]:
    """
    Get the status and result of an automation run.

    Args:
        api_key: Mino.ai API key
        run_id: Run identifier

    Returns:
        Run details including status and result
    """
    headers = {"X-API-Key": api_key}

    response = requests.get(
        f"{BASE_URL}/runs/{run_id}",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()


def wait_for_completion(api_key: str, run_id: str) -> dict[str, Any]:
    """
    Poll run status until completion or timeout.

    Args:
        api_key: Mino.ai API key
        run_id: Run identifier

    Returns:
        Final run result

    Raises:
        TimeoutError: If run doesn't complete within MAX_WAIT_TIME
    """
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_WAIT_TIME:
            raise TimeoutError(f"Run {run_id} did not complete within {MAX_WAIT_TIME}s")

        run_data = get_run_status(api_key, run_id)
        status = run_data.get("status", "").lower()

        print(f"  Status: {status} ({elapsed:.0f}s elapsed)", file=sys.stderr)

        if status in ("completed", "success"):
            return run_data
        elif status in ("failed", "error"):
            error_msg = run_data.get("error", "Unknown error")
            raise RuntimeError(f"Run {run_id} failed: {error_msg}")

        time.sleep(POLL_INTERVAL)


def process_url(api_key: str, url: str, goal: str) -> dict[str, Any]:
    """
    Process a single URL with Mino.ai agent.

    Args:
        api_key: Mino.ai API key
        url: Target URL
        goal: Analysis goal

    Returns:
        Extraction result
    """
    print(f"Submitting async run for {url}...", file=sys.stderr)
    run_id = submit_async_run(api_key, url, goal)
    print(f"  Run ID: {run_id}", file=sys.stderr)

    print("Waiting for completion...", file=sys.stderr)
    result = wait_for_completion(api_key, run_id)

    return result.get("result", {})


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

    # Process all URLs
    print(f"Processing {len(URLS)} URL(s) with Mino.ai...", file=sys.stderr)
    results = []

    for url in URLS:
        try:
            result = process_url(api_key, url, goal)
            results.append(result)
        except Exception as e:
            print(f"Error processing {url}: {e}", file=sys.stderr)
            sys.exit(1)

    # Combine results (for single URL, just use first result)
    final_result = results[0] if len(results) == 1 else {"results": results}

    # Save output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(final_result, indent=2, ensure_ascii=False) + "\n")

    # Print summary
    print(f"✓ Successfully extracted data from {len(URLS)} URL(s)", file=sys.stderr)
    print(f"✓ Output saved to {OUTPUT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
