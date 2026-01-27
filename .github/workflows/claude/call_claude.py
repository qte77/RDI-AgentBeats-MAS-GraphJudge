#!/usr/bin/env python3
"""
AgentBeats Competition Analysis Script
Analyzes agents from agentbeats.dev using Claude API.
"""

import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic

OUTPUT_FILE = Path("docs/AgentsBeats/CompetitionAnalysis-Claude.json")


def main():
    """Main execution function."""
    # Load prompt and schema
    script_dir = Path(__file__).parent
    prompt = (script_dir / "prompt.txt").read_text()
    schema = json.loads((script_dir / "schema.json").read_text())

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Construct full prompt with schema
    full_prompt = f"""{prompt}

# JSON Schema
Your output MUST conform to this exact schema:

```json
{json.dumps(schema, indent=2)}
```

Analyze all agents listed on https://agentbeats.dev/ across all categories
and produce comprehensive JSON output following the schema above.
"""

    # Call Claude API
    print("Calling Claude API...", file=sys.stderr)
    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=16000,
        temperature=0.0,
        messages=[{"role": "user", "content": full_prompt}],
    )

    # Parse response
    response_text = message.content[0].text

    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        json_str = response_text[json_start:json_end].strip()
    else:
        json_str = response_text.strip()

    try:
        result = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    # Save output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    # Print summary
    agent_count = len(result.get("agents", []))
    print(f"✓ Analyzed {agent_count} agents", file=sys.stderr)


if __name__ == "__main__":
    main()
