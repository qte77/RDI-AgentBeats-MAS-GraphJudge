---
title: Multi-Agent Tracing Architecture
version: 1.0
status: design
applies-to: Feature 7 (STORY-018 to STORY-025)
purpose: Common module, hybrid tracing, plugin system design
---

## TL;DR

Purple agents communicate P2P while Green collects traces asynchronously.

```text
┌─────────────────────────────────────────────────────────────────┐
│                         GREEN AGENT                             │
│  ┌──────────────┐    ┌───────────────┐    ┌─────────────────┐  │
│  │ POST /traces │───▶│ TraceStore    │───▶│ Evaluators      │  │
│  │ POST /register│   │ (in-memory)   │    │ (Tier 1/2/3)    │  │
│  │ GET /peers   │    └───────────────┘    └─────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
        ▲ async traces              ▲ registry
        │                           │
┌───────┴───────┐           ┌───────┴───────┐
│   Purple-1    │◀─────────▶│   Purple-2    │  Direct A2A (P2P)
└───────────────┘           └───────────────┘
```

## Key Components

| Component | Location | Purpose |
| ----------- | ---------- | --------- |
| **Common Models** | `src/common/models.py` | CallType, InteractionStep, JSONRPC types |
| **LLMSettings** | `src/common/settings.py` | Shared LLM configuration |
| **Messenger** | `src/common/messenger.py` | A2A client (eliminates duplication) |
| **TraceReporter** | `src/common/trace_reporter.py` | Fire-and-forget trace reporting |
| **PeerDiscovery** | `src/common/peer_discovery.py` | Static + Green registry lookup |
| **TraceStore** | `src/green/trace_store.py` | In-memory trace storage |

## Green Endpoints

| Endpoint | Method | Purpose |
| ---------- | -------- | --------- |
| `/traces` | POST | Receive async trace reports |
| `/register` | POST | Register agent in registry |
| `/peers` | GET | List registered agent URLs |

## InteractionStep Model

```python
class InteractionStep(BaseModel):
    step_id: str           # Unique step identifier
    trace_id: str          # Parent trace identifier
    call_type: CallType    # AGENT, TOOL, or HOST
    start_time: datetime
    end_time: datetime
    latency: int | None    # Milliseconds
    error: str | None
    parent_step_id: str | None
```

## Evaluator Tiers

| Tier | Evaluator | Purpose |
| ------ | ----------- | --------- |
| 1 | GraphEvaluator | Structural analysis (centrality, density) |
| 2 | LLMJudge | Semantic assessment with reasoning |
| 2 | LatencyEvaluator | Performance percentiles (p50/p95/p99) |
| 3 | TextEvaluator | Custom text analysis (optional) |

---

## Common Module

### Package Structure

```text
src/common/
├── __init__.py          # Package exports
├── models.py            # CallType, InteractionStep, JSONRPC
├── settings.py          # LLMSettings
├── messenger.py         # A2A Messenger
├── llm_client.py        # create_llm_client() factory
├── trace_reporter.py    # Async trace reporting
└── peer_discovery.py    # Static + registry discovery
```

### Backward Compatibility

Green and Purple re-export from common:

```python
# src/green/models.py
from common.models import CallType, InteractionStep  # Re-export
```

### LLMSettings

```python
class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENTBEATS_LLM_")

    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    enabled: bool = True
```

---

## Trace Collection

### TraceReporter (Fire-and-Forget)

```python
class TraceReporter:
    def __init__(self, green_agent_url: str | None = None):
        self._green_url = green_agent_url
        self._client = httpx.AsyncClient(timeout=5.0)

    async def report_trace(self, trace: InteractionStep) -> None:
        if not self._green_url:
            return
        try:
            await self._client.post(
                f"{self._green_url}/traces",
                json=trace.model_dump(mode="json"),
            )
        except Exception:
            pass  # Fire-and-forget
```

### PeerDiscovery

```python
class PeerDiscovery:
    def __init__(
        self,
        static_peers: list[str] | None = None,
        green_agent_url: str | None = None,
        cache_ttl: int = 60,
    ):
        self._static_peers = static_peers or []
        self._green_url = green_agent_url

    async def get_peers(self) -> list[str]:
        peers = set(self._static_peers)
        if self._green_url:
            dynamic = await self._fetch_from_green()
            peers.update(dynamic)
        return list(peers)
```

---

## Plugin System

### Evaluator Interface

```python
class BaseEvaluator(ABC):
    @abstractmethod
    async def evaluate(
        self,
        traces: list[InteractionStep],
        **context: Any,
    ) -> dict[str, Any]:
        pass

    @property
    def tier(self) -> int:
        return 3  # Default to custom tier
```

### Pipeline Execution

```python
async def evaluate_all(self, traces: list[InteractionStep]) -> dict:
    results = {}
    context = {}

    # Tier 1: Structural
    for plugin in self._plugins[1]:
        result = await plugin.evaluate(traces, **context)
        results[plugin.name] = result
        context[plugin.name.lower()] = result

    # Tier 2: Semantic + Performance (receives Tier 1 context)
    for plugin in self._plugins[2]:
        result = await plugin.evaluate(traces, **context)
        results[plugin.name] = result

    # Tier 3: Custom (receives all context)
    for plugin in self._plugins[3]:
        result = await plugin.evaluate(traces, **context)
        results[plugin.name] = result

    return results
```

### Settings-Based Loading

```python
class PluginSettings(BaseSettings):
    graph_enabled: bool = True
    llm_judge_enabled: bool = True
    latency_enabled: bool = True
    text_enabled: bool = False  # Tier 3 disabled by default
```

---

## Purple Agent Enhancement

### Settings

```python
class PurpleSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PURPLE_")

    host: str = "0.0.0.0"
    port: int = 9010

    # LLM (disabled by default)
    llm: LLMSettings = Field(
        default_factory=lambda: LLMSettings(enabled=False)
    )

    # Tracing
    green_agent_url: str | None = None
    static_peers: list[str] = Field(default_factory=list)
```

### Executor with LLM + Tracing

```python
class Executor:
    def __init__(self, settings: PurpleSettings):
        self._trace_reporter = TraceReporter(settings.green_agent_url)
        self._peer_discovery = PeerDiscovery(
            settings.static_peers, settings.green_agent_url
        )
        self._llm_client = (
            create_llm_client(settings.llm)
            if settings.llm.enabled else None
        )

    async def execute_task(self, task: str, context_id: str) -> str:
        start = datetime.now(UTC)

        result = (
            await self._process_with_llm(task)
            if self._llm_client
            else f"Processed: {task}"
        )

        trace = InteractionStep(
            step_id=str(uuid.uuid4()),
            trace_id=context_id,
            call_type=CallType.AGENT,
            start_time=start,
            end_time=datetime.now(UTC),
        )
        await self._trace_reporter.report_trace(trace)

        return result
```

---

## Verification

```bash
# Start Green
GREEN_PORT=9009 python -m green.server

# Start Purple with tracing
GREEN_AGENT_URL=http://localhost:9009 python -m purple.server

# Check traces
curl http://localhost:9009/traces

# Check peers
curl http://localhost:9009/peers
```

---

## References

- [A2A Protocol](https://a2a-protocol.org/latest/)
- [A2A Traceability Extension](https://a2a-protocol.org/latest/extensions/traceability/)
- [Feature 7 Stories](../GreenAgent-PRD.md) (STORY-018 to STORY-025)
