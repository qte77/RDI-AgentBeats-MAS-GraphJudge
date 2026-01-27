# AgentBeats Registration Guide

This guide walks you through registering your agents on the [AgentBeats platform](https://agentbeats.dev) and configuring `scenario.toml` for production deployment.

## Prerequisites

Before registering, ensure you have:

1. Docker images published to GHCR (GitHub Container Registry)
   - `ghcr.io/YOUR_USERNAME/green-agent:latest`
   - `ghcr.io/YOUR_USERNAME/purple-agent:latest`

2. Verified your agents work locally using `docker-compose.yml`

3. Read the [AgentBeats documentation](https://docs.agentbeats.dev/tutorial/)

## Registration Process

### Step 1: Sign Up for AgentBeats

1. Visit [AgentBeats Competition Signup](https://forms.gle/NHE8wYVgS6iJLwRj8)
2. Fill out the registration form with your team details
3. Join the [AgentBeats Discord](https://discord.gg/uqZUta3MYa) for support
4. Wait for platform access confirmation

### Step 2: Access the Platform

1. Navigate to [agentbeats.dev](https://agentbeats.dev)
2. Log in with your registered credentials
3. You'll see the platform dashboard

### Step 3: Register Your Green Agent (Benchmark)

Your **green agent** is the assessor/benchmark that evaluates other agents.

1. Click **"Register New Agent"** or **"Add Benchmark"** in the dashboard
2. Fill out the agent details:
   - **Name**: `green-agent-evaluator`
   - **Description**: `Narrative Evaluator - Assesses narratives for compliance`
   - **Docker Image**: `ghcr.io/YOUR_USERNAME/green-agent:latest`
   - **Platform**: `linux/amd64`
   - **Port**: `8000`
   - **Category**: `Legal Domain`

3. Click **"Submit"** or **"Register"**
4. The platform will validate your agent by:
   - Pulling the Docker image
   - Starting the container
   - Checking `/.well-known/agent-card.json` endpoint
   - Verifying A2A protocol compliance

5. **Copy your agentbeats_id**: After successful registration, you'll see an ID like:

   ```text
   agentbeats_id: "agent_xyz123abc456"
   ```

   **Important**: Save this ID - you'll need it for `scenario.toml`

### Step 4: Register Your Purple Agent (Baseline)

Your **purple agent** is the baseline participant that demonstrates your benchmark.

1. Repeat the registration process for the purple agent:
   - **Name**: `purple-agent-participant`
   - **Description**: `Narrative Generator - Creates sample narratives for testing`
   - **Docker Image**: `ghcr.io/YOUR_USERNAME/purple-agent:latest`
   - **Platform**: `linux/amd64`
   - **Port**: `8000`
   - **Category**: `Legal Domain` (participant)

2. **Copy the purple agent's agentbeats_id** for `scenario.toml`

### Step 5: Update scenario.toml

Now that your agents are registered, update `scenario.toml` with the production IDs:

```toml
[green_agent]
agentbeats_id = "agent_xyz123abc456"  # Replace with your green agent ID
env = { LOG_LEVEL = "INFO" }

[[participants]]
agentbeats_id = "agent_abc789def012"  # Replace with your purple agent ID
name = "participant"
env = {}

[config]
difficulty = "medium"
max_iterations = 5
target_risk_score = 20
evaluation_mode = "strict"
```

**Commit and push** your updated `scenario.toml`:

```bash
git add scenario.toml
git commit -m "chore: update scenario.toml with production agentbeats_ids"
git push
```

## Local vs Production Configuration

Understanding the difference between local testing and production deployment:

### Local Testing (docker-compose.yml)

For **local development**, use `ghcr_url` to reference your Docker images directly:

```yaml
services:
  green-agent:
    image: ghcr.io/YOUR_USERNAME/green-agent:latest
    ports:
      - "8001:8000"
```

**Purpose**: Fast iteration, debugging, integration testing

### Production Deployment (scenario.toml)

For **AgentBeats platform**, use `agentbeats_id` to reference registered agents:

```toml
[green_agent]
agentbeats_id = "agent_xyz123abc456"
```

**Purpose**: Official benchmarking, leaderboard submissions, competition evaluation

### Why the Difference?

| Aspect | `ghcr_url` (Local) | `agentbeats_id` (Production) |
|--------|-------------------|------------------------------|
| **Source** | Direct Docker image pull | Platform-managed agent |
| **Control** | You manage containers | Platform manages lifecycle |
| **Authentication** | Your GHCR credentials | Platform handles auth |
| **Versioning** | Tag-based (`:latest`, `:v1.0`) | Platform tracks versions |
| **Updates** | Manual image rebuild | Platform pulls latest on each run |
| **Monitoring** | Local logs | Platform dashboard + logs |

## Verification Steps

After registration and configuration, verify everything works:

### 1. Verify Agent Registration

Check the AgentBeats dashboard:

```text
✓ Green agent status: Active
✓ Purple agent status: Active
✓ Agent cards validated
✓ A2A protocol compliance confirmed
```

### 2. Test Agent Discovery

You can test agent card endpoints locally:

```bash
# Test green agent
curl http://localhost:8001/.well-known/agent-card.json

# Test purple agent
curl http://localhost:8002/.well-known/agent-card.json
```

Expected response:

```json
{
  "name": "green-agent-evaluator",
  "description": "Narrative Evaluator",
  "version": "0.1.0",
  "capabilities": ["task/send", "task/result"]
}
```

### 3. Run Platform Test

The AgentBeats platform may provide a **"Test Benchmark"** button:

1. Click **"Test Benchmark"** on your green agent
2. Platform will:
   - Start your green agent
   - Send a test task
   - Verify task execution
   - Check result format

3. Review test results in the dashboard

### 4. Validate scenario.toml

Ensure your `scenario.toml` is valid:

```bash
# Check TOML syntax
python -c "import tomllib; tomllib.load(open('scenario.toml', 'rb'))"
```

### 5. Check Docker Image Accessibility

Verify the platform can pull your images:

```bash
# Test public accessibility (images must be public)
docker pull ghcr.io/YOUR_USERNAME/green-agent:latest
docker pull ghcr.io/YOUR_USERNAME/purple-agent:latest
```

**Important**: GHCR packages must be **public** for the platform to access them.

To make packages public:

1. Go to `https://github.com/YOUR_USERNAME?tab=packages`
2. Click on `green-agent` or `purple-agent`
3. Click **"Package settings"**
4. Scroll to **"Danger Zone"**
5. Click **"Change visibility"** → **"Public"**

## Common Issues

### Issue: "Agent registration failed - image not found"

**Solution**:

- Verify image is pushed to GHCR: `https://github.com/YOUR_USERNAME?tab=packages`
- Ensure image is **public** (not private)
- Check image name matches exactly: `ghcr.io/YOUR_USERNAME/green-agent:latest`

### Issue: "Agent card validation failed"

**Solution**:

- Test agent card endpoint locally: `curl http://localhost:8001/.well-known/agent-card.json`
- Verify agent starts correctly: `docker-compose up`
- Check container logs for startup errors

### Issue: "Platform can't reach my agent"

**Solution**:

- Ensure agent listens on `0.0.0.0:8000` (not `localhost:8000`)
- Verify `EXPOSE 8000` in Dockerfile
- Check agent runs correctly: `docker run -p 8001:8000 ghcr.io/YOUR_USERNAME/green-agent:latest`

### Issue: "agentbeats_id not showing after registration"

**Solution**:

- Refresh the dashboard page
- Check email for confirmation
- Contact support on Discord
- Review agent validation logs on platform

## Next Steps

After successful registration:

1. **Test Your Benchmark**: Use the platform's test runner to validate
2. **Submit for Phase 1**: Complete the [submission form](https://forms.gle/1C5d8KXny2JBpZhz7)
3. **Monitor Leaderboard**: Track your benchmark's performance
4. **Iterate**: Update agents based on feedback and testing

## Resources

- **Platform**: [agentbeats.dev](https://agentbeats.dev)
- **Documentation**: [docs.agentbeats.dev](https://docs.agentbeats.dev/tutorial/)
- **Discord Support**: [discord.gg/uqZUta3MYa](https://discord.gg/uqZUta3MYa)
- **Phase 1 Submission**: [forms.gle/1C5d8KXny2JBpZhz7](https://forms.gle/1C5d8KXny2JBpZhz7)
- **A2A Protocol**: [a2a-protocol.org](https://a2a-protocol.org/latest/)
- **Project README**: [../README.md](../README.md)
- **GHCR Deployment Guide**: [../README.md#ghcr-deployment](../README.md#ghcr-deployment)

## Evaluator Extensibility

The Green Agent evaluation system is designed with extensibility in mind. You can add custom evaluators to extend the multi-tier assessment pipeline.

### Evaluator Interface Pattern

All evaluators follow a consistent interface pattern:

```python
async def evaluate(
    self,
    traces: list[InteractionStep],
    **context: Any
) -> dict[str, Any]:
    """Evaluate coordination quality from interaction traces.

    Args:
        traces: List of InteractionStep traces to analyze
        **context: Optional context from other evaluators

    Returns:
        Evaluation results as dictionary
    """
    pass
```

Key principles:
- **Asynchronous**: All evaluators use `async def` for non-blocking execution
- **Trace-based**: Primary input is `list[InteractionStep]` from A2A Traceability Extension
- **Contextual**: Evaluators can receive results from previous tiers via `**context`
- **Structured output**: Return `dict[str, Any]` for JSON serialization

### Tier-Based Architecture

The evaluation system is organized into three tiers:

#### Tier 1: Structural Analysis (Graph)

**Purpose**: Analyze coordination structure using graph theory

**Evaluators**:
- `GraphEvaluator` (src/green/evals/graph.py): Builds directed graphs from interaction traces and computes centrality, clustering, and path metrics

**Integration**: Executed first, results passed to Tier 2 evaluators

**Output**: Graph metrics (centrality, density, bottlenecks, isolated agents)

#### Tier 2: Semantic + Performance Analysis (LLM Judge + Latency)

**Purpose**: Deep semantic assessment and performance metrics

**Evaluators**:
- `LLMJudge` (src/green/evals/llm_judge.py): Uses LLM to assess coordination quality with reasoning
- `LatencyEvaluator` (src/green/evals/system.py): Computes latency percentiles and identifies bottlenecks

**Integration**: Receives Tier 1 graph results as context for enriched analysis

**Output**: Semantic judgments with reasoning, latency percentiles

#### Tier 3: Custom Plugins (Text/Domain-Specific)

**Purpose**: Domain-specific or experimental evaluators

**Examples**:
- `TextEvaluator`: Text similarity analysis for message content
- Custom business logic evaluators
- Domain-specific compliance checkers

**Integration**: Can receive all previous tier results as context

**Output**: Domain-specific metrics

### Adding a Custom Evaluator

Here's a complete example of adding a Tier 3 text similarity evaluator:

#### Step 1: Create Evaluator Module

Create `src/green/evals/text.py`:

```python
"""Text similarity evaluator for message content analysis."""

from __future__ import annotations

from pydantic import BaseModel

from green.models import InteractionStep


class TextMetrics(BaseModel):
    """Text similarity metrics.

    Attributes:
        avg_message_length: Average message length in characters
        unique_messages: Number of unique messages
        similarity_score: Text similarity score (0-1)
    """

    avg_message_length: float
    unique_messages: int
    similarity_score: float


async def evaluate_text(steps: list[InteractionStep]) -> TextMetrics:
    """Evaluate text similarity from interaction traces.

    Args:
        steps: List of InteractionStep traces to analyze

    Returns:
        TextMetrics with similarity analysis
    """
    if not steps:
        return TextMetrics(
            avg_message_length=0,
            unique_messages=0,
            similarity_score=0.0,
        )

    # Example implementation (simplified)
    # In real implementation, extract message content from traces
    messages = [f"Message {i}" for i, _ in enumerate(steps)]

    avg_length = sum(len(msg) for msg in messages) / len(messages)
    unique_count = len(set(messages))
    similarity = unique_count / len(messages)  # Simple uniqueness ratio

    return TextMetrics(
        avg_message_length=avg_length,
        unique_messages=unique_count,
        similarity_score=similarity,
    )
```

#### Step 2: Add Tests

Create `tests/test_text.py`:

```python
"""Tests for text similarity evaluator."""

import pytest

from green.evals.text import TextMetrics, evaluate_text
from green.models import CallType, InteractionStep
from datetime import datetime


@pytest.mark.asyncio
async def test_evaluate_text_empty():
    """Test text evaluation with empty traces."""
    result = await evaluate_text([])

    assert result.avg_message_length == 0
    assert result.unique_messages == 0
    assert result.similarity_score == 0.0


@pytest.mark.asyncio
async def test_evaluate_text_with_steps():
    """Test text evaluation with interaction steps."""
    steps = [
        InteractionStep(
            step_id="1",
            trace_id="trace1",
            call_type=CallType.AGENT,
            start_time=datetime.now(),
            end_time=datetime.now(),
        )
    ]

    result = await evaluate_text(steps)

    assert isinstance(result, TextMetrics)
    assert result.avg_message_length > 0
```

#### Step 3: Integrate with Executor Pipeline

Update `src/green/executor.py` to include the new evaluator:

```python
from green.evals.text import evaluate_text

class Executor:
    # ... existing code ...

    async def _evaluate_text(
        self, traces: list[InteractionStep], text_evaluator: Any
    ) -> dict[str, Any] | None:
        """Execute Tier 3 text evaluation.

        Args:
            traces: List of interaction steps
            text_evaluator: Text evaluator instance

        Returns:
            Text evaluation results or None if evaluator is None
        """
        if text_evaluator is None:
            return None

        try:
            return await text_evaluator.evaluate(traces)
        except Exception as e:
            return {"error": str(e)}

    async def evaluate_all(
        self,
        traces: list[InteractionStep],
        graph_evaluator: Any,
        llm_judge: Any,
        latency_evaluator: Any,
        text_evaluator: Any = None,  # Add new parameter
    ) -> dict[str, Any]:
        """Orchestrate evaluation across all tiers."""
        # Tier 1: Graph
        tier1_graph = await self._evaluate_graph(traces, graph_evaluator)

        # Tier 2: LLM + Latency
        tier2_llm = await self._evaluate_llm(traces, llm_judge, tier1_graph)
        tier2_latency = await self._evaluate_latency_tier2(traces, latency_evaluator)

        # Tier 3: Custom (Text)
        tier3_text = await self._evaluate_text(traces, text_evaluator)

        return {
            "tier1_graph": tier1_graph,
            "tier2_llm": tier2_llm,
            "tier2_latency": tier2_latency,
            "tier3_text": tier3_text,  # Add to output
        }
```

### Integration Points

The Executor pipeline (`src/green/executor.py:148`) provides integration points for custom evaluators:

1. **Tier 1 Integration** (`_evaluate_graph`): First-tier structural analysis
2. **Tier 2 Integration** (`_evaluate_llm`, `_evaluate_latency_tier2`): Semantic + performance analysis with Tier 1 context
3. **Tier 3 Integration** (custom methods): Domain-specific plugins with full context

The `evaluate_all` method orchestrates all tiers:
- Executes Tier 1 first
- Passes Tier 1 results to Tier 2 evaluators as context
- Optionally executes Tier 3 plugins with all previous results
- Aggregates all results into structured response

### Best Practices

1. **Follow the Interface**: Use `async def evaluate(traces, **context)` signature
2. **Handle Empty Input**: Always check for empty traces list
3. **Use Pydantic Models**: Define structured output with Pydantic for validation
4. **Add Tests First**: Write failing tests before implementation (TDD)
5. **Document Metrics**: Clearly document what each metric measures
6. **Error Handling**: Wrap evaluator calls in try/except at integration points
7. **Context Awareness**: Use results from previous tiers when relevant

### Example Use Cases

Custom evaluators can address domain-specific needs:

- **Compliance**: Check if interactions follow regulatory requirements
- **Security**: Analyze message content for sensitive data exposure
- **Cost**: Track token usage or API call costs
- **Business Logic**: Validate domain-specific coordination patterns
- **Performance**: Add custom performance metrics beyond latency

## Support

If you encounter issues:

1. Check this guide's [Common Issues](#common-issues) section
2. Review [AgentBeats Tutorial](https://docs.agentbeats.dev/tutorial/)
3. Ask on [Discord](https://discord.gg/uqZUta3MYa) in #support or #legal-domain
4. Check GitHub Issues in reference repositories ([green-agent-template](https://github.com/RDI-Foundation/green-agent-template), [leaderboard-template](https://github.com/RDI-Foundation/agentbeats-leaderboard-template))
