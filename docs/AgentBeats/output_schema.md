# AgentBeats Output Schema

Output format specification for AgentBeats.dev leaderboard integration.

Adapted for multi-agent coordination evaluation per PRD STORY-008, STORY-014.

## Required Schema

```json
{
  "participants": {
    "agent": "<uuid>"
  },
  "results": [
    {
      "pass_rate": 85.0,
      "time_used": 350.0,
      "max_score": 100
    }
  ]
}
```

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `participants.agent` | string (UUID) | Yes | Agent UUID for tracking |
| `results[].pass_rate` | float (0-100) | Yes | Success rate percentage (overall_score * 100) |
| `results[].time_used` | float | Yes | Execution time in milliseconds (p99_latency) |
| `results[].max_score` | float | Yes | Maximum possible score |
| `results[].domain` | string | No | Task domain (default: "coordination") |
| `results[].score` | float | No | Actual score achieved |
| `results[].task_rewards` | object | No | Per-dimension rewards |
| `results[].detail` | GreenAgentOutput | No | Full coordination evaluation output |

## GreenAgentOutput Schema (detail)

Per PRD STORY-008, STORY-014:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `overall_score` | float (0-1) | Yes | Overall coordination score |
| `reasoning` | string | Yes | Explanation of the assessment |
| `coordination_quality` | "low" \| "medium" \| "high" | Yes | Qualitative assessment |
| `strengths` | string[] | No | Observed coordination strengths |
| `weaknesses` | string[] | No | Observed coordination weaknesses |
| `graph_metrics` | GraphMetrics | No | Tier 1 graph structural analysis |
| `latency_metrics` | LatencyMetrics | No | Tier 2 performance metrics |

## GraphMetrics Schema

Per PRD STORY-014:

| Field | Type | Description |
|-------|------|-------------|
| `graph_density` | float (0-1) | Graph density (>0.3 indicates healthy collaboration) |
| `degree_centrality` | dict[str, float] | Degree centrality per agent |
| `betweenness_centrality` | dict[str, float] | Betweenness centrality per agent |
| `closeness_centrality` | dict[str, float] | Closeness centrality per agent |
| `eigenvector_centrality` | dict[str, float] | Eigenvector centrality per agent |
| `pagerank` | dict[str, float] | PageRank scores per agent |
| `clustering_coefficient` | float | Average clustering coefficient |
| `connected_components` | int | Number of connected components |
| `average_path_length` | float | Average path length between agents |
| `diameter` | int | Graph diameter (longest shortest path) |
| `bottlenecks` | string[] | Agents with betweenness > 0.5 |
| `has_bottleneck` | bool | Whether bottleneck agents detected |
| `isolated_agents` | string[] | Agents with degree = 0 |
| `over_centralized` | bool | Single agent handles > 70% interactions |
| `coordination_quality` | string | Classification: high/medium/low/bottleneck |

## LatencyMetrics Schema

Per PRD STORY-010:

| Field | Type | Description |
|-------|------|-------------|
| `avg` | float | Average latency in milliseconds |
| `p50` | float | 50th percentile latency (median) |
| `p95` | float | 95th percentile latency |
| `p99` | float | 99th percentile latency |
| `slowest_agent` | string \| null | URL of slowest agent |
| `warning` | string | Comparability warning message |

> **Warning**: Latency values are only comparable within the same system/run.

## Complete Example

```json
{
  "participants": {
    "agent": "019b4d08-d84c-7a00-b2ec-4905ef7afc96"
  },
  "results": [
    {
      "domain": "coordination",
      "score": 85.0,
      "max_score": 100,
      "pass_rate": 85.0,
      "time_used": 350.0,
      "task_rewards": {
        "overall_score": 0.85,
        "graph_density": 0.45,
        "coordination_quality": 1.0
      },
      "detail": {
        "overall_score": 0.85,
        "reasoning": "Agents demonstrated efficient task delegation with clear communication patterns.",
        "coordination_quality": "high",
        "strengths": [
          "Fast response times",
          "Clear delegation",
          "No errors"
        ],
        "weaknesses": [
          "Could optimize parallel execution"
        ],
        "graph_metrics": {
          "graph_density": 0.45,
          "degree_centrality": {"agent-1": 0.6, "agent-2": 0.4},
          "betweenness_centrality": {"agent-1": 0.3, "agent-2": 0.2},
          "has_bottleneck": false,
          "bottlenecks": [],
          "isolated_agents": [],
          "over_centralized": false,
          "coordination_quality": "high"
        },
        "latency_metrics": {
          "avg": 150.5,
          "p50": 120.0,
          "p95": 280.0,
          "p99": 350.0,
          "slowest_agent": "http://agent-2:9009",
          "warning": "Latency values only comparable within same system/run"
        }
      }
    }
  ]
}
```

## Leaderboard SQL Query

```sql
SELECT id,
  ROUND(pass_rate,1) AS "Pass Rate",
  ROUND(time_used,1) AS "Time",
  total_tasks AS "# Tasks"
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY id ORDER BY pass_rate DESC, time_used ASC) AS rn
  FROM (
    SELECT
      results.participants.agent AS id,
      res.pass_rate AS pass_rate,
      res.time_used AS time_used,
      SUM(res.max_score) OVER (PARTITION BY results.participants.agent) AS total_tasks
    FROM results
    CROSS JOIN UNNEST(results.results) AS r(res)
  )
)
WHERE rn = 1
ORDER BY "Pass Rate" DESC;
```

## Usage

```python
from green.models import (
    AgentBeatsOutputModel,
    GreenAgentOutput,
    GraphMetrics,
    LatencyMetrics,
)

# Create GreenAgentOutput directly
green_output = GreenAgentOutput(
    overall_score=0.85,
    reasoning="Agents demonstrated efficient coordination.",
    coordination_quality="high",
    strengths=["Fast response times", "Clear delegation"],
    weaknesses=["Could optimize parallel execution"],
    graph_metrics=GraphMetrics(graph_density=0.45).model_dump(),
    latency_metrics=LatencyMetrics(avg=150.0, p50=120.0, p95=280.0, p99=350.0, slowest_agent=None).model_dump(),
)

# Create from GreenAgentOutput
output = AgentBeatsOutputModel.from_green_output(
    green_output=green_output,
    agent_id="019b4d08-d84c-7a00-b2ec-4905ef7afc96",
    time_used=350.0,
)

# Or create from executor evaluation results
output = AgentBeatsOutputModel.from_evaluation_results(
    evaluation_results={
        "tier1_graph": {...},
        "tier2_llm": {...},
        "tier2_latency": {...},
    },
    agent_id="019b4d08-d84c-7a00-b2ec-4905ef7afc96",
)

# Validate from dict
data = {...}
output = AgentBeatsOutputModel.model_validate(data)
green = GreenAgentOutput.model_validate(data["results"][0]["detail"])

# Export
json_str = output.to_json(indent=2)
```

## Validation

All models use Pydantic's `model_validate()` for automatic validation:

```python
# Validate from dict
output = AgentBeatsOutputModel.model_validate(data)
```

See tests in `tests/test_green_models.py` for validation examples.

## References

- [AgentBeats Debate Leaderboard](https://github.com/RDI-Foundation/agentbeats-debate-leaderboard)
- [Pydantic Models](../../src/green/models.py)
- [Sample Output](./sample_output.json)
