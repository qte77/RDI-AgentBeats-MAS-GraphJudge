# Documentation Index

**Project**: Graph-Based Multi-Agent Coordination Benchmark

---

## Quick Navigation

### Start Here

1. **[AgentBeats/ABSTRACT.md](AgentBeats/ABSTRACT.md)** - TL;DR: USP and value proposition

#### Green Agent (Assessor)
2. **[GreenAgent-UserStory.md](GreenAgent-UserStory.md)** - Product vision, problem statement, scope
3. **[GreenAgent-PRD.md](GreenAgent-PRD.md)** - Technical requirements and story breakdown

#### Purple Agent (Baseline Participant)
4. **[PurpleAgent-UserStory.md](PurpleAgent-UserStory.md)** - Vision for baseline test fixture
5. **[PurpleAgent-PRD.md](PurpleAgent-PRD.md)** - Technical requirements for baseline agent

### Implementation

1. **[AgentBeats/QUICKSTART.md](AgentBeats/QUICKSTART.md)** - Get running in 5 minutes

### Platform Integration & Competition

1. **[AgentBeats/COMPETITION-ALIGNMENT.md](AgentBeats/COMPETITION-ALIGNMENT.md)** - Competition alignment analysis (97% aligned)
2. **[AgentBeats/SUBMISSION-GUIDE.md](AgentBeats/SUBMISSION-GUIDE.md)** - Phase 1 submission checklist
3. **[AgentBeats/AGENTBEATS_REGISTRATION.md](AgentBeats/AGENTBEATS_REGISTRATION.md)** - Platform registration process
4. **[AgentBeats/LIMITATIONS.md](AgentBeats/LIMITATIONS.md)** - Scope boundaries and deferred features

### Architecture

| Diagram | Focus |
|---------|-------|
| [ComponentDiagram.puml](arch_vis/ComponentDiagram.puml) | How is it composed? |
| [AgenticBenchArch.puml](arch_vis/AgenticBenchArch.puml) | How does evaluation work? |
| [TracingArchitecture.puml](arch_vis/TracingArchitecture.puml) | When do API calls happen? |

See [arch_vis/](arch_vis/) for PlantUML source files.

### Research & Design

1. **[research/MULTI_AGENT_TRACING.md](research/MULTI_AGENT_TRACING.md)** - Common module, tracing, plugin architecture (Feature 7)

### Reference

1. **[AgentBeats/RESOURCES.md](AgentBeats/RESOURCES.md)** - External links, tool docs

---

## Documentation Structure

```text
docs/
├── README.md (THIS FILE)
├── TODO.md (implementation roadmap)
├── GreenAgent-UserStory.md (Green Agent vision)
├── GreenAgent-PRD.md (Green Agent requirements)
├── PurpleAgent-UserStory.md (Purple Agent vision)
├── PurpleAgent-PRD.md (Purple Agent requirements)
├── AgentBeats/
│   ├── ABSTRACT.md (TL;DR)
│   ├── QUICKSTART.md (developer setup)
│   ├── COMPETITION-ALIGNMENT.md (alignment analysis)
│   ├── LIMITATIONS.md (scope boundaries)
│   ├── AGENTBEATS_REGISTRATION.md (registration guide)
│   ├── SUBMISSION-GUIDE.md (Phase 1 checklist)
│   ├── RESOURCES.md (external links)
│   ├── DEMO_VIDEO_SCRIPT.md (demo recording guide)
│   ├── output_schema.md (JSON output format)
│   ├── sample_output.json (example output)
│   └── scenario.toml (platform config)
├── research/
│   ├── MULTI_AGENT_TRACING.md (Feature 7 design)
│   └── trace-collection-strategy.md
├── best-practices/
│   ├── testing-strategy.md
│   ├── tdd-best-practices.md
│   └── bdd-best-practices.md
└── arch_vis/
    ├── ComponentDiagram.puml (how is it composed?)
    ├── AgenticBenchArch.puml (how does evaluation work?)
    └── TracingArchitecture.puml (when do API calls happen?)
```

---

## Development Workflow

```bash
# 1. Get running fast
Read: AgentBeats/QUICKSTART.md

# 2. Understand the vision
Read: GreenAgent-UserStory.md → GreenAgent-PRD.md

# 3. Check competition alignment
Read: AgentBeats/COMPETITION-ALIGNMENT.md

# 4. Deploy to platform
Read: AgentBeats/SUBMISSION-GUIDE.md
```

---

## Quick Reference

| Question | Document |
| ---------- | ---------- |
| TL;DR? | AgentBeats/ABSTRACT.md |
| Competition aligned? | AgentBeats/COMPETITION-ALIGNMENT.md |
| What's out of scope? | AgentBeats/LIMITATIONS.md |
| Green Agent vision? | GreenAgent-UserStory.md |
| Green Agent requirements? | GreenAgent-PRD.md |
| Purple Agent vision? | PurpleAgent-UserStory.md |
| Purple Agent requirements? | PurpleAgent-PRD.md |
| Get started? | AgentBeats/QUICKSTART.md |
| Architecture? | arch_vis/*.puml |
| Deploy? | AgentBeats/AGENTBEATS_REGISTRATION.md |
| Submit? | AgentBeats/SUBMISSION-GUIDE.md |
| Tracing/plugins? | research/MULTI_AGENT_TRACING.md |
| TODOs? | TODO.md |

---

## Project TODOs

See **[TODO.md](TODO.md)** for implementation roadmap, open design decisions, and pending tasks.
