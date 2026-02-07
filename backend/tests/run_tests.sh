#!/bin/bash
# =============================================================================
# EvalHub Test Runner Script
# =============================================================================
# This script runs the test suite and generates evidence for M3 documentation.
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh unit         # Run only unit tests
#   ./run_tests.sh integration  # Run only integration tests
#   ./run_tests.sh e2e          # Run only end-to-end tests
#   ./run_tests.sh quick        # Run quick smoke tests (health check only)
#
# Prerequisites:
#   - Python 3.12+ installed
#   - Poetry installed and dependencies resolved
#   - Database accessible (for integration/e2e tests)
#   - Environment variables set (.env file)
#
# Output:
#   - Test results printed to console
#   - Evidence files saved to tests/evidence/
#   - Coverage report generated (if running full suite)
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   EvalHub Test Suite Runner${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Navigate to backend directory
cd "$BACKEND_DIR"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Error: Poetry is not installed${NC}"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Some tests may fail.${NC}"
fi

# Determine test scope
TEST_SCOPE="${1:-all}"

run_unit_tests() {
    echo -e "\n${GREEN}Running Unit Tests...${NC}"
    poetry run pytest tests/unit/ -v --tb=short
}

run_integration_tests() {
    echo -e "\n${GREEN}Running Integration Tests...${NC}"
    poetry run pytest tests/integration/ -v --tb=short
}

run_e2e_tests() {
    echo -e "\n${GREEN}Running End-to-End Tests...${NC}"
    poetry run pytest tests/e2e/ -v --tb=short
}

run_quick_tests() {
    echo -e "\n${GREEN}Running Quick Smoke Tests...${NC}"
    poetry run pytest tests/test_main.py -v --tb=short
}

run_all_tests() {
    echo -e "\n${GREEN}Running Full Test Suite with Coverage...${NC}"
    poetry run pytest tests/ -v --tb=short --cov=api --cov-report=term-missing --cov-report=html:tests/evidence/coverage_report
}

case "$TEST_SCOPE" in
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    e2e)
        run_e2e_tests
        ;;
    quick)
        run_quick_tests
        ;;
    all)
        run_all_tests
        ;;
    *)
        echo -e "${RED}Unknown test scope: $TEST_SCOPE${NC}"
        echo "Usage: $0 [unit|integration|e2e|quick|all]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Test Execution Complete${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Evidence files are saved in: tests/evidence/"
echo ""
