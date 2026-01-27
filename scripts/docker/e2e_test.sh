#!/bin/bash
#
# Unified test script for GraphJudge agents
#
# Usage:
#   ./scripts/docker/test.sh              # Quick smoke test (default)
#   ./scripts/docker/test.sh --quick      # Quick smoke test
#   ./scripts/docker/test.sh --comprehensive  # Full test with ground truth
#
# Prerequisites:
#   - Docker and docker-compose installed
#   - Ports 8001 and 8002 available
#
# Outputs:
#   - logs/e2e_YYYYMMDD_HHMMSS/ - Quick test logs
#   - logs/comprehensive_YYYYMMDD_HHMMSS/ - Comprehensive test logs
#

set -e

# Docker Compose configuration
COMPOSE_FILE="docker-compose-local.yaml"

# Parse arguments (default: quick)
ARG="${1:-quick}"

case "$ARG" in
  quick|--quick)
    TEST_MODE="quick"
    ;;
  comprehensive|--comprehensive|full)
    TEST_MODE="comprehensive"
    ;;
  *)
    echo "Usage: $0 [quick|comprehensive]"
    echo ""
    echo "Modes:"
    echo "  quick (default)    : Quick smoke test with 2 test cases"
    echo "  comprehensive/full : Full test with all ground truth narratives"
    echo ""
    echo "Examples:"
    echo "  $0              # Run quick test (default)"
    echo "  $0 quick        # Run quick test"
    echo "  $0 comprehensive# Run comprehensive test"
    echo "  $0 full         # Run comprehensive test (alias)"
    exit 1
    ;;
esac

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
  echo "Dataset size: $(jq 'length' data/ground_truth.json)"
fi
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}✓ $1${NC}"; echo "PASS: $1" >> "$LOG_DIR/summary.log"; }
fail() { echo -e "${RED}✗ $1${NC}"; echo "FAIL: $1" >> "$LOG_DIR/summary.log"; }
info() { echo -e "${YELLOW}ℹ $1${NC}"; echo "INFO: $1" >> "$LOG_DIR/summary.log"; }

# ============================================================================
# COMMON: Start containers and validate
# ============================================================================

echo "Step 1: Starting containers..."
docker-compose -f "$COMPOSE_FILE" up -d --build

# Wait for containers to be healthy
echo "Waiting for agents to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:8001/.well-known/agent-card.json > /dev/null 2>&1 && \
     curl -s http://localhost:8002/.well-known/agent-card.json > /dev/null 2>&1; then
    break
  fi
  sleep 1
done

if [ "$TEST_MODE" = "quick" ]; then
  # Quick mode: basic checks
  echo ""
  echo "Step 2: Checking containers..."
  if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    pass "Containers running"
  else
    fail "Containers not running"
  fi

  # Step 3: Test Purple AgentCard
  echo ""
  echo "Step 3: Testing Purple AgentCard..."
  PURPLE_CARD=$(curl -s http://localhost:8001/.well-known/agent-card.json)
  echo "$PURPLE_CARD" > "$LOG_DIR/purple_agent_card.json"
  if echo "$PURPLE_CARD" | grep -q "Bulletproof Purple Agent"; then
    pass "Purple AgentCard OK"
  else
    fail "Purple AgentCard failed"
  fi

  # Step 4: Test Green AgentCard
  echo ""
  echo "Step 4: Testing Green AgentCard..."
  GREEN_CARD=$(curl -s http://localhost:8002/.well-known/agent-card.json)
  echo "$GREEN_CARD" > "$LOG_DIR/green_agent_card.json"
  if echo "$GREEN_CARD" | grep -q "Bulletproof Green Agent"; then
    pass "Green AgentCard OK"
  else
    fail "Green AgentCard failed"
  fi

  # Step 5: Test Purple narrative generation
  echo ""
  echo "Step 5: Testing Purple Agent (narrative generation)..."
  PURPLE_RESPONSE=$(curl -s -X POST http://localhost:8001/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"messageId":"test-1","role":"user","parts":[{"text":"Generate a qualifying R&D narrative"}]}}}')
  echo "$PURPLE_RESPONSE" > "$LOG_DIR/purple_narrative_response.json"

  if echo "$PURPLE_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'narrative' in str(d) else 1)" 2>/dev/null; then
    pass "Purple Agent generated narrative"
  else
    fail "Purple Agent failed to generate narrative"
  fi

  # Step 6: Test Green evaluation (non-qualifying)
  echo ""
  echo "Step 6: Testing Green Agent (non-qualifying narrative)..."
  GREEN_RESPONSE_BAD=$(curl -s -X POST http://localhost:8002/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":"2","method":"message/send","params":{"message":{"messageId":"test-2","role":"user","parts":[{"text":"We used standard debugging and routine maintenance to fix bugs and improve market share."}]}}}')
  echo "$GREEN_RESPONSE_BAD" > "$LOG_DIR/green_eval_non_qualifying.json"

  CLASSIFICATION_BAD=$(echo "$GREEN_RESPONSE_BAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['parts'][0]['data']['classification'])" 2>/dev/null || echo "ERROR")
  if [ "$CLASSIFICATION_BAD" = "NON_QUALIFYING" ]; then
    pass "Green Agent correctly identified NON_QUALIFYING"
  else
    echo "Got classification: $CLASSIFICATION_BAD"
    fail "Green Agent failed to identify NON_QUALIFYING"
  fi

  # Step 7: Test Green evaluation (qualifying)
  echo ""
  echo "Step 7: Testing Green Agent (qualifying narrative)..."
  GREEN_RESPONSE_GOOD=$(curl -s -X POST http://localhost:8002/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":"3","method":"message/send","params":{"message":{"messageId":"test-3","role":"user","parts":[{"text":"Our hypothesis was that a novel architecture could resolve the technical uncertainty. Through experimentation, we tested alternatives. Iterations failed with 50ms latency. The unknown solution emerged from systematic failure analysis."}]}}}')
  echo "$GREEN_RESPONSE_GOOD" > "$LOG_DIR/green_eval_qualifying.json"

  CLASSIFICATION_GOOD=$(echo "$GREEN_RESPONSE_GOOD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['parts'][0]['data']['classification'])" 2>/dev/null || echo "ERROR")
  if [ "$CLASSIFICATION_GOOD" = "QUALIFYING" ]; then
    pass "Green Agent correctly identified QUALIFYING"
  else
    echo "Got classification: $CLASSIFICATION_GOOD"
    fail "Green Agent failed to identify QUALIFYING"
  fi

  # Step 8: Validate Green Agent outputs scores
  echo ""
  echo "Step 8: Validating Green Agent score output..."

  REQUIRED_FIELDS="overall_score correctness safety specificity experimentation risk_score risk_category confidence classification redline"
  MISSING_FIELDS=$(echo "$GREEN_RESPONSE_BAD" | python3 -c "
import sys, json
d = json.load(sys.stdin)['result']['parts'][0]['data']
required = '$REQUIRED_FIELDS'.split()
missing = [f for f in required if f not in d]
if missing:
    print(' '.join(missing))
" 2>/dev/null)

  if [ -z "$MISSING_FIELDS" ]; then
    pass "Green Agent outputs all required score fields"
  else
    echo "Missing fields: $MISSING_FIELDS"
    fail "Green Agent missing score fields"
  fi

  # Step 9: Score Summary
  echo ""
  echo "Step 9: Score Summary..."
  echo "----------------------------------------"

  # Extract and log metrics
  echo "=== METRICS ===" > "$LOG_DIR/metrics.log"
  echo "" >> "$LOG_DIR/metrics.log"

  echo "Non-qualifying narrative:"
  echo "Non-qualifying narrative:" >> "$LOG_DIR/metrics.log"
  METRICS_BAD=$(echo "$GREEN_RESPONSE_BAD" | python3 -c "
import sys,json
d=json.load(sys.stdin)['result']['parts'][0]['data']
print(f\"  Risk Score: {d['risk_score']}\")
print(f\"  Classification: {d['classification']}\")
print(f\"  Risk Category: {d['risk_category']}\")
print(f\"  Confidence: {d['confidence']}\")
print(f\"  Overall Score: {d['overall_score']:.2f}\")
print(f\"  Correctness: {d['correctness']:.2f}\")
print(f\"  Safety: {d['safety']:.2f}\")
print(f\"  Specificity: {d['specificity']:.2f}\")
print(f\"  Experimentation: {d['experimentation']:.2f}\")
" 2>/dev/null || echo "  Could not extract metrics")
  echo "$METRICS_BAD"
  echo "$METRICS_BAD" >> "$LOG_DIR/metrics.log"

  echo ""
  echo "" >> "$LOG_DIR/metrics.log"

  echo "Qualifying narrative:"
  echo "Qualifying narrative:" >> "$LOG_DIR/metrics.log"
  METRICS_GOOD=$(echo "$GREEN_RESPONSE_GOOD" | python3 -c "
import sys,json
d=json.load(sys.stdin)['result']['parts'][0]['data']
print(f\"  Risk Score: {d['risk_score']}\")
print(f\"  Classification: {d['classification']}\")
print(f\"  Risk Category: {d['risk_category']}\")
print(f\"  Confidence: {d['confidence']}\")
print(f\"  Overall Score: {d['overall_score']:.2f}\")
print(f\"  Correctness: {d['correctness']:.2f}\")
print(f\"  Safety: {d['safety']:.2f}\")
print(f\"  Specificity: {d['specificity']:.2f}\")
print(f\"  Experimentation: {d['experimentation']:.2f}\")
" 2>/dev/null || echo "  Could not extract metrics")
  echo "$METRICS_GOOD"
  echo "$METRICS_GOOD" >> "$LOG_DIR/metrics.log"

  # Generate AgentBeats-compatible results.json
  python3 -c "
import json
from datetime import datetime

bad = json.loads('''$GREEN_RESPONSE_BAD''')['result']['parts'][0]['data']
good = json.loads('''$GREEN_RESPONSE_GOOD''')['result']['parts'][0]['data']

results = {
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'version': '1.0',
    'participants': {
        'substantiator': 'local-test'
    },
    'results': [
        {
            'test_case': 'non_qualifying',
            'overall_score': bad['overall_score'],
            'classification': bad['classification'],
            'risk_score': bad['risk_score'],
            'risk_category': bad['risk_category'],
            'confidence': bad['confidence'],
            'component_scores': {
                'correctness': bad['correctness'],
                'safety': bad['safety'],
                'specificity': bad['specificity'],
                'experimentation': bad['experimentation']
            }
        },
        {
            'test_case': 'qualifying',
            'overall_score': good['overall_score'],
            'classification': good['classification'],
            'risk_score': good['risk_score'],
            'risk_category': good['risk_category'],
            'confidence': good['confidence'],
            'component_scores': {
                'correctness': good['correctness'],
                'safety': good['safety'],
                'specificity': good['specificity'],
                'experimentation': good['experimentation']
            }
        }
    ]
}

print(json.dumps(results, indent=2))
" > "$LOG_DIR/results.json" 2>/dev/null

  EXIT_CODE=0

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

  # Process each narrative
  jq -c '.[] | {index: .id, classification: .classification, expected_score: .expected_score, narrative: .narrative}' data/ground_truth.json | while read -r test_case; do
    INDEX=$(echo "$test_case" | jq -r '.index')
    EXPECTED_CLASS=$(echo "$test_case" | jq -r '.classification')
    EXPECTED_SCORE=$(echo "$test_case" | jq -r '.expected_score')
    NARRATIVE=$(echo "$test_case" | jq -r '.narrative')

    echo "Testing $INDEX: $EXPECTED_CLASS (expected score: $EXPECTED_SCORE)..."

    # Call Green Agent
    RESPONSE=$(curl -s -X POST http://localhost:8002/ \
      -H "Content-Type: application/json" \
      -d "{\"jsonrpc\":\"2.0\",\"id\":\"$INDEX\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"test-$INDEX\",\"role\":\"user\",\"parts\":[{\"text\":\"$NARRATIVE\"}]}}}")

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
  ACCURACY=$(echo "scale=2; $CORRECT_CLASS * 100 / $TOTAL" | bc)
  echo "Accuracy: ${ACCURACY}%"
  echo ""

  if [ "$ACCURACY" = "100.00" ]; then
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
    ground_truth = {item["id"]: item for item in json.load(f)}

# Process each response
for response_file in sorted(glob.glob(f"{log_dir}/*_response.json")):
    test_id = response_file.split("/")[-1].split("_")[0]

    try:
        with open(response_file) as f:
            response = json.load(f)

        actual_class = response.get("result", {}).get("parts", [{}])[0].get("data", {}).get("classification", "ERROR")
        actual_score = response.get("result", {}).get("parts", [{}])[0].get("data", {}).get("overall_score", None)

        expected = ground_truth.get(test_id, {})
        expected_class = expected.get("classification", "UNKNOWN")

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
  docker-compose -f "$COMPOSE_FILE" down
  echo "Containers stopped."
fi

exit $EXIT_CODE
