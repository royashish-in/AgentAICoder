#!/bin/bash
# Test runner script for coding crew application

set -e

echo "🧪 Running Coding Crew Test Suite"
echo "=================================="

# Check if Ollama is running
OLLAMA_RUNNING=false
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    OLLAMA_RUNNING=true
    echo "✅ Ollama service detected"
else
    echo "⚠️  Ollama service not detected"
fi

# Unit tests
echo ""
echo "📋 Running Unit Tests..."
echo "------------------------"
uv run pytest tests/test_*.py -v --cov=coding_crew --cov=core --cov=agents --cov-report=term-missing

# Integration tests
echo ""
echo "🔗 Running Integration Tests..."
echo "-------------------------------"
uv run pytest tests/integration/ -v

# End-to-end tests
echo ""
echo "🎯 Running End-to-End Tests..."
echo "------------------------------"
uv run pytest tests/e2e/ -v

# Ollama integration tests (if available)
if [ "$OLLAMA_RUNNING" = true ]; then
    echo ""
    echo "🤖 Running Ollama Integration Tests..."
    echo "------------------------------------"
    # Add Ollama-specific tests here when implemented
    echo "Ollama tests would run here (not implemented yet)"
else
    echo ""
    echo "⏭️  Skipping Ollama tests (service not available)"
fi

# Code quality checks
echo ""
echo "🔍 Running Code Quality Checks..."
echo "--------------------------------"
echo "Formatting check..."
uv run black --check coding_crew/ core/ agents/ tests/

echo "Linting..."
uv run flake8 coding_crew/ core/ agents/ tests/

echo "Type checking..."
uv run mypy coding_crew/ core/ agents/

echo ""
echo "✅ All tests completed successfully!"
echo "=================================="