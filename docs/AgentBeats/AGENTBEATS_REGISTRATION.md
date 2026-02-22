# Evaluator Plugin Architecture

This guide explains how to extend the AgentBeats evaluation pipeline with custom evaluators.

## Tier System Overview

The evaluation pipeline is organized into three tiers:

| Tier | Name | Evaluator | File |
|------|------|-----------|------|
| **Tier 1** | Graph / Structural | `GraphEvaluator` | `src/green/evals/graph.py` |
| **Tier 2** | LLM + Latency | `_LLMJudgeEvaluator`, `_LatencyEvaluator` | `src/green/server.py` |
| **Tier 3** | Custom plugins | `BaseEvaluator` subclasses | `src/green/evals/` |

All tiers are orchestrated by `Executor.evaluate_all()` in `src/green/executor.py`.

---

## BaseEvaluator ABC — Tier 3 Interface

New Tier 3 evaluators must implement the `BaseEvaluator` abstract base class:

```python
# src/green/evals/base.py
from abc import ABC, abstractmethod
from typing import Any

from green.models import InteractionStep


class BaseEvaluator(ABC):
    """Interface for custom Tier 3 evaluators."""

    @abstractmethod
    async def evaluate(
        self,
        traces: list[InteractionStep],
        **context: Any,
    ) -> dict[str, Any]:
        """Evaluate agent traces and return a results dict.

        Args:
            traces: Collected interaction steps from a task run.
            **context: Optional context (e.g., graph_results from Tier 1).

        Returns:
            Dict of evaluation results keyed by metric name.
        """

    @property
    def tier(self) -> int:
        return 3
```

---

## GraphMetricPlugin ABC — Extension Point Within Tier 1

`GraphMetricPlugin` is a second-level extension point **inside** `GraphEvaluator` (Tier 1). It computes a single metric on a NetworkX directed graph.

```python
# src/green/evals/graph.py:17-23
from abc import ABC, abstractmethod
from typing import Any

import networkx as nx


class GraphMetricPlugin(ABC):
    """Base interface for graph metric plugins."""

    @abstractmethod
    def compute(self, graph: nx.DiGraph[str]) -> Any:
        """Compute metric from graph."""
```

Built-in plugins (registered by `GraphEvaluator.__init__`) include:
`DegreeCentralityPlugin`, `BetweennessCentralityPlugin`, `ClosenessCentralityPlugin`,
`EigenvectorCentralityPlugin`, `PageRankPlugin`, `GraphDensityPlugin`,
`ClusteringCoefficientPlugin`, `ConnectedComponentsPlugin`.

Custom plugins are registered at runtime via `GraphEvaluator.register_plugin()`:

```python
# src/green/evals/graph.py:116-123
def register_plugin(self, name: str, plugin: GraphMetricPlugin) -> None:
    """Register a custom metric plugin.

    Args:
        name: Plugin name (used as key in metrics output)
        plugin: GraphMetricPlugin instance
    """
    self._plugins[name] = plugin
```

Results for custom plugins appear in `GraphMetrics` output under the registered name
because `GraphMetrics` uses `model_config = {"extra": "allow"}`.

---

## Step-by-Step: Adding a Custom Tier 3 Evaluator

### Step 1 — Create the evaluator file

Create `src/green/evals/text_evaluator.py` implementing `BaseEvaluator`:

```python
# src/green/evals/text_evaluator.py
from typing import Any

from green.models import InteractionStep

from .base import BaseEvaluator


class TextEvaluator(BaseEvaluator):
    """Tier 3 custom evaluator: analyses text content of agent traces."""

    async def evaluate(
        self,
        traces: list[InteractionStep],
        **context: Any,
    ) -> dict[str, Any]:
        total_steps = len(traces)
        return {
            "text_total_steps": total_steps,
        }
```

### Step 2 — Implement `evaluate()`

`evaluate()` receives the list of `InteractionStep` traces collected during a task run.
Return a plain `dict[str, Any]`; all keys will be included in the final output.

### Step 3 — Register in `Executor.evaluate_all()`

Wire the new evaluator into `src/green/executor.py` alongside the existing tiers:

```python
# src/green/executor.py:279 (Executor.evaluate_all)
async def evaluate_all(
    self,
    traces: list[InteractionStep],
    graph_evaluator: Any,    # Tier 1
    llm_judge: Any,          # Tier 2
    latency_evaluator: Any,  # Tier 2
    text_evaluator: Any = None,  # Tier 3 (custom)
) -> dict[str, Any]:
    tier1_graph_result = await self._evaluate_graph(traces, graph_evaluator)
    # ... existing Tier 1 / Tier 2 logic ...

    tier3_text = None
    if text_evaluator is not None:
        tier3_text = await text_evaluator.evaluate(traces)

    return {
        "tier1_graph": tier1_graph,
        "tier2_llm": tier2_llm,
        "tier2_latency": tier2_latency,
        "tier3_text": tier3_text,  # new
    }
```

### Step 4 — Pass the evaluator from `server.py`

In `src/green/server.py`, instantiate and pass the new evaluator to `evaluate_all()`:

```python
from green.evals.text_evaluator import TextEvaluator

evaluation_results = await executor.evaluate_all(
    traces=traces,
    graph_evaluator=GraphEvaluator(),
    llm_judge=_LLMJudgeEvaluator(),
    latency_evaluator=_LatencyEvaluator(),
    text_evaluator=TextEvaluator(),   # new
)
```

---

## Reference Implementation: TextEvaluator (Tier 3)

`TextEvaluator` is the canonical Tier 3 example. It demonstrates the minimal surface
required to add a custom evaluator without modifying any existing Tier 1 or Tier 2 code:

```python
# src/green/evals/text_evaluator.py
from abc import ABC, abstractmethod
from typing import Any

from green.models import InteractionStep


class BaseEvaluator(ABC):
    @abstractmethod
    async def evaluate(
        self,
        traces: list[InteractionStep],
        **context: Any,
    ) -> dict[str, Any]: ...

    @property
    def tier(self) -> int:
        return 3


class TextEvaluator(BaseEvaluator):
    """Counts interaction steps; extend with richer text analysis."""

    async def evaluate(
        self,
        traces: list[InteractionStep],
        **context: Any,
    ) -> dict[str, Any]:
        return {"text_total_steps": len(traces)}
```

---

## Integration Points

| Extension Point | File | Lines |
|----------------|------|-------|
| `GraphMetricPlugin` ABC | `src/green/evals/graph.py` | 17–23 |
| `GraphEvaluator.register_plugin()` | `src/green/evals/graph.py` | 116–123 |
| Built-in plugin registration | `src/green/evals/graph.py` | 107–114 |
| `Executor.evaluate_all()` | `src/green/executor.py` | 279–333 |
| `_LLMJudgeEvaluator` (Tier 2 pattern) | `src/green/server.py` | 107–116 |
| `_LatencyEvaluator` (Tier 2 pattern) | `src/green/server.py` | 119–126 |
| Evaluator wiring in server | `src/green/server.py` | 152–157 |

---

## Adding a Custom GraphMetricPlugin (Tier 1 Extension)

To add a metric to the existing graph evaluation without touching any other code:

```python
# src/green/evals/graph.py — add a new plugin class
import networkx as nx
from typing import Any

from green.evals.graph import GraphMetricPlugin, GraphEvaluator


class TriangleCountPlugin(GraphMetricPlugin):
    """Counts triangles in the interaction graph."""

    def compute(self, graph: nx.DiGraph[str]) -> int:
        undirected = graph.to_undirected()
        triangles: dict[str, int] = nx.triangles(undirected)
        return sum(triangles.values()) // 3


# Register at startup (e.g. in server.py or a factory):
evaluator = GraphEvaluator()
evaluator.register_plugin("triangle_count", TriangleCountPlugin())
```

The result appears in `GraphMetrics` output as `triangle_count` because the model
uses `model_config = {"extra": "allow"}`.
