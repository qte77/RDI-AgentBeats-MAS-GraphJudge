#!/bin/bash
#
# Unified test script for GraphJudge agents
#
# Usage (from repo root):
#   ./e2e_test.sh                    # Quick test (default)
#   ./e2e_test.sh quick              # Quick test
#   ./e2e_test.sh comprehensive      # Full test
#   ./e2e_test.sh --build            # Quick test with rebuild
#   ./e2e_test.sh comprehensive --build
#
# Environment variables:
#   E2E_MODE=quick|comprehensive  # Test mode (default: quick)
#   E2E_BUILD=1                   # Force container rebuild
#
# Prerequisites:
#   - Docker and docker-compose installed
#   - Ports 9009 (green) and 9010 (purple) available
#

set -e

# Docker Compose configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose-local.yaml}"

# Defaults from environment
TEST_MODE="${E2E_MODE:-quick}"
BUILD_FLAG=""
[[ "${E2E_BUILD:-0}" == "1" ]] && BUILD_FLAG="--build"

# Parse command line arguments
for arg in "$@"; do
  case "$arg" in
    quick|--quick)
      TEST_MODE="quick"
      ;;
    comprehensive|--comprehensive|full|--full)
      TEST_MODE="comprehensive"
      ;;
    --build)
      BUILD_FLAG="--build"
      ;;
    --help|-h)
      echo "Usage: $0 [MODE] [OPTIONS]"
      echo ""
      echo "Modes:"
      echo "  quick (default)    : Quick smoke test"
      echo "  comprehensive/full : Full test with ground truth"
      echo ""
      echo "Options:"
      echo "  --build : Rebuild containers before testing"
      echo ""
      echo "Environment variables:"
      echo "  E2E_MODE=quick|comprehensive"
      echo "  E2E_BUILD=1"
      exit 0
      ;;
  esac
done

# Setup logging
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ "$TEST_MODE" = "quick" ]; then
  LOG_DIR="logs/e2e_quick_${TIMESTAMP}"
  TEST_LABEL="End-to-End Agent Test (Quick)"
else
  LOG_DIR="logs/e2e_full_${TIMESTAMP}"
  TEST_LABEL="Comprehensive E2E Test with Ground Truth"
fi
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "$TEST_LABEL"
echo "=========================================="
echo "Mode: $TEST_MODE"
echo "Logs: $LOG_DIR"
if [ "$TEST_MODE" = "comprehensive" ]; then
  echo "Traces: mocked (from ground_truth interaction patterns)"
  echo "Dataset size: $(jq '.scenarios | length' data/ground_truth.json)"
else
  echo "Traces: real (via Purple agent communication)"
fi
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track test failures
FAILED_TESTS=0

pass() { echo -e "${GREEN}✓ $1${NC}"; echo "PASS: $1" >> "$LOG_DIR/summary.log"; }
fail() { echo -e "${RED}✗ $1${NC}"; echo "FAIL: $1" >> "$LOG_DIR/summary.log"; FAILED_TESTS=$((FAILED_TESTS + 1)); }
info() { echo -e "${YELLOW}ℹ $1${NC}"; echo "INFO: $1" >> "$LOG_DIR/summary.log"; }

# ============================================================================
# COMMON: Start containers and validate
# ============================================================================

echo "Step 1: Starting containers..."
docker-compose --env-file /dev/null -f "$COMPOSE_FILE" up -d $BUILD_FLAG

# Wait for containers to be healthy
echo "Waiting for agents to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:9009/.well-known/agent-card.json > /dev/null 2>&1 && \
     curl -s http://localhost:9010/.well-known/agent-card.json > /dev/null 2>&1; then
    break
  fi
  sleep 1
done

if [ "$TEST_MODE" = "quick" ]; then
  # Quick mode: basic checks
  echo ""
  echo "Step 2: Checking containers..."
  if docker-compose --env-file /dev/null -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    pass "Containers running"
  else
    fail "Containers not running"
  fi

  # Step 3: Test Purple AgentCard
  echo ""
  echo "Step 3: Testing Purple AgentCard..."
  PURPLE_CARD=$(curl -s http://localhost:9010/.well-known/agent-card.json)
  echo "$PURPLE_CARD" > "$LOG_DIR/purple_agent_card.json"
  if echo "$PURPLE_CARD" | grep -q "Purple Agent"; then
    pass "Purple AgentCard OK"
  else
    fail "Purple AgentCard failed"
  fi

  # Step 4: Test Green AgentCard
  echo ""
  echo "Step 4: Testing Green AgentCard..."
  GREEN_CARD=$(curl -s http://localhost:9009/.well-known/agent-card.json)
  echo "$GREEN_CARD" > "$LOG_DIR/green_agent_card.json"
  if echo "$GREEN_CARD" | grep -q "Green Agent"; then
    pass "Green AgentCard OK"
  else
    fail "Green AgentCard failed"
  fi

  # Step 5: Test Purple task handling
  echo ""
  echo "Step 5: Testing Purple Agent (task handling)..."
  PURPLE_RESPONSE=$(curl -s -X POST http://localhost:9010/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"task":{"description":"Generate a test response"}}}')
  echo "$PURPLE_RESPONSE" > "$LOG_DIR/purple_response.json"

  if echo "$PURPLE_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'result' in d and d.get('error') is None else 1)" 2>/dev/null; then
    pass "Purple Agent responded to task"
  else
    fail "Purple Agent failed to respond"
  fi

  # Step 6: Test Green task handling
  echo ""
  echo "Step 6: Testing Green Agent (task handling)..."
  GREEN_RESPONSE_1=$(curl -s -X POST http://localhost:9009/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":"2","method":"message/send","params":{"task":{"description":"Evaluate test task 1"}}}')
  echo "$GREEN_RESPONSE_1" > "$LOG_DIR/green_response_1.json"

  if echo "$GREEN_RESPONSE_1" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'result' in d and d.get('error') is None else 1)" 2>/dev/null; then
    pass "Green Agent responded to task 1"
  else
    fail "Green Agent failed to respond to task 1"
  fi

  # Step 7: Test Green second task
  echo ""
  echo "Step 7: Testing Green Agent (second task)..."
  GREEN_RESPONSE_2=$(curl -s -X POST http://localhost:9009/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":"3","method":"message/send","params":{"task":{"description":"Evaluate test task 2"}}}')
  echo "$GREEN_RESPONSE_2" > "$LOG_DIR/green_response_2.json"

  if echo "$GREEN_RESPONSE_2" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'result' in d and d.get('error') is None else 1)" 2>/dev/null; then
    pass "Green Agent responded to task 2"
  else
    fail "Green Agent failed to respond to task 2"
  fi

  # Step 8: Validate JSON-RPC response structure
  echo ""
  echo "Step 8: Validating response structure..."

  if echo "$GREEN_RESPONSE_1" | python3 -c "
import sys, json
d = json.load(sys.stdin)
# Check for valid JSON-RPC response structure
required = ['jsonrpc', 'id', 'result']
exit(0 if all(k in d for k in required) else 1)
" 2>/dev/null; then
    pass "Response has valid JSON-RPC structure"
  else
    fail "Response missing required JSON-RPC fields"
  fi

  # Step 9: Test Summary
  echo ""
  echo "Step 9: Summary..."
  echo "----------------------------------------"

  # Save test summary
  python3 -c "
import json
from datetime import datetime

results = {
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'test_mode': 'quick',
    'agents': {
        'green': 'localhost:9009',
        'purple': 'localhost:9010'
    },
    'tests_run': 8,
    'status': 'completed'
}

print(json.dumps(results, indent=2))
" > "$LOG_DIR/results.json" 2>/dev/null

  echo "Test results saved to $LOG_DIR/results.json"

  if [ $FAILED_TESTS -gt 0 ]; then
    EXIT_CODE=1
  else
    EXIT_CODE=0
  fi

else
  # ========================================================================
  # COMPREHENSIVE: Test all narratives
  # ========================================================================

  pass "Containers ready"
  echo ""

  # Step 2: Test all narratives
  echo "Step 2: Testing all narratives..."
  echo "========================================"
  echo ""

  # Initialize counters
  TOTAL=0
  CORRECT_CLASS=0
  INCORRECT_CLASS=0

  # Process each scenario from ground truth
  jq -c '.scenarios[] | {index: .id, quality: .expected_metrics.coordination_quality, task: .task_description, pattern: .interaction_pattern}' data/ground_truth.json | while read -r test_case; do
    INDEX=$(echo "$test_case" | jq -r '.index')
    EXPECTED_CLASS=$(echo "$test_case" | jq -r '.quality')
    EXPECTED_SCORE=$(echo "$test_case" | jq -r '.quality')
    NARRATIVE=$(echo "$test_case" | jq -r '.task')
    PATTERN=$(echo "$test_case" | jq -c '.pattern')

    echo "Testing $INDEX: $EXPECTED_CLASS (expected score: $EXPECTED_SCORE)..."

    # Call Green Agent with interaction pattern for evaluation
    RESPONSE=$(curl -s -X POST http://localhost:9009/ \
      -H "Content-Type: application/json" \
      -d "{\"jsonrpc\":\"2.0\",\"id\":\"$INDEX\",\"method\":\"message/send\",\"params\":{\"task\":{\"description\":\"$NARRATIVE\",\"interaction_pattern\":$PATTERN}}}")

    # Save response
    echo "$RESPONSE" > "$LOG_DIR/${INDEX}_response.json"

    # Extract classification
    ACTUAL_CLASS=$(echo "$RESPONSE" | jq -r '.result.parts[0].data.classification' 2>/dev/null || echo "ERROR")
    ACTUAL_SCORE=$(echo "$RESPONSE" | jq -r '.result.parts[0].data.overall_score' 2>/dev/null || echo "ERROR")

    # Check if classification matches
    if [ "$ACTUAL_CLASS" = "$EXPECTED_CLASS" ]; then
      pass "$INDEX: Classification correct ($ACTUAL_CLASS)"
      CORRECT_CLASS=$((CORRECT_CLASS + 1))
    else
      fail "$INDEX: Classification mismatch - expected $EXPECTED_CLASS, got $ACTUAL_CLASS"
      INCORRECT_CLASS=$((INCORRECT_CLASS + 1))
    fi

    TOTAL=$((TOTAL + 1))

    # Show scores
    if [ "$ACTUAL_SCORE" != "ERROR" ]; then
      info "$INDEX: Score $ACTUAL_SCORE (expected ~$EXPECTED_SCORE)"
    fi

    echo ""
  done

  # Step 3: Summary
  echo "=========================================="
  echo "Test Summary"
  echo "=========================================="
  echo ""
  echo "Total tests: $TOTAL"
  echo "Classification accuracy: $CORRECT_CLASS/$TOTAL correct"
  if [ "$TOTAL" -gt 0 ]; then
    ACCURACY=$(awk "BEGIN {printf \"%.1f\", ($CORRECT_CLASS * 100) / $TOTAL}")
  else
    ACCURACY="0.0"
  fi
  echo "Accuracy: ${ACCURACY}%"
  echo ""

  if [ "$ACCURACY" = "100.0" ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    EXIT_CODE=0
  else
    echo -e "${YELLOW}⚠ Some tests failed (${ACCURACY}% accuracy)${NC}"
    EXIT_CODE=1
  fi

  # Generate comprehensive report
  python3 << 'PYTHON_EOF'
import json
from datetime import datetime
import glob
import os

log_dir = os.environ.get('LOG_DIR', 'logs')

# Collect all test results
results = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "total_tests": 0,
    "correct_classifications": 0,
    "incorrect_classifications": 0,
    "tests": []
}

# Load ground truth for reference
with open("data/ground_truth.json") as f:
    data = json.load(f)
    ground_truth = {item["id"]: item for item in data.get("scenarios", [])}

# Process each response
for response_file in sorted(glob.glob(f"{log_dir}/*_response.json")):
    test_id = response_file.split("/")[-1].split("_")[0]

    try:
        with open(response_file) as f:
            response = json.load(f)

        actual_class = response.get("result", {}).get("parts", [{}])[0].get("data", {}).get("classification", "ERROR")
        actual_score = response.get("result", {}).get("parts", [{}])[0].get("data", {}).get("overall_score", None)

        expected = ground_truth.get(test_id, {})
        expected_class = expected.get("expected_metrics", {}).get("coordination_quality", "UNKNOWN")

        results["total_tests"] += 1
        if actual_class == expected_class:
            results["correct_classifications"] += 1
        else:
            results["incorrect_classifications"] += 1

        results["tests"].append({
            "id": test_id,
            "expected_classification": expected_class,
            "actual_classification": actual_class,
            "match": actual_class == expected_class,
            "actual_score": actual_score,
            "expected_score": expected.get("expected_score")
        })
    except Exception as e:
        print(f"Error processing {response_file}: {e}")

# Calculate accuracy
if results["total_tests"] > 0:
    results["accuracy"] = (results["correct_classifications"] / results["total_tests"]) * 100

# Save report
with open(f"{log_dir}/comprehensive_report.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
PYTHON_EOF

fi

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}All tests passed!${NC}"
else
  echo -e "${YELLOW}Some tests failed${NC}"
fi
echo "=========================================="
echo ""
echo "Logs saved to: $LOG_DIR"
ls -lh "$LOG_DIR"

# Optional: Stop containers
echo ""
read -p "Stop containers? (y/N): " STOP
if [ "$STOP" = "y" ] || [ "$STOP" = "Y" ]; then
  docker-compose --env-file /dev/null -f "$COMPOSE_FILE" down
  echo "Containers stopped."
fi

exit $EXIT_CODE
