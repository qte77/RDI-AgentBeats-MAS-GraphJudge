# Resources

> **Last Updated**: 2026-01-31
> **Purpose**: External links for AgentX-AgentBeats competition and development

Central repository of all external resources, tools, and documentation needed for GraphJudge development and AgentBeats Phase 1 submission.

---

## AgentBeats Competition

### Official Platform

| Resource | Link | Purpose |
|----------|------|---------|
| Platform | [agentbeats.dev](https://agentbeats.dev) | Agent registration and leaderboards |
| Documentation | [docs.agentbeats.dev](https://docs.agentbeats.dev/tutorial/) | Official tutorial and guides |
| Discord | [discord.gg/uqZUta3MYa](https://discord.gg/uqZUta3MYa) | Community support (#legal-domain, #support) |
| Team Signup | [forms.gle/NHE8wYVgS6iJLwRj8](https://forms.gle/NHE8wYVgS6iJLwRj8) | Competition registration |

### Submission

| Resource | Link | Purpose |
|----------|------|---------|
| Phase 1 Submission | [forms.gle/1C5d8KXny2JBpZhz7](https://forms.gle/1C5d8KXny2JBpZhz7) | Green agent submission form |
| Deadline | January 31, 2026 | Phase 1 submission cutoff |

---

## Competition Templates

### Reference Repositories

| Repo | Purpose | Use Case |
|------|---------|----------|
| [green-agent-template](https://github.com/RDI-Foundation/green-agent-template) | Benchmark (green) agent scaffold | Starting point for new benchmarks |
| [agent-template](https://github.com/RDI-Foundation/agent-template) | General (purple) agent scaffold | Baseline participant agent |
| [agentbeats-leaderboard-template](https://github.com/RDI-Foundation/agentbeats-leaderboard-template) | Submission workflow | GitHub Actions for deployment |
| [agentbeats-tutorial](https://github.com/RDI-Foundation/agentbeats-tutorial) | End-to-end example | Learn A2A integration |
| [agentbeats-debate-leaderboard](https://github.com/RDI-Foundation/agentbeats-debate-leaderboard) | Debate benchmark example | Reference implementation |

---

## A2A Protocol

### Protocol Documentation

| Resource | Link | Content |
|----------|------|---------|
| Protocol Spec | [a2a-protocol.org](https://a2a-protocol.org/latest/) | Official A2A specification |
| Python Guide | [a2aprotocol.ai](https://a2aprotocol.ai/docs/guide/a2a-protocol-specification-python) | Python implementation guide |
| Python SDK | [github.com/a2aproject/a2a-python](https://github.com/a2aproject/a2a-python) | Official Python SDK |
| Google ADK | [google.github.io/adk-docs](https://google.github.io/adk-docs/a2a/intro/) | Google Agent Development Kit |

### A2A Extensions

| Extension | Purpose | Documentation |
|-----------|---------|---------------|
| Traceability | Interaction step tracking | [A2A Traceability Extension](https://a2a-protocol.org/latest/extensions/traceability/) |
| Timestamp | Latency measurement | [A2A Timestamp Extension](https://a2a-protocol.org/latest/extensions/timestamp/) |

---

## Core Dependencies

### Python Libraries

| Tool | Version | Purpose | Docs |
|------|---------|---------|------|
| NetworkX | ≥3.0 | Graph analysis (Tier 1) | [networkx.org/documentation](https://networkx.org/documentation/stable/) |
| OpenAI SDK | Latest | LLM Judge (Tier 2) | [platform.openai.com/docs](https://platform.openai.com/docs/api-reference) |
| NumPy | ≥1.24 | Latency percentiles | [numpy.org/doc](https://numpy.org/doc/stable/) |
| Pydantic | ≥2.0 | Data validation | [docs.pydantic.dev](https://docs.pydantic.dev/latest/) |
| FastAPI | ≥0.100 | HTTP server | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| uvicorn | Latest | ASGI server | [uvicorn.org](https://www.uvicorn.org/) |
| a2a-sdk | ≥0.3.20 | A2A protocol | [github.com/a2aproject/a2a-python](https://github.com/a2aproject/a2a-python) |

### Development Tools

| Tool | Purpose | Docs |
|------|---------|------|
| Docker | Containerization (linux/amd64) | [docs.docker.com](https://docs.docker.com/) |
| uv | Fast Python package manager | [github.com/astral-sh/uv](https://github.com/astral-sh/uv) |
| pytest | Testing framework | [docs.pytest.org](https://docs.pytest.org/en/stable/) |
| ruff | Linting and formatting | [docs.astral.sh/ruff](https://docs.astral.sh/ruff/) |

---

## GitHub Container Registry (GHCR)

### Deployment Guides

| Resource | Link | Purpose |
|----------|------|---------|
| GHCR Docs | [docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) | Push Docker images |
| Authentication | [docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry) | Docker login with PAT |
| Visibility | [docs.github.com/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility) | Make packages public |

### Our GHCR Images

| Image | Tag | URL |
|-------|-----|-----|
| Green Agent | latest | `ghcr.io/qte77/agentbeats-greenagent:latest` |
| Purple Agent | latest | `ghcr.io/qte77/agentbeats-purpleagent:latest` |

---

## Research Papers & Concepts

### Graph Theory for Multi-Agent Systems

| Topic | Reference | Relevance |
|-------|-----------|-----------|
| Centrality Metrics | [Newman (2010) - Networks: An Introduction](https://www.amazon.com/Networks-Introduction-Mark-Newman/dp/0199206651) | Betweenness, closeness, eigenvector |
| Coordination Patterns | [Wooldridge (2009) - MultiAgent Systems](https://www.wiley.com/en-us/An+Introduction+to+MultiAgent+Systems%2C+2nd+Edition-p-9780470519462) | Multi-agent coordination theory |
| Graph Clustering | [Fortunato (2010) - Community Detection](https://doi.org/10.1016/j.physrep.2009.11.002) | Clustering coefficient, communities |

### LLM-as-Judge

| Topic | Reference | Relevance |
|-------|-----------|-----------|
| LLM Evaluation | [Zheng et al. (2023) - Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) | LLM judge methodology |
| Prompt Engineering | [OpenAI Prompt Guide](https://platform.openai.com/docs/guides/prompt-engineering) | Effective prompt design |

### Phase 2 Research (Future)

| Topic | Reference | Status |
|-------|-----------|--------|
| ART Training | [WeightWatcher](https://github.com/calculatedcontent/weightwatcher) | 🔜 Phase 2 |
| Self-Evolving Agents | [DGM Paper](https://arxiv.org/abs/2410.04444) | 🔮 Phase 3 |
| Text Similarity | [PeerRead Dataset](https://github.com/allenai/PeerRead) | 🔜 Phase 2 |

---

## GraphJudge Project Documentation

### Internal Documentation

| Document | Path | Purpose |
|----------|------|---------|
| README | [README.md](../../README.md) | Project overview, quick start |
| Abstract | [docs/AgentBeats/ABSTRACT.md](ABSTRACT.md) | Competition abstract |
| Submission Guide | [docs/AgentBeats/SUBMISSION-GUIDE.md](SUBMISSION-GUIDE.md) | Phase 1 checklist |
| Competition Alignment | [docs/AgentBeats/COMPETITION-ALIGNMENT.md](COMPETITION-ALIGNMENT.md) | Requirements analysis |
| Limitations | [docs/AgentBeats/LIMITATIONS.md](LIMITATIONS.md) | Scope boundaries |
| Registration Guide | [docs/AgentBeats/AGENTBEATS_REGISTRATION.md](AGENTBEATS_REGISTRATION.md) | Platform registration steps |
| Quick Start | [docs/AgentBeats/QUICKSTART.md](QUICKSTART.md) | Local development guide |
| Green Agent PRD | [docs/GreenAgent-PRD.md](../GreenAgent-PRD.md) | Feature requirements |
| Green Agent User Story | [docs/GreenAgent-UserStory.md](../GreenAgent-UserStory.md) | Problem statement |
| Purple Agent PRD | [docs/PurpleAgent-PRD.md](../PurpleAgent-PRD.md) | Purple agent specs |

---

## Community & Support

### Getting Help

| Channel | Best For | Response Time |
|---------|----------|---------------|
| Discord #support | Technical issues, platform bugs | < 24 hours |
| Discord #legal-domain | Legal domain track discussions | < 48 hours |
| GitHub Issues | Reference repo questions | Community-driven |
| AgentBeats Docs | Self-service documentation | Immediate |

### Contributing

| Resource | Link | Purpose |
|----------|------|---------|
| CONTRIBUTING.md | [docs/CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution guidelines |
| Code of Conduct | [CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md) | Community standards |
| Issue Templates | [.github/ISSUE_TEMPLATE/](../../.github/ISSUE_TEMPLATE/) | Bug reports, features |

---

## Useful Tools

### Graph Visualization

| Tool | Purpose | Link |
|------|---------|------|
| Gephi | Interactive graph visualization | [gephi.org](https://gephi.org/) |
| Graphviz | Programmatic graph rendering | [graphviz.org](https://graphviz.org/) |
| NetworkX Draw | Python-based graph plotting | [NetworkX Drawing](https://networkx.org/documentation/stable/reference/drawing.html) |

### A2A Testing

| Tool | Purpose | Link |
|------|---------|------|
| Postman | API testing (JSON-RPC) | [postman.com](https://www.postman.com/) |
| curl | Command-line HTTP client | Built-in (Linux/Mac) |
| jq | JSON processor | [stedolan.github.io/jq](https://stedolan.github.io/jq/) |

### Docker Utilities

| Tool | Purpose | Link |
|------|---------|------|
| dive | Docker image layer explorer | [github.com/wagoodman/dive](https://github.com/wagoodman/dive) |
| docker-compose | Multi-container orchestration | [docs.docker.com/compose](https://docs.docker.com/compose/) |
| hadolint | Dockerfile linter | [github.com/hadolint/hadolint](https://github.com/hadolint/hadolint) |

---

## Competition Tracks & Sponsors

### Phase 1 Tracks

| Track | Sponsor | Prize | Details |
|-------|---------|-------|---------|
| Coding Agent | Nebius, Google DeepMind | TBD | Code generation benchmarks |
| Research Agent | OpenAI | TBD | Information retrieval |
| Multi-Agent | - | TBD | **GraphJudge Track** |
| Legal Domain | - | TBD | **GraphJudge Track** |
| Safety Agent | Lambda | TBD | Red-teaming, security |

### Custom Tracks

| Track | Sponsor | Deadline | Details |
|-------|---------|----------|---------|
| Agent Security | Lambda | Jan 31, 2026 | Red-teaming challenge |
| τ²-Bench | Sierra | March 30, 2026 | Advanced benchmarking |
| OpenEnv Challenge | Meta, Hugging Face | March 30, 2026 | General intelligence |

---

## Quick Reference

### Essential Commands

```bash
# Pull and run green agent
docker pull ghcr.io/qte77/agentbeats-greenagent:latest
docker run -p 9009:9009 ghcr.io/qte77/agentbeats-greenagent:latest

# Test AgentCard
curl http://localhost:9009/.well-known/agent-card.json

# Local development
uv venv && source .venv/bin/activate
uv sync
uv run pytest

# Build Docker images
docker build -f Dockerfile.green -t green-agent:local .
docker build -f Dockerfile.purple -t purple-agent:local .

# Push to GHCR
echo $CR_PAT | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
docker tag green-agent:local ghcr.io/$GITHUB_USERNAME/green-agent:latest
docker push ghcr.io/$GITHUB_USERNAME/green-agent:latest
```

### Important Dates

| Date | Event |
|------|-------|
| Oct 16, 2025 | Participant registration opens |
| Oct 24, 2025 | Team signup & Build Phase 1 |
| **Jan 31, 2026** | **Green agent submission deadline** |
| Feb 1, 2026 | Green agent judging |
| Feb 16, 2026 | Phase 2: Build purple agents |
| March 30, 2026 | Purple agent submission |
| March 31, 2026 | Purple agent judging |

---

## Updates & Changelog

### Document History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-31 | 2.0 | Consolidated from AGENTBEATS_REGISTRATION.md + SUBMISSION-GUIDE.md |
| 2025-12-15 | 1.0 | Initial resource collection |

---

## See Also

- [Competition Alignment Analysis](COMPETITION-ALIGNMENT.md)
- [Current Limitations & Scope](LIMITATIONS.md)
- [Submission Checklist](SUBMISSION-GUIDE.md)
- [AgentBeats Registration Guide](AGENTBEATS_REGISTRATION.md)
