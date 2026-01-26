# Documentation Index

**Project**: Graph-Based Multi-Agent Coordination Benchmark

---

## Quick Navigation

### Start Here
1. **[UserStory.md](UserStory.md)** - Product vision, problem statement, value proposition
2. **[DOMAIN_FOCUS.md](DOMAIN_FOCUS.md)** - Project scope (graph coordination only)
3. **[PRD.md](PRD.md)** - Technical requirements and story breakdown

### Implementation
4. **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** - Detailed patterns, phase gates, validation gates
5. **[AgentBeats/QUICKSTART.md](AgentBeats/QUICKSTART.md)** - Get running in 5 minutes (commands only)

### Platform Integration
6. **[AgentBeats/AGENTBEATS_REGISTRATION.md](AgentBeats/AGENTBEATS_REGISTRATION.md)** - Platform registration process

### Reference
7. **[AgentBeats/RESOURCES.md](AgentBeats/RESOURCES.md)** - External links, research papers
8. **[AgentBeats/CompetitionAnalysis.md](AgentBeats/CompetitionAnalysis.md)** - Competitive landscape

---

## Documentation Structure

```
docs/
├── README.md (THIS FILE)
├── UserStory.md (product vision, problem, value prop)
├── DOMAIN_FOCUS.md
├── PRD.md
├── IMPLEMENTATION_CHECKLIST.md (detailed patterns)
├── AgentBeats/
│   ├── QUICKSTART.md (5-minute setup commands)
│   ├── AGENTBEATS_REGISTRATION.md
│   ├── RESOURCES.md
│   └── CompetitionAnalysis.md
└── best-practices/
    └── python-best-practices.md
```

---

## What Changed (2026-01-26 Consolidation)

### New Files
- **QUICKSTART.md** - Minimal 5-minute setup (79 lines, commands only)
- **IMPLEMENTATION_CHECKLIST.md** - Detailed patterns moved here (A2A, Docker, server entry point)

### Archived Files
Moved to `_archive/docs/` to reduce redundancy:
- **A2A-Extension-Integration.md** → Patterns moved to IMPLEMENTATION_CHECKLIST.md
- **Local-Testing-and-Deployment.md** → Commands moved to QUICKSTART.md
- **AgentBeats-Research.md** → Outdated competition context
- **AgentBeats-Benchmark-Design-Principles.md** → Outdated competition context
- **DOCUMENTATION_SUMMARY.md** → Meta-documentation
- **GAP_ANALYSIS.md** → Deleted (redundant)

### Principles Applied
- **KISS**: Minimal quickstart (79 lines) + detailed checklist for implementation
- **DRY**: Eliminated redundant patterns (A2A appeared in 3 files → now in 1)
- **YAGNI**: Removed GitHub Actions YAML, GHCR manual steps (see AGENTBEATS_REGISTRATION.md instead)

---

## Development Workflow

```bash
# 1. Get running fast
Read: AgentBeats/QUICKSTART.md (5-minute setup)

# 2. Understand the vision
Read: UserStory.md → DOMAIN_FOCUS.md → PRD.md

# 3. Implement features
Read: IMPLEMENTATION_CHECKLIST.md (detailed patterns, phase gates)

# 4. Deploy to platform
Read: AgentBeats/AGENTBEATS_REGISTRATION.md (GHCR + registration)
```

---

## Quick Reference

- **Get started fast?**: See QUICKSTART.md (5-minute setup)
- **What is GraphJudge?**: See UserStory.md (problem, value proposition)
- **What's in scope?**: See DOMAIN_FOCUS.md (graph coordination only)
- **Technical requirements?**: See PRD.md (features, acceptance criteria)
- **Implementation patterns?**: See IMPLEMENTATION_CHECKLIST.md (A2A, Docker, server)
- **Deploy to platform?**: See AGENTBEATS_REGISTRATION.md (GHCR + registration)
