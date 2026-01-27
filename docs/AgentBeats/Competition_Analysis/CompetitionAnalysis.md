# AgentBeats Competition Analysis

## Overview

**Total Agents Analyzed**: 100+ across 14 categories
**Data Sources**: Claude API analysis + Firecrawl extraction
**Last Updated**: 2026-01-17

## Agent Distribution by Category

| Category | Count | Notable Agents |
| -------- | ----- | -------------- |
| Cybersecurity | 18+ | netheal-purple, RCABench, cybergym, VulnHunter |
| Coding | 20+ | SWE-Bench-A2A, coding-debater, spider2-sql-db, ArchX |
| Web | 19+ | webshop-plus, WABE, AIpolicyBench, web-agent-judge |
| Multi-agent | 11 | **GraphJudge**, PertBench, tau2-bench |
| Software Testing | 5 | swebench-verified, RaidAI, terminal-bench |
| Legal Domain | 5 | ChinaLawBridge, legal-agent-green |
| Finance | 3+ | Alpha-Cortex-AI, AgentBusters-Finance |
| Research | 17 | counterfacts, dm-control, hepex-analysisops |
| Agent Safety | 16 | AgentHarm, PersonaGym, NAAMSE |
| DeFi | 1 | DeFiGym |
| Computer Use | 3 | create-your-reality, cs294 |

## GraphJudge Position

**Category**: Multi-agent Evaluation (Green Agent)
**Author**: qte77
**Status**: Registered 1 day ago

### Unique Differentiator

**Only agent using graph-based coordination analysis** via NetworkX

- Measures *how* agents coordinate, not just *what* they accomplish
- Multi-tier: Graph metrics + LLM-as-judge + text similarity + latency

### Tech Stack

Python 3.13+, NetworkX, A2A SDK, Pydantic v2, OpenAI SDK, uvicorn, Docker

### Repository

<https://github.com/qte77/RDI-AgentX-AgentBeats-Competition>

## Key Competitors

### 1. SWE-Bench-A2A (ManishMuttreja1)

- **Innovation**: Contamination detection (memorization vs reasoning)
- **Approach**: Mutation-based testing, multi-provider (Claude, GPT-4o, Haiku)
- **Finding**: 14-15% performance drop when problems mutated
- **Robustness**: fuzz (97.7%), edge cases (44.0%), mutation (22.0%)

### 2. PertBench (HaoranShao)

- **Innovation**: Domain-specific biology QA with paraphrase robustness
- **Approach**: Template-based question variations, majority voting
- **Metrics**: accuracy, coverage, invalid/ambiguous rates, token cost

### 3. spider2-sql-db (yiren-liu)

- **Innovation**: Real-world enterprise text-to-SQL on Snowflake
- **Dataset**: Spider2-Snow with 1,000+ column databases
- **ArXiv**: <https://arxiv.org/abs/2411.07763>

### 4. WABE (hjerpe)

- **Innovation**: Web Agent Browser Evaluation
- **ArXiv**: <https://arxiv.org/abs/2504.01382>
- **Repository**: <https://github.com/Dimmmas28/wabe>

### 5. coding-debater (Lumin-Lab)

- **Innovation**: Adversarial debate format for code assessment
- **Focus**: Reasoning and explanation quality (similar to GraphJudge's "how" focus)

## Novel Approaches Observed

| Approach | Agents | Focus |
| -------- | ------ | ----- |
| **Graph-based coordination** | GraphJudge | Interaction patterns |
| **Contamination detection** | SWE-Bench-A2A | Memorization vs reasoning |
| **Paraphrase robustness** | PertBench | Consistency across rephrasings |
| **Domain-specific QA** | PertBench, spider2-sql | Biology, SQL with real DBs |
| **Adversarial debate** | coding-debater | Argumentation quality |
| **LLM-as-judge** | GraphJudge, coding-debater | Qualitative assessment |

## Common Patterns

### Technology Stack (90%+ of agents)

- Python
- Docker (linux/amd64)
- A2A Protocol
- GitHub Actions for CI/CD

### Green/Purple Distribution

- Green (Evaluators): ~40%
- Purple (Competitors): ~60%

### External Links

- **ArXiv papers**: 8 agents (spider2-sql, WABE, ArchX, Legal-agent, etc.)
- **GitHub repos**: 90%+ of agents
- **Leaderboards**: 60%+ of agents

## GraphJudge Strengths vs Competition

✅ **Novel**: Only graph-based evaluator in competition
✅ **Multi-tier**: Combines quantitative + qualitative + consistency
✅ **LLM fallback**: Graceful degradation without API keys
✅ **Trace-based**: Full interaction capture for replay/debugging
✅ **Domain-agnostic**: Works across all agent types

## Identified Gaps (Opportunities)

❌ **No contamination detection** (SWE-Bench has this)
❌ **No paraphrase testing** (PertBench has this)
❌ **Simple text metrics** (Jaccard only, no embeddings)
❌ **No benchmark results** (newly registered)
❌ **No ArXiv paper** (8+ competitors have papers)

## Actionable Recommendations

### High-Impact Quick Wins

1. **Publish benchmark results** → Establish credibility
2. **Add semantic similarity** (sentence-transformers) → Better text metrics
3. **Create visualization exports** (Graphviz/D3.js) → Show coordination patterns

### Medium-Term

1. **Add paraphrase testing** → Consistency validation
2. **Multi-provider support** → Test Claude/GPT-4o/Gemini simultaneously
3. **Write ArXiv paper** → Academic credibility

### Long-Term

1. **Contamination detection module** → Novel: graph + contamination
2. **Cross-track meta-evaluation** → Evaluate evaluators

## Competition Insights

### Recent Activity (Last 24 hours)

- 10+ new agents registered
- Heavy activity in: Coding, Cybersecurity, Web categories
- Multi-agent evaluation: Limited competition (good positioning)

### Leaderboard Status

Most agents show "leaderboard unavailable" → Early stage competition

### Documentation Quality

- High: Agents with ArXiv papers, detailed READMEs
- Medium: GitHub repos with basic documentation
- Low: Name-only registrations

## Sources

- Claude API analysis: 11 detailed agent profiles
- Firecrawl extraction: 100+ agent listings
- AgentBeats platform: <https://agentbeats.dev/>
- Competition page: <https://rdi.berkeley.edu/agentx-agentbeats.html>
