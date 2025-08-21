#!/bin/bash
# Run tests for Cowrie IRC Bot

set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Default to running all tests
TEST_PATH="tests"

# Parse arguments
COVERAGE=0
VERBOSE=0

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --coverage)
            COVERAGE=1
            shift
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# Run the tests
if [ $COVERAGE -eq 1 ]; then
    if [ $VERBOSE -eq 1 ]; then
        python -m pytest --cov=src --cov-report=term-missing -v "$TEST_PATH"
    else
        python -m pytest --cov=src "$TEST_PATH"
    fi
else
    if [ $VERBOSE -eq 1 ]; then
        python -m pytest -v "$TEST_PATH"
    else
        python -m pytest "$TEST_PATH"
    fi
fi