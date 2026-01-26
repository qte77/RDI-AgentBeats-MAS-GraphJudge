# A2A Extension Integration Guide

**Purpose**: Comprehensive implementation guide for A2A Traceability and Timestamp extensions in graph coordination benchmark

**Specifications**:
- [A2A Traceability Extension Specification](https://a2aprotocol.ai/docs/guide/traceability-extension-analysis)
- [A2A Timestamp Extension Specification](https://a2aprotocol.ai/docs/guide/a2a-timestamp-extension-analysis)

**Extension URIs**:
- Traceability: `https://github.com/a2aproject/a2a-samples/extensions/traceability/v1`
- Timestamp: `https://github.com/a2aproject/a2a-samples/extensions/timestamp/v1`

---

## Table of Contents

1. [Overview](#overview)
2. [Core Problems Solved](#core-problems-solved)
3. [Design Principles](#design-principles)
4. [Data Model](#data-model)
5. [Five Integration Patterns](#five-integration-patterns)
6. [Extension Activation](#extension-activation)
7. [Implementation Examples](#implementation-examples)
8. [Best Practices](#best-practices)
9. [Performance Monitoring](#performance-monitoring)
10. [Integration with External Systems](#integration-with-external-systems)
11. [Real-World Application Scenarios](#real-world-application-scenarios)

---

## Overview

### What Are A2A Extensions?

Extensions are a means of extending the Agent2Agent (A2A) protocol with new data, requirements, methods, and state machines.

**Key Characteristics**:
- **Optional**: Agents declare support in their AgentCard
- **Client Opt-In**: Clients activate extensions via request headers
- **URI-Identified**: Each extension has a unique URI
- **Specification-Defined**: Anyone can define, publish, and implement extensions

### Extension Mechanism

```
1. Agent declares support → AgentCard.extensions = [URI1, URI2]
2. Client discovers support → Reads agent's AgentCard
3. Client opts-in → Sends X-A2A-Extensions: URI header
4. Extension behavior activates → Protocol extended for that request
```

---

## Core Problems Solved

### 1. Observability in Multi-Agent Systems

**Problem**: Multi-agent systems involve complex, distributed interactions across multiple agents. Without tracing, debugging failures or understanding coordination patterns is nearly impossible.

**Solution**: Traceability Extension captures the full call chain:
- Agent A → Agent B → Agent C relationship tracking
- Parent-child step hierarchies via `parent_step_id`
- Complete interaction history for forensic analysis

**Application to Our Benchmark**: Graph coordination analysis requires visibility into agent-to-agent communication patterns. Traceability enables building coordination graphs from actual runtime traces.

### 2. Cost and Performance Monitoring for Agent Calls

**Problem**: LLM API calls are expensive. Multi-agent systems can quickly accumulate costs without visibility.

**Solution**: Track operational costs and performance:
- `cost` field: Monetary cost per operation
- `total_tokens` field: LLM token consumption
- `latency` field: Auto-calculated response time

**Application to Our Benchmark**:
- Tier 2 LLM Judge tracks cost/tokens for coordination assessment
- Tier 3 Latency evaluator identifies performance bottlenecks
- Budget tracking for benchmark execution costs

### 3. Error Propagation and Fault Diagnosis

**Problem**: When multi-agent workflows fail, pinpointing the root cause agent is difficult.

**Solution**: Error field captures exception information:
- `error` field: Exception details at failure point
- Trace chain shows error propagation path
- Parent-child relationships reveal cascading failures

**Application to Our Benchmark**: Identify which agent in a coordination scenario caused task failure. Graph analysis can highlight agents with high error rates.

### 4. Business Process Optimization

**Problem**: Coordination inefficiencies (bottlenecks, redundant communication) are invisible without trace data.

**Solution**: Analyze trace patterns to identify:
- High-centrality agents (coordination bottlenecks)
- Redundant message patterns
- Isolated agents (poor integration)
- Long-latency interactions

**Application to Our Benchmark**: Core value proposition - measure "how agents coordinate" through graph analysis of traced interactions.

---

## Design Principles

### Architecture Patterns

#### 1. Distributed Call Tracing
- **Trace ID Propagation**: Single `trace_id` spans entire multi-agent workflow
- **Parent-Child Relationships**: `parent_step_id` links nested operations
- **Cross-Service Boundaries**: Traces persist across agent boundaries

#### 2. Intelligent Context Management
- **Automatic Propagation**: SDK maintains trace context across async operations
- **Manual Control**: Explicit `parent_step_id` for complex patterns
- **Context Isolation**: Each benchmark run uses unique `trace_id`

#### 3. Diverse Integration Approaches
Five patterns (manual to fully automated) accommodate different implementation styles and existing codebases.

---

## Data Model

### ResponseTrace (Root Container)

```python
from pydantic import BaseModel, Field

class ResponseTrace(BaseModel):
    trace_id: str = Field(description="Unique identifier for entire trace")
    steps: list[InteractionStep] = Field(description="Collection of interaction steps")
```

**Purpose**: Aggregate all steps from a single benchmark execution.

### InteractionStep (A2A Step Specification)

Defined in `src/agentbeats/models.py`:

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class CallType(str, Enum):
    """A2A Traceability Extension call types."""
    AGENT = "AGENT"  # Agent-to-agent calls
    TOOL = "TOOL"    # External API calls (LLM, databases)
    HOST = "HOST"    # Local computation

class InteractionStep(BaseModel):
    """A2A Traceability Extension Step model.

    Conforms to: github.com/a2aproject/a2a-samples/extensions/traceability/v1
    """
    # Required A2A fields
    step_id: str = Field(description="Unique step identifier (UUID)")
    trace_id: str = Field(description="Parent trace identifier")
    call_type: CallType = Field(description="Operation type: AGENT/TOOL/HOST")
    start_time: datetime = Field(description="ISO 8601 operation start")
    end_time: datetime = Field(description="ISO 8601 operation end")

    # Optional A2A fields
    parent_step_id: str | None = Field(default=None, description="Hierarchical parent reference")
    latency: int | None = Field(default=None, description="Duration in milliseconds (auto-calculated)")
    cost: float | None = Field(default=None, description="Monetary operation cost")
    total_tokens: int | None = Field(default=None, description="LLM token consumption")
    error: str | None = Field(default=None, description="Exception information if failed")
    name: str | None = Field(default=None, description="Human-readable operation description")
    additional_attributes: dict = Field(default_factory=dict, description="Custom metadata")

    # Domain-specific coordination fields
    sender_url: str = Field(description="Source agent URL")
    receiver_url: str = Field(description="Target agent URL")
    message_content: dict = Field(description="Message payload")
    task_id: str | None = Field(default=None, description="A2A task identifier")
```

### CallType Classification

| Type | Use Case | Examples in Our Benchmark |
|------|----------|---------------------------|
| **AGENT** | Agent-to-agent communication | Messenger → Purple agents |
| **TOOL** | External API/service calls | LLM Judge → OpenAI API |
| **HOST** | Local computation | Graph analysis, Latency percentiles |

**Filtering Example**:
```python
# Only analyze agent-to-agent coordination
agent_calls = [s for s in trace.steps if s.call_type == CallType.AGENT]

# Track LLM costs separately
llm_costs = sum(s.cost for s in trace.steps if s.call_type == CallType.TOOL and s.cost)
```

---

## Five Integration Patterns

### Pattern 1: Full Manual Control

**Description**: Developer explicitly manages trace creation, step lifecycle, and termination.

**Use Case**: Maximum flexibility, custom trace logic, legacy code integration.

**Example**:
```python
import uuid
from datetime import datetime

# Create trace manually
trace = ResponseTrace(trace_id=str(uuid.uuid4()), steps=[])

# Create step manually
step = InteractionStep(
    step_id=str(uuid.uuid4()),
    trace_id=trace.trace_id,
    call_type=CallType.AGENT,
    start_time=datetime.now(),
    end_time=datetime.now(),  # Placeholder
    sender_url="http://green:8000",
    receiver_url="http://purple:8000",
    message_content={"task": "evaluate"},
)

# Execute operation
try:
    result = await agent.call(message)
    step.end_time = datetime.now()
    step.latency = int((step.end_time - step.start_time).total_seconds() * 1000)
except Exception as e:
    step.end_time = datetime.now()
    step.error = str(e)

trace.steps.append(step)
```

**Pros**: Full control, no framework dependencies
**Cons**: Verbose, error-prone, manual latency calculation

---

### Pattern 2: Context Manager

**Description**: Use `with` statements to automatically handle step initialization and closure.

**Use Case**: Cleaner code, automatic exception tracking, manual trace management.

**Example**:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def trace_step(trace_id: str, call_type: CallType, name: str):
    step = InteractionStep(
        step_id=str(uuid.uuid4()),
        trace_id=trace_id,
        call_type=call_type,
        name=name,
        start_time=datetime.now(),
        end_time=datetime.now(),  # Placeholder
    )
    try:
        yield step
        step.end_time = datetime.now()
        step.latency = int((step.end_time - step.start_time).total_seconds() * 1000)
    except Exception as e:
        step.end_time = datetime.now()
        step.error = str(e)
        step.latency = int((step.end_time - step.start_time).total_seconds() * 1000)
        raise

# Usage
trace_id = str(uuid.uuid4())
async with trace_step(trace_id, CallType.AGENT, "Call Purple Agent") as step:
    result = await messenger.send_message(agent_url, message)
    step.sender_url = "http://green:8000"
    step.receiver_url = agent_url
    step.message_content = message
```

**Pros**: Automatic cleanup, exception handling, reduced boilerplate
**Cons**: Still requires manual trace management

---

### Pattern 3: Decorator Automation

**Description**: Function decorators transparently wrap operations, automatically recording calls.

**Use Case**: Minimal code changes, retrofit existing functions, consistent tracing.

**Example**:
```python
from functools import wraps

def trace_agent_call(call_type: CallType):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            trace_id = kwargs.get('trace_id') or str(uuid.uuid4())
            step = InteractionStep(
                step_id=str(uuid.uuid4()),
                trace_id=trace_id,
                call_type=call_type,
                name=func.__name__,
                start_time=datetime.now(),
                end_time=datetime.now(),
            )
            try:
                result = await func(*args, **kwargs)
                step.end_time = datetime.now()
                step.latency = int((step.end_time - step.start_time).total_seconds() * 1000)
                return result
            except Exception as e:
                step.end_time = datetime.now()
                step.error = str(e)
                step.latency = int((step.end_time - step.start_time).total_seconds() * 1000)
                raise
        return wrapper
    return decorator

# Usage
@trace_agent_call(CallType.AGENT)
async def call_purple_agent(agent_url: str, message: dict, trace_id: str):
    return await client.send_message(agent_url, message)
```

**Pros**: Non-invasive, reusable, clean separation of concerns
**Cons**: Limited customization per call, hidden trace context

---

### Pattern 4: Client Wrapping

**Description**: Wrap existing clients to add tracing functionality transparently.

**Use Case**: Non-invasive integration, external libraries, consistent instrumentation.

**Example**:
```python
class TracedMessenger:
    def __init__(self, messenger, trace_id: str):
        self._messenger = messenger
        self._trace_id = trace_id

    async def send_message(self, agent_url: str, message: dict) -> dict:
        step = InteractionStep(
            step_id=str(uuid.uuid4()),
            trace_id=self._trace_id,
            call_type=CallType.AGENT,
            name=f"Send to {agent_url}",
            start_time=datetime.now(),
            end_time=datetime.now(),
            sender_url=self._messenger.green_url,
            receiver_url=agent_url,
            message_content=message,
        )
        try:
            result = await self._messenger.send_message(agent_url, message)
            step.end_time = datetime.now()
            step.latency = int((step.end_time - step.start_time).total_seconds() * 1000)
            return result
        except Exception as e:
            step.end_time = datetime.now()
            step.error = str(e)
            step.latency = int((step.end_time - step.start_time).total_seconds() * 1000)
            raise
        finally:
            # Store step somewhere (e.g., in-memory list, database)
            self._messenger.trace_storage.append(step)

# Usage
messenger = Messenger()
traced_messenger = TracedMessenger(messenger, trace_id=str(uuid.uuid4()))
result = await traced_messenger.send_message("http://purple:8000", message)
```

**Pros**: No modification to original client, easy rollback
**Cons**: Requires wrapper maintenance, potential interface mismatches

---

### Pattern 5: Global Tracing (Executor-Level)

**Description**: Enable system-wide tracing at the executor level, automatically capturing all operations.

**Use Case**: Complete observability, production monitoring, zero code changes.

**Example**:
```python
class TracedExecutor:
    def __init__(self, executor, enable_tracing: bool = True):
        self._executor = executor
        self._enable_tracing = enable_tracing
        self._current_trace_id: str | None = None

    async def execute(self, task_id: str, participants: dict) -> dict:
        if self._enable_tracing:
            self._current_trace_id = str(uuid.uuid4())

        # Executor automatically instruments all downstream calls
        result = await self._executor.execute(task_id, participants)

        if self._enable_tracing:
            result["trace_id"] = self._current_trace_id
            result["trace_steps"] = self._executor.get_trace_steps()

        return result

# Usage
executor = AgentExecutor()
traced_executor = TracedExecutor(executor, enable_tracing=True)
result = await traced_executor.execute(task_id, participants)
```

**Pros**: Zero code changes, comprehensive coverage, toggle on/off
**Cons**: Performance overhead, potential over-instrumentation

---

### Pattern Comparison

| Pattern | Code Changes | Flexibility | Automation | Best For |
|---------|--------------|-------------|------------|----------|
| **Manual** | High | Maximum | None | Custom logic, legacy code |
| **Context Manager** | Medium | High | Partial | Explicit boundaries, clean code |
| **Decorator** | Low | Medium | High | Function-level tracing |
| **Client Wrap** | None (wrapper) | Medium | High | External libraries |
| **Global** | None | Low | Maximum | Production monitoring |

**Recommendation for Our Benchmark**: Use **Pattern 4 (Client Wrapping)** for messenger operations, combined with **Pattern 2 (Context Manager)** for evaluator steps.

---

## Extension Activation

### 1. AgentCard Declaration (Server-Side)

Agents declare extension support in their AgentCard:

```python
# src/agentbeats/agent_card.py
AGENT_CARD = {
    "name": "green-agent-coordination-benchmark",
    "description": "Graph-based multi-agent coordination benchmark",
    "version": "0.0.0",
    "url": "http://localhost:8000",
    "extensions": [
        "https://github.com/a2aproject/a2a-samples/extensions/traceability/v1",
        "https://github.com/a2aproject/a2a-samples/extensions/timestamp/v1",
    ],
    # ...
}
```

**Purpose**: Advertise support so clients know extensions are available.

### 2. Client Opt-In (Request Headers)

Clients activate extensions by sending activation headers:

```python
# Messenger sends extension activation header
headers = {
    "X-A2A-Extensions": "https://github.com/a2aproject/a2a-samples/extensions/traceability/v1",
    "Content-Type": "application/json",
}

client = await ClientFactory.connect(agent_url, headers=headers)
```

**Purpose**: Explicitly opt-in to extension behavior for specific requests.

### 3. Extension Discovery Flow

```
1. Client: GET /.well-known/agent-card.json
2. Server: Returns { "extensions": ["traceability/v1", "timestamp/v1"] }
3. Client: Checks if desired extension is supported
4. Client: Sends request with X-A2A-Extensions header
5. Server: Activates extension behavior for this request
```

### Timestamp Extension Integration

**Mechanism**: Adds ISO 8601 timestamps to Message and Artifact objects.

**AgentCard**: Same declaration as traceability (already in `AGENT_CARD`)

**Activation**: Automatic when traceability is enabled (timestamps populate `start_time` and `end_time`)

**Precision**: Microsecond-level (`2024-01-15T10:30:45.123456+00:00`)

**Relationship to Traceability**: Timestamps enable latency auto-calculation:
```python
latency = int((end_time - start_time).total_seconds() * 1000)  # milliseconds
```

---

## Implementation Examples

### Messenger with Extension Activation

```python
# src/agentbeats/messenger.py
from a2a.client import ClientFactory
from agentbeats.models import InteractionStep, CallType
import uuid
from datetime import datetime

class Messenger:
    def __init__(self, green_agent_url: str):
        self.green_agent_url = green_agent_url
        self.trace_storage: list[InteractionStep] = []

    async def talk_to_agent(
        self,
        agent_url: str,
        message: dict,
        trace_id: str
    ) -> InteractionStep:
        """Send message and capture A2A trace."""
        step_id = str(uuid.uuid4())
        start_time = datetime.now()

        # Activate extensions via header
        headers = {
            "X-A2A-Extensions": "https://github.com/a2aproject/a2a-samples/extensions/traceability/v1"
        }

        try:
            client = await ClientFactory.connect(agent_url, headers=headers)
            response = await client.send_task(message)
            end_time = datetime.now()

            step = InteractionStep(
                step_id=step_id,
                trace_id=trace_id,
                call_type=CallType.AGENT,
                start_time=start_time,
                end_time=end_time,
                latency=int((end_time - start_time).total_seconds() * 1000),
                sender_url=self.green_agent_url,
                receiver_url=agent_url,
                message_content=message,
                task_id=response.task_id,
                name=f"Agent call to {agent_url}",
            )

            self.trace_storage.append(step)
            return step

        except Exception as e:
            end_time = datetime.now()
            step = InteractionStep(
                step_id=step_id,
                trace_id=trace_id,
                call_type=CallType.AGENT,
                start_time=start_time,
                end_time=end_time,
                latency=int((end_time - start_time).total_seconds() * 1000),
                error=str(e),
                sender_url=self.green_agent_url,
                receiver_url=agent_url,
                message_content=message,
                name=f"Failed call to {agent_url}",
            )
            self.trace_storage.append(step)
            raise

    def get_trace(self, trace_id: str) -> list[InteractionStep]:
        """Retrieve all steps for a trace."""
        return [s for s in self.trace_storage if s.trace_id == trace_id]
```

### LLM Judge with Cost Tracking

```python
# src/agentbeats/evals/llm_judge.py
from openai import AsyncOpenAI
from agentbeats.models import InteractionStep, CallType
import uuid
from datetime import datetime

class LLMJudge:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def evaluate(
        self,
        traces: list[InteractionStep],
        trace_id: str
    ) -> dict:
        """Evaluate coordination with cost tracking."""
        step_id = str(uuid.uuid4())
        start_time = datetime.now()

        prompt = self._build_prompt(traces)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )

            end_time = datetime.now()

            # Track LLM call as TOOL step
            llm_step = InteractionStep(
                step_id=step_id,
                trace_id=trace_id,
                call_type=CallType.TOOL,
                start_time=start_time,
                end_time=end_time,
                latency=int((end_time - start_time).total_seconds() * 1000),
                cost=response.usage.prompt_tokens * 0.00001,  # Example pricing
                total_tokens=response.usage.total_tokens,
                name="LLM Judge - Coordination Analysis",
                additional_attributes={
                    "model": self.model,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                },
            )

            return {
                "judgment": response.choices[0].message.content,
                "llm_step": llm_step,
            }

        except Exception as e:
            end_time = datetime.now()

            # Track failed LLM call
            llm_step = InteractionStep(
                step_id=step_id,
                trace_id=trace_id,
                call_type=CallType.TOOL,
                start_time=start_time,
                end_time=end_time,
                latency=int((end_time - start_time).total_seconds() * 1000),
                error=str(e),
                name="LLM Judge - Failed",
            )

            # Fallback to rule-based
            return {
                "judgment": self._fallback_evaluate(traces),
                "llm_step": llm_step,
            }
```

---

## Best Practices

### 1. Appropriate Tracing Granularity

**Principle**: Trace business-relevant operations, not implementation details.

**Do Trace**:
- Agent-to-agent calls
- LLM API calls
- Major computation steps (graph analysis, latency calculation)
- External service calls

**Don't Trace**:
- Variable assignments
- Utility function calls
- Internal class methods
- Logging operations

**Example**:
```python
# Good - Business operation
async with trace_step(trace_id, CallType.AGENT, "Evaluate Agent Coordination"):
    result = await evaluate_coordination(agents)

# Bad - Implementation detail
async with trace_step(trace_id, CallType.HOST, "Parse JSON"):
    data = json.loads(response)  # Too granular
```

### 2. Meaningful Step Naming

**Principle**: Use clear business semantics, not technical implementation details.

**Good Names**:
- `"Agent call to http://purple:8000"`
- `"LLM Judge - Coordination Analysis"`
- `"Graph centrality computation"`
- `"Latency percentile calculation"`

**Bad Names**:
- `"function_call"`
- `"Step 1"`
- `"execute"`
- `"process_data"`

**Parameterized Names**:
```python
step.name = f"Agent call to {agent_url}"
step.name = f"Database query - {table_name}"
step.name = f"LLM call - {self.model}"
```

### 3. Proper Error Handling

**Principle**: Always populate `error` field on failure, maintain trace chain.

**Pattern**:
```python
try:
    result = await operation()
    step.end_time = datetime.now()
    step.latency = calculate_latency(step)
except Exception as e:
    step.end_time = datetime.now()
    step.error = str(e)
    step.latency = calculate_latency(step)
    step.additional_attributes["error_type"] = type(e).__name__
    step.additional_attributes["status"] = "failed"
    raise  # Re-raise to propagate error
```

**Error Analysis**:
```python
# Identify failing agents
failed_steps = [s for s in trace.steps if s.error is not None]
error_agents = {s.sender_url for s in failed_steps}

# Error rate calculation
error_rate = len(failed_steps) / len(trace.steps)
```

### 4. Sensitive Information Protection

**Principle**: Never log credentials, PII, or secrets in trace data.

**Sanitize Before Storing**:
```python
def sanitize_message(message: dict) -> dict:
    """Remove sensitive fields from message."""
    sanitized = message.copy()
    sensitive_keys = ["api_key", "password", "token", "secret", "authorization"]

    for key in sensitive_keys:
        if key in sanitized:
            sanitized[key] = "[REDACTED]"

    return sanitized

# Usage
step.message_content = sanitize_message(message)
step.additional_attributes["api_key"] = "[REDACTED]"
```

**What to Redact**:
- API keys, tokens, passwords
- Personal identifiable information (PII)
- Credit card numbers, SSNs
- Internal system details (database URLs, internal IPs)

### 5. Consistent Timestamp Format

**Principle**: Always use UTC ISO 8601 format with timezone.

**Correct Format**:
```python
from datetime import datetime, timezone

start_time = datetime.now(timezone.utc)  # With timezone
iso_string = start_time.isoformat()      # "2024-01-15T10:30:45.123456+00:00"
```

**Why UTC**: Eliminates timezone confusion in distributed systems.

### 6. Parent-Child Relationships

**Principle**: Use `parent_step_id` to link nested operations.

**Example**:
```python
# Parent step: Overall coordination evaluation
parent_step = InteractionStep(
    step_id=str(uuid.uuid4()),
    trace_id=trace_id,
    call_type=CallType.HOST,
    name="Coordination Evaluation",
    start_time=datetime.now(),
    end_time=datetime.now(),
)

# Child steps: Individual agent calls
for agent_url in agents:
    child_step = InteractionStep(
        step_id=str(uuid.uuid4()),
        trace_id=trace_id,
        parent_step_id=parent_step.step_id,  # Link to parent
        call_type=CallType.AGENT,
        name=f"Call to {agent_url}",
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
```

**Visualization**:
```
Parent: Coordination Evaluation [HOST]
  ├─ Child: Call to Agent A [AGENT]
  ├─ Child: Call to Agent B [AGENT]
  └─ Child: Call to Agent C [AGENT]
```

---

## Performance Monitoring

### Trace Data Analysis

**Latency Distribution**:
```python
import numpy as np

latencies = [s.latency for s in trace.steps if s.latency]

metrics = {
    "avg": np.mean(latencies),
    "p50": np.percentile(latencies, 50),
    "p95": np.percentile(latencies, 95),
    "p99": np.percentile(latencies, 99),
    "max": max(latencies),
}
```

**Cost Tracking**:
```python
# Total LLM costs
llm_steps = [s for s in trace.steps if s.call_type == CallType.TOOL]
total_cost = sum(s.cost for s in llm_steps if s.cost)
total_tokens = sum(s.total_tokens for s in llm_steps if s.total_tokens)

print(f"LLM Cost: ${total_cost:.4f} ({total_tokens} tokens)")
```

**Bottleneck Detection**:
```python
# Find slowest operations
sorted_steps = sorted(trace.steps, key=lambda s: s.latency or 0, reverse=True)
bottlenecks = sorted_steps[:5]

for step in bottlenecks:
    print(f"{step.name}: {step.latency}ms")
```

### Real-Time Monitoring Dashboard

**Metrics to Track**:
1. **Throughput**: Traces completed per minute
2. **Error Rate**: Percentage of failed steps
3. **Latency**: p50, p95, p99 response times
4. **Cost**: Total spend on LLM calls
5. **Agent Health**: Error rate per agent URL

**Example Dashboard Data**:
```python
def compute_dashboard_metrics(traces: list[ResponseTrace]) -> dict:
    all_steps = [s for t in traces for s in t.steps]

    return {
        "total_traces": len(traces),
        "total_steps": len(all_steps),
        "error_rate": len([s for s in all_steps if s.error]) / len(all_steps),
        "avg_latency": np.mean([s.latency for s in all_steps if s.latency]),
        "total_cost": sum(s.cost for s in all_steps if s.cost),
        "agent_calls": len([s for s in all_steps if s.call_type == CallType.AGENT]),
        "llm_calls": len([s for s in all_steps if s.call_type == CallType.TOOL]),
    }
```

---

## Integration with External Systems

### Logging System Integration

**Purpose**: Correlate traces with application logs for debugging.

**Pattern**:
```python
import logging

logger = logging.getLogger(__name__)

class Messenger:
    async def talk_to_agent(self, agent_url: str, message: dict, trace_id: str):
        step_id = str(uuid.uuid4())

        # Log with trace context
        logger.info(
            "Agent call started",
            extra={
                "trace_id": trace_id,
                "step_id": step_id,
                "agent_url": agent_url,
                "call_type": "AGENT",
            }
        )

        try:
            result = await self._send_message(agent_url, message)

            logger.info(
                "Agent call succeeded",
                extra={
                    "trace_id": trace_id,
                    "step_id": step_id,
                    "latency_ms": step.latency,
                }
            )

            return result

        except Exception as e:
            logger.error(
                "Agent call failed",
                extra={
                    "trace_id": trace_id,
                    "step_id": step_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise
```

**Benefit**: Search logs by `trace_id` to see full execution context.

### Monitoring System Integration (Prometheus)

**Purpose**: Export trace metrics for alerting and visualization.

**Pattern**:
```python
from prometheus_client import Counter, Histogram

# Define metrics
agent_calls_total = Counter(
    'agent_calls_total',
    'Total number of agent calls',
    ['agent_url', 'status']
)

agent_call_duration = Histogram(
    'agent_call_duration_seconds',
    'Agent call duration in seconds',
    ['agent_url']
)

class Messenger:
    async def talk_to_agent(self, agent_url: str, message: dict, trace_id: str):
        start = time.time()

        try:
            result = await self._send_message(agent_url, message)

            # Record success
            agent_calls_total.labels(agent_url=agent_url, status="success").inc()
            agent_call_duration.labels(agent_url=agent_url).observe(time.time() - start)

            return result

        except Exception as e:
            # Record failure
            agent_calls_total.labels(agent_url=agent_url, status="error").inc()
            agent_call_duration.labels(agent_url=agent_url).observe(time.time() - start)
            raise
```

**Prometheus Queries**:
```promql
# Error rate
rate(agent_calls_total{status="error"}[5m]) / rate(agent_calls_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(agent_call_duration_seconds_bucket[5m]))

# Calls per agent
sum by (agent_url) (rate(agent_calls_total[5m]))
```

---

## Real-World Application Scenarios

### 1. Intelligent Customer Service System Tracing

**Scenario**: Multi-agent customer service with triage, specialist, and escalation agents.

**Agents**:
- Triage Agent: Routes customer query
- FAQ Agent: Handles common questions
- Specialist Agent: Domain expert responses
- Escalation Agent: Human handoff

**Trace Analysis**:
```python
# Identify routing patterns
triage_calls = [s for s in trace.steps if "triage" in s.sender_url]
routing_distribution = Counter(s.receiver_url for s in triage_calls)

# Measure escalation rate
escalations = [s for s in trace.steps if "escalation" in s.receiver_url]
escalation_rate = len(escalations) / len(triage_calls)

# Find bottleneck agents
latencies_by_agent = defaultdict(list)
for s in trace.steps:
    if s.latency:
        latencies_by_agent[s.receiver_url].append(s.latency)

bottleneck = max(latencies_by_agent.items(), key=lambda x: np.mean(x[1]))
```

### 2. Financial Risk Control System Monitoring

**Scenario**: Multi-agent fraud detection with data collection, analysis, and decision agents.

**Agents**:
- Data Collector: Gathers transaction data
- Pattern Analyzer: Detects anomalies
- Risk Scorer: Calculates risk score
- Decision Engine: Approve/reject decision

**Trace Analysis**:
```python
# Track processing time per transaction
transaction_traces = load_traces(date_range)
processing_times = [
    max(s.end_time for s in t.steps) - min(s.start_time for s in t.steps)
    for t in transaction_traces
]

# Identify high-risk decisions
risk_steps = [s for t in transaction_traces for s in t.steps if "risk" in s.name]
high_risk = [s for s in risk_steps if s.additional_attributes.get("risk_score", 0) > 0.8]

# Audit trail for compliance
def generate_audit_trail(trace_id: str) -> list[dict]:
    trace = get_trace(trace_id)
    return [
        {
            "timestamp": s.start_time.isoformat(),
            "agent": s.sender_url,
            "action": s.name,
            "decision": s.additional_attributes.get("decision"),
            "risk_score": s.additional_attributes.get("risk_score"),
        }
        for s in trace.steps
    ]
```

### 3. Graph Coordination Benchmark (Our Use Case)

**Scenario**: Evaluate multi-agent coordination patterns through graph analysis.

**Workflow**:
1. Submit coordination task to green agent
2. Green agent orchestrates purple agents via messenger
3. Messenger captures all agent-to-agent interactions as InteractionSteps
4. Graph evaluator builds coordination graph from traces
5. LLM judge assesses semantic coordination quality
6. Latency evaluator identifies bottlenecks

**Trace Analysis**:
```python
# Build coordination graph
import networkx as nx

G = nx.DiGraph()
agent_steps = [s for s in trace.steps if s.call_type == CallType.AGENT]

for step in agent_steps:
    G.add_edge(step.sender_url, step.receiver_url, weight=step.latency or 0)

# Compute centrality
centrality = nx.betweenness_centrality(G)
bottleneck_agent = max(centrality.items(), key=lambda x: x[1])

# Detect isolated agents
isolated = [node for node in G.nodes() if G.degree(node) == 0]

# Coordination efficiency
density = nx.density(G)
clustering = nx.average_clustering(G)
```

---

## Testing

### Validate A2A Compliance

```python
# tests/test_models.py
import pytest
from agentbeats.models import InteractionStep, CallType
from datetime import datetime

def test_interaction_step_conforms_to_a2a():
    """Verify InteractionStep has required A2A fields."""
    step = InteractionStep(
        step_id="test-123",
        trace_id="trace-456",
        call_type=CallType.AGENT,
        start_time=datetime.now(),
        end_time=datetime.now(),
        sender_url="http://green:8000",
        receiver_url="http://purple:8000",
        message_content={},
    )

    # Required fields present
    assert step.step_id
    assert step.trace_id
    assert step.call_type in [CallType.AGENT, CallType.TOOL, CallType.HOST]
    assert step.start_time
    assert step.end_time

    # Latency calculable
    assert (step.end_time - step.start_time).total_seconds() >= 0
```

### Validate Extension Activation

```python
# tests/test_messenger.py
from unittest.mock import patch

@pytest.mark.asyncio
async def test_messenger_sends_extension_header():
    """Verify X-A2A-Extensions header sent with requests."""
    messenger = Messenger("http://green:8000")

    with patch("a2a.client.ClientFactory.connect") as mock_connect:
        await messenger.talk_to_agent("http://purple:8000", {"task": "test"}, "trace-123")

        # Verify extension activation header
        call_args = mock_connect.call_args
        headers = call_args.kwargs.get("headers", {})

        assert "X-A2A-Extensions" in headers
        assert "traceability/v1" in headers["X-A2A-Extensions"]
```

---

## References

- [A2A Traceability Extension Specification](https://a2aprotocol.ai/docs/guide/traceability-extension-analysis)
- [A2A Timestamp Extension Specification](https://a2aprotocol.ai/docs/guide/a2a-timestamp-extension-analysis)
- [A2A Protocol Python SDK](https://github.com/a2aproject/a2a-sdk-python)
- [A2A Protocol Specification](https://a2aprotocol.ai/docs/guide/a2a-protocol-specification-python)
