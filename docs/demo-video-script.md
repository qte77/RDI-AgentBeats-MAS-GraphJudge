# Green Agent Demo Video Script

**Duration:** ~3 minutes
**Target Audience:** Developers, AI researchers, multi-agent system architects

---

## Introduction (0:00 - 0:30)

### Narration
"Welcome to the Green Agent demonstration. Green Agent is a multi-agent coordination quality evaluator that uses graph analysis, LLM assessment, and latency metrics to provide comprehensive evaluation of agent-to-agent collaboration. In this demo, we'll show you how Green Agent analyzes coordination patterns in real-time using the A2A protocol."

### Screen Actions
- Show title card: "Green Agent - Multi-Agent Coordination Evaluator"
- Display architecture diagram showing Green Agent's three-tier evaluation system
- Highlight key features: Graph Analysis, LLM Judge, Latency Metrics

### Timing Cues
- 0:00-0:10: Title card with smooth fade-in
- 0:10-0:30: Architecture overview with animated components

---

## Scene 1: Server Startup and A2A Endpoint Verification (0:30 - 1:00)

### Narration
"Let's start Green Agent. The server starts on port 9009 and immediately exposes its Agent Card, which is the standard way A2A-compliant agents advertise their capabilities. Notice the AgentCard declares support for the A2A Traceability Extension and Timestamp Extension - these enable precise coordination tracking."

### Screen Actions
1. Open terminal window
2. Execute command:
   ```bash
   uv run python -m green.server --host 0.0.0.0 --port 9009
   ```
3. Show server startup logs with INFO messages
4. Open browser or use curl to access AgentCard endpoint:
   ```bash
   curl http://localhost:9009/.well-known/agent-card.json | jq
   ```
5. Display formatted AgentCard JSON showing:
   - Agent ID: "green-agent"
   - Name: "Green Agent (Assessor)"
   - Extensions: traceability, timestamp
   - Endpoints: /health, A2A JSON-RPC endpoint

### Timing Cues
- 0:30-0:40: Terminal command execution
- 0:40-0:50: AgentCard retrieval and display
- 0:50-1:00: Highlight extension support in the JSON

---

## Scene 2: Evaluation Flow with Trace Capture (1:00 - 2:00)

### Narration
"Now we'll send an evaluation task to Green Agent. The agent receives a coordination task description via A2A JSON-RPC 2.0 protocol. Watch as Green Agent sends messages to the target agents, captures interaction traces with microsecond-precision timestamps, and measures latency automatically using the A2A Traceability Extension."

### Screen Actions
1. Show terminal with JSON-RPC request payload:
   ```json
   {
     "jsonrpc": "2.0",
     "method": "tasks.send",
     "params": {
       "task": {
         "description": "Evaluate coordination quality of the Purple Agent network"
       }
     },
     "id": "eval-001"
   }
   ```
2. Execute request using curl or Python script:
   ```bash
   curl -X POST http://localhost:9009/ \
     -H "Content-Type: application/json" \
     -d @evaluation_request.json
   ```
3. Split screen showing:
   - Left: Green Agent logs showing trace collection
   - Right: Purple Agent network responding to messages
4. Highlight log entries showing:
   - Messenger connecting to agents
   - Interaction steps being recorded
   - Trace IDs and step IDs being generated
   - Latency measurements (in milliseconds)

### Timing Cues
- 1:00-1:15: Display request payload
- 1:15-1:30: Execute request and show initial response
- 1:30-1:50: Split screen showing coordinated agent interaction
- 1:50-2:00: Close-up on trace collection logs

---

## Scene 3: Multi-Tier Results Display (2:00 - 2:50)

### Narration
"Green Agent processes the traces through three evaluation tiers. Tier 1 performs graph-based structural analysis - computing centrality metrics, identifying bottlenecks, and detecting isolated agents. Tier 2 combines LLM-based semantic assessment with latency performance metrics. The LLM Judge analyzes coordination quality, providing reasoning and identifying strengths and weaknesses. All results are written to the output directory following the AgentBeats leaderboard standard."

### Screen Actions
1. Show results file being written:
   ```bash
   cat output/results.json | jq
   ```
2. Display structured results with three sections highlighted:

   **Tier 1 - Graph Metrics:**
   ```json
   {
     "tier1_graph": {
       "degree_centrality": {"agent-1": 0.75, "agent-2": 0.50},
       "betweenness_centrality": {"agent-1": 0.60, "agent-2": 0.20},
       "graph_density": 0.45,
       "bottlenecks": ["agent-1"],
       "isolated_agents": [],
       "over_centralized": false
     }
   }
   ```

   **Tier 2 - LLM Judge:**
   ```json
   {
     "tier2_llm": {
       "overall_score": 0.75,
       "reasoning": "Agents demonstrated good coordination with efficient task delegation...",
       "coordination_quality": "high",
       "strengths": ["Fast response times", "Clear delegation"],
       "weaknesses": ["Single point of bottleneck at agent-1"]
     }
   }
   ```

   **Tier 2 - Latency Metrics:**
   ```json
   {
     "tier2_latency": {
       "avg_latency_ms": 145.3,
       "p50_latency_ms": 120,
       "p95_latency_ms": 280,
       "p99_latency_ms": 320,
       "slowest_agent": "agent-2"
     }
   }
   ```

3. Zoom in on each tier sequentially with visual highlights

### Timing Cues
- 2:00-2:15: Show results file output
- 2:15-2:30: Tier 1 graph metrics with visual annotations
- 2:30-2:40: Tier 2 LLM Judge assessment
- 2:40-2:50: Tier 2 latency performance metrics

---

## Conclusion (2:50 - 3:00)

### Narration
"Green Agent provides comprehensive, multi-dimensional evaluation of agent coordination quality. The combination of graph theory, LLM reasoning, and performance metrics gives you deep insights into how well your agents collaborate. Visit the GitHub repository to learn more and contribute to the project."

### Screen Actions
- Show GitHub repository URL: `github.com/rdi-berkeley/RDI-AgentX-AgentBeats-GraphJudge`
- Display key capabilities as bullet points:
  - ✓ A2A Protocol Compliant
  - ✓ Graph-Based Structural Analysis
  - ✓ LLM Semantic Assessment
  - ✓ Latency Performance Tracking
  - ✓ Extensible Evaluator Architecture
- Fade to end card with contact information

### Timing Cues
- 2:50-2:55: Capabilities summary
- 2:55-3:00: End card with fade-out

---

## Technical Notes for Video Production

### Required Assets
1. Terminal recording software (e.g., asciinema, terminalizer)
2. Browser or API client for HTTP requests
3. Running instances of:
   - Green Agent server (port 9009)
   - Purple Agent network (test fixtures)
4. Sample JSON request files
5. Syntax highlighting for JSON output

### Visual Style Guidelines
- Use monospace fonts for code and terminal output
- Apply syntax highlighting for JSON (green for strings, blue for numbers)
- Keep terminal text readable (minimum 14pt font)
- Use smooth transitions between scenes (0.5-1 second fades)
- Highlight key information with subtle overlays or arrows

### Audio Production
- Record narration in quiet environment with clear enunciation
- Normalize audio levels across all sections
- Add subtle background music (optional, low volume)
- Include captions/subtitles for accessibility

### Post-Production Checklist
- [ ] Verify all timing cues align with narration
- [ ] Check that all code/JSON is properly formatted and visible
- [ ] Ensure smooth transitions between scenes
- [ ] Add callouts/annotations where needed
- [ ] Test final video at 1080p resolution
- [ ] Export with high-quality codec (H.264 or H.265)
