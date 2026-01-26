# MAS-GraphJudge 

> Measure how, not just whether

A GreenAgent for [AgentBeats competition](https://rdi.berkeley.edu/agentx-agentbeats.html)
that evaluates **how agents coordinate**, not just whether they succeed.

![Version](https://img.shields.io/badge/version-0.0.0-58f4c2.svg)
[![License](https://img.shields.io/badge/license-BSD3Clause-58f4c2.svg)](LICENSE.md)
[![CodeQL](https://github.com/qte77/RDI-AgentX-AgentBeats-CompetitionRDI-AgentX-AgentBeats-GraphJudge/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/qte77/RDI-AgentX-AgentBeats-CompetitionRDI-AgentX-AgentBeats-GraphJudge/actions/workflows/github-code-scanning/codeql)
[![CodeFactor](https://www.codefactor.io/repository/github/qte77/RDI-AgentX-AgentBeats-CompetitionRDI-AgentX-AgentBeats-GraphJudge/badge)](https://www.codefactor.io/repository/github/qte77/RDI-AgentX-AgentBeats-CompetitionRDI-AgentX-AgentBeats-GraphJudge)
[![ruff](https://github.com/qte77/RDI-AgentX-AgentBeats-CompetitionRDI-AgentX-AgentBeats-GraphJudge/actions/workflows/ruff.yaml/badge.svg)](https://github.com/qte77/RDI-AgentX-AgentBeats-CompetitionRDI-AgentX-AgentBeats-GraphJudge/actions/workflows/ruff.yaml)
[![pytest](https://github.com/qte77/RDI-AgentX-AgentBeats-CompetitionRDI-AgentX-AgentBeats-GraphJudge/actions/workflows/pytest.yaml/badge.svg)](https://github.com/qte77/RDI-AgentX-AgentBeats-CompetitionRDI-AgentX-AgentBeats-GraphJudge/actions/workflows/pytest.yaml)

## Novel Value

Graph-based runtime coordination analysis - measuring collaboration quality
through NetworkX metrics and LLM-as-judge evaluation.

## Evaluation Tiers

| Tier | Type      | Description                                   |
| ---- | --------- | --------------------------------------------- |
| 1    | Graph     | NetworkX metrics (centrality, efficiency)     |
| 2    | LLM-Judge | Coordination quality assessment               |
| 3    | Text      | Similarity metrics (plugin for PeerRead)      |

## Architecture

![Agentic Graph Benchmark Architecture](assets/AgenticBenchArch.png)

## Submission

### Competition Tracks

- Research Agent
- Multi-Agent
- AAA (Agentified Agent Assessment)

### Abstract

GreenAgent is a novel evaluation framework that measures **how agents
coordinate**, not just whether they succeed. The system combines graph-based
structural analysis (NetworkX metrics), LLM-as-judge assessment, and text
similarity scoring to provide comprehensive multi-tier evaluation of agent
coordination quality. Through A2A-compliant trace capture and directed graph
analysis, GreenAgent reveals coordination patterns, bottlenecks, and
collaboration effectiveness. We demonstrate perfect reproducibility (0%
variance) across metrics in independent evaluation runs, enabling fair and
consistent assessment of multi-agent systems.

Full abstract: [docs/ABSTRACT.md](docs/ABSTRACT.md)

### Demo Video

**Video URL**: [To be added - demo video showing agent startup, evaluation
flow, and results interpretation]

The demo video (max 3 minutes) demonstrates:

- GreenAgent server startup and A2A endpoint verification
- Purple agent evaluation flow with trace capture
- Multi-tier evaluation results (graph metrics, LLM judge, text similarity)
- Result interpretation and leaderboard integration
- See [Demo Video Script](./docs/DEMO_VIDEO_SCRIPT.md)

## Roadmap

- ✅ Phase 1: A2A + Graph + Basic eval (current)
- 🔜 Phase 2 (outlook): ART training on traces, potentially using
  [WeightWatcher](https://github.com/calculatedcontent/weightwatcher) or
  [PerforatedAI](https://github.com/PerforatedAI/PerforatedAI)
- 🔮 Phase 3 (outlook): Self-evolving GreenAgent, e.g.,
  [DGM](https://arxiv.org/abs/2410.04444)

**Note**: Time constraints limited full implementation of advanced features
planned in Phase 2 and 3. Current release focuses on core graph-based
evaluation with proven reproducibility.

## Quick Start

### Run from GHCR (no build needed)

```bash
# Pull and run GraphJudge container
docker pull ghcr.io/qte77/agentbeats-greenagent:latest
docker run -p 9009:9009 ghcr.io/qte77/agentbeats-greenagent:latest

# Test (new terminal)
curl localhost:9009/.well-known/agent.json
