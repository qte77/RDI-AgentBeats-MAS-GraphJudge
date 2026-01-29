---
title: BDD Best Practices
version: 1.0
based-on: Industry research 2025-2026
see-also: testing-strategy.md
---

## Behavior-Driven Development (BDD)

BDD focuses on defining expected system behavior through collaboration between technical and non-technical stakeholders using plain-language scenarios.

## The Three Pillars

```
┌─────────────────────────────────────────────────┐
│  1. DISCOVERY                                   │
│  Three Amigos: PO + Dev + Tester                │
│  Uncover examples early, reduce ambiguity       │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  2. FORMULATION                                 │
│  Given-When-Then scenarios                      │
│  Capture examples in business language          │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  3. AUTOMATION                                  │
│  Executable tests as living documentation       │
│  Integrate into CI/CD pipeline                  │
└─────────────────────────────────────────────────┘
```

## Pillar 1: Discovery (Three Amigos)

**Who**: Product Owner, Developer, Tester collaborate

**Goal**: Uncover concrete examples before implementation

**Process**:
1. Discuss feature/requirement
2. Ask "Can you give me an example?"
3. Explore edge cases through examples
4. Reach shared understanding

**Outcome**: Real examples that reduce late-stage rework

## Pillar 2: Formulation (Given-When-Then)

**Format**: Gherkin syntax for scenarios

```gherkin
Feature: Green Agent Evaluation
  As an AgentBeats judge
  I want to evaluate multi-agent coordination
  So that I can score team performance

  Scenario: Detect coordination bottleneck
    Given a hub-spoke coordination pattern
      And coordinator agent "green-hub"
      And worker agents "worker-1", "worker-2", "worker-3"
    When the evaluator analyzes interaction traces
    Then it should detect a bottleneck
      And "green-hub" should be identified as the bottleneck
```

**Structure**:
- **Given** - Context and preconditions
- **When** - Action or event
- **Then** - Expected outcome

## Pillar 3: Automation

**Implement scenarios as executable tests**:

```python
from pytest_bdd import scenario, given, when, then

@scenario('features/evaluation.feature', 'Detect coordination bottleneck')
def test_detect_bottleneck():
    pass

@given('a hub-spoke coordination pattern')
def hub_spoke_pattern():
    return build_hub_spoke_traces(hub="green-hub", spokes=["worker-1", "worker-2", "worker-3"])

@when('the evaluator analyzes interaction traces')
def analyze_traces(hub_spoke_pattern):
    return GraphEvaluator().evaluate(hub_spoke_pattern)

@then('it should detect a bottleneck')
def verify_bottleneck(analyze_traces):
    assert analyze_traces.has_bottleneck
```

**Benefits**:
- Living documentation that stays current
- Business-readable test reports
- Fast feedback on behavior changes

## Core BDD Practices

### 1. Collaboration First

**Shift focus from code to behavior**:
- Use plain-English descriptions
- All stakeholders can understand
- Align on requirements before implementation

**Three Amigos pattern**: PO defines "what", Dev designs "how", Tester asks "what about...?"

### 2. Scenario Quality

**Focus on business value**:
```gherkin
# GOOD - Business behavior
Scenario: Calculate coordination quality score
  Given interaction traces with balanced communication
  When the evaluator computes metrics
  Then the coordination quality should be "high"
```

**Avoid technical details**:
```gherkin
# BAD - Implementation details
Scenario: GraphEvaluator uses NetworkX
  Given a DiGraph instance
  When compute_metrics() is called
  Then it should return a dict with keys...
```

### 3. Declarative, Not Imperative

**Declarative** (what, not how):
```gherkin
# GOOD
Given a user is authenticated
When they request the dashboard
Then they should see their coordination scores
```

**Imperative** (step-by-step actions):
```gherkin
# BAD
Given the user opens the login page
  And enters "user@example.com" in the email field
  And enters "password123" in the password field
  And clicks the "Login" button
  And waits for the page to load
When they click on "Dashboard" in the navigation
Then they should see a table with columns...
```

### 4. One Scenario Per Behavior

```gherkin
# GOOD - Focused scenarios
Scenario: Detect bottleneck in hub-spoke pattern
Scenario: Calculate graph density metric
Scenario: Identify isolated agents

# BAD - Kitchen sink scenario
Scenario: Test all evaluator features
  Given various trace patterns
  When evaluator runs all metrics
  Then everything works
```

### 5. Maintain Scenarios

**Evolve with the application**:
- Revisit scenarios when requirements change
- Remove obsolete scenarios
- Prevent test suite bloat
- Keep scenarios aligned with business needs

## BDD Anti-Patterns

**Too technical**:
```gherkin
# BAD
Given the database has a record with id=123
When the API endpoint /api/v1/users/123 receives a GET request
Then the response JSON should have a "data" key
```

**Too many scenarios**:
- Keep scenarios focused
- Avoid testing every permutation
- Use Scenario Outlines for data variations

**Coupling to UI**:
```gherkin
# BAD - Brittle UI coupling
When I click the button with id "submit-btn"

# GOOD - Behavior focused
When I submit the evaluation request
```

## Combining TDD + BDD

**Complementary approaches**:

```
BDD Scenario (acceptance criteria)
    │
    ├─> TDD: Implement step definition
    ├─> TDD: Implement business logic
    └─> TDD: Implement data layer

Integration Test: BDD scenario passes
```

**Strategy**:
1. Write BDD scenario for feature acceptance
2. Use TDD to implement components
3. BDD scenario passes when feature complete

## Tools for BDD

**Python ecosystem**:
- **pytest-bdd** - Gherkin scenarios with pytest
- **behave** - Pure BDD framework
- **Cucumber** - Cross-language BDD (via behave-cucumber)

**This project**: Consider pytest-bdd for integration with existing pytest suite

## When to Use BDD

**Use BDD for**:
- User-facing features
- Acceptance criteria
- Cross-team communication
- Integration tests
- API contracts

**Consider alternatives for**:
- Unit tests (use TDD)
- Performance tests
- Infrastructure tests

## Integration with This Project

**Potential BDD scenarios**:
```gherkin
Feature: AgentBeats Evaluation Pipeline
  Scenario: Evaluate Green-Purple coordination
  Scenario: Generate AgentBeats output format
  Scenario: Handle A2A protocol messages

Feature: Graph Metrics Analysis
  Scenario: Detect communication bottlenecks
  Scenario: Calculate graph density
  Scenario: Identify isolated agents
```

Store scenarios in `tests/acceptance/features/`

## References

- [BDD Essential Guide 2026](https://monday.com/blog/rnd/behavior-driven-development/)
- [Effective Behavior-Driven Development](https://www.manning.com/books/effective-behavior-driven-development)
- [BDD Documentation - Cucumber.io](https://cucumber.io/docs/bdd/)
- [TDD vs BDD 2025 Comparison](https://medium.com/@sharmapraveen91/tdd-vs-bdd-vs-ddd-in-2025-choosing-the-right-approach-for-modern-software-development-6b0d3286601e)
