# Abstract

## GraphJudge: Measuring How Agents Coordinate

**Problem**: Current benchmarks evaluate whether multi-agent systems succeed, not *how* they collaborate. Coordination failures—bottlenecks, isolation, inefficiency—remain invisible.

**Solution**: GraphJudge transforms agent interactions into coordination graphs and evaluates collaboration quality through three tiers:

| Tier | Method | Measures |
|------|--------|----------|
| 1 | Graph Analysis (NetworkX) | Centrality, bottlenecks, isolation |
| 2 | LLM-as-Judge + Latency | Coordination quality, performance |
| 3 | Text Similarity (plugin) | Extensibility demonstration |

**Key Innovation**: No existing AgentBeats benchmark analyzes coordination patterns through graph structure.

**Results**: 0% variance across independent runs—deterministic, reproducible evaluation.

**Value**: Actionable insights into *why* multi-agent systems fail to coordinate, not just *that* they failed.

---

See [GreenAgent-UserStory.md](GreenAgent-UserStory.md) for full problem statement.
