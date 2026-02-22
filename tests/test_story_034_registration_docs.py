"""STORY-034: Tests for docs/AgentBeats/AGENTBEATS_REGISTRATION.md existence and completeness."""

from pathlib import Path

REGISTRATION_MD = (
    Path(__file__).parent.parent / "docs" / "AgentBeats" / "AGENTBEATS_REGISTRATION.md"
)


def test_registration_md_exists():
    """Acceptance: docs/AgentBeats/AGENTBEATS_REGISTRATION.md must be created."""
    assert REGISTRATION_MD.exists(), "docs/AgentBeats/AGENTBEATS_REGISTRATION.md must exist"


def test_registration_md_documents_base_evaluator():
    """Acceptance: Must document BaseEvaluator ABC interface with typed Python code example."""
    content = REGISTRATION_MD.read_text()
    assert "BaseEvaluator" in content, "Must document BaseEvaluator ABC"
    assert "abstractmethod" in content or "ABC" in content, "Must show abstract base class pattern"
    assert "async def evaluate" in content, "Must show typed evaluate() method signature"
    assert "InteractionStep" in content, "Must reference InteractionStep in typed example"


def test_registration_md_documents_tier_system():
    """Acceptance: Must document tier-based structure: Tier 1, Tier 2, Tier 3."""
    content = REGISTRATION_MD.read_text()
    assert "Tier 1" in content, "Must document Tier 1 (Graph/structural)"
    assert "Tier 2" in content, "Must document Tier 2 (LLM + Latency)"
    assert "Tier 3" in content, "Must document Tier 3 (custom plugins)"


def test_registration_md_documents_tier1_graph_structural():
    """Acceptance: Tier 1 must reference Graph/structural analysis."""
    content = REGISTRATION_MD.read_text()
    tier1_keywords = ["graph", "structural", "Graph"]
    assert any(kw in content for kw in tier1_keywords), (
        "Tier 1 must describe graph/structural analysis"
    )


def test_registration_md_documents_tier2_llm_latency():
    """Acceptance: Tier 2 must reference LLM and Latency."""
    content = REGISTRATION_MD.read_text()
    assert "LLM" in content or "llm" in content.lower(), "Tier 2 must mention LLM judge"
    assert "latency" in content.lower() or "Latency" in content, "Tier 2 must mention Latency"


def test_registration_md_documents_graph_metric_plugin():
    """Acceptance: Must document GraphMetricPlugin ABC as second-level extension point."""
    content = REGISTRATION_MD.read_text()
    assert "GraphMetricPlugin" in content, "Must document GraphMetricPlugin ABC"
    assert "register_plugin" in content, "Must document register_plugin() method"
    assert "compute" in content, "Must show compute() abstract method"


def test_registration_md_has_step_by_step_guide():
    """Acceptance: Must have step-by-step guide with evaluate() and executor wiring."""
    content = REGISTRATION_MD.read_text()
    # Should have numbered steps or an explicit step-by-step section
    has_steps = (
        "Step 1" in content
        or "step 1" in content.lower()
        or "## Step" in content
        or "1." in content
    )
    assert has_steps, "Must include step-by-step guide"
    assert "evaluate()" in content or "evaluate(" in content, "Must reference evaluate() method"
    assert "evaluate_all" in content, "Must reference Executor.evaluate_all() registration point"


def test_registration_md_references_file_paths():
    """Acceptance: Integration points must be described with file paths."""
    content = REGISTRATION_MD.read_text()
    assert "src/green/evals/" in content, "Must reference src/green/evals/ file path"
    assert "src/green/executor.py" in content, "Must reference src/green/executor.py"


def test_registration_md_has_text_evaluator_example():
    """Acceptance: TextEvaluator (Tier 3) must be shown as worked example."""
    content = REGISTRATION_MD.read_text()
    assert "TextEvaluator" in content, "Must show TextEvaluator as worked example"


def test_registration_md_has_code_examples():
    """Acceptance: Code examples must be copy-paste accurate (no pseudocode)."""
    content = REGISTRATION_MD.read_text()
    # Must have fenced Python code blocks
    assert "```python" in content, "Must include Python code blocks"
    # Must have real imports, not pseudocode
    assert "from abc import" in content or "import ABC" in content or "from abc" in content, (
        "Code examples must show real imports"
    )


def test_registration_md_documents_graph_metric_plugin_workflow():
    """Acceptance: GraphMetricPlugin workflow must be documented with DiGraph reference."""
    content = REGISTRATION_MD.read_text()
    assert "DiGraph" in content or "nx.DiGraph" in content, (
        "Must reference nx.DiGraph in GraphMetricPlugin example"
    )
    assert "GraphEvaluator" in content, "Must reference GraphEvaluator"
