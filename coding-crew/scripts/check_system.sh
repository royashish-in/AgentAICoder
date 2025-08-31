#!/bin/bash

echo "🔍 System Check - Coding Crew"
echo "=============================="

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version)"
else
    echo "❌ Python 3 not found"
fi

# Check uv
if command -v uv &> /dev/null; then
    echo "✅ uv: $(uv --version)"
else
    echo "❌ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    echo "✅ Ollama: $(ollama --version)"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✅ Ollama service: Running"
        
        # Check models
        echo "📋 Available models:"
        ollama list | grep -E "(llama3.1:8b|qwen2.5-coder)" || echo "⚠️  Required models not found"
    else
        echo "⚠️  Ollama service: Not running (run 'ollama serve')"
    fi
else
    echo "❌ Ollama not found. Install from: https://ollama.ai"
fi

# Check port availability
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000: In use"
else
    echo "✅ Port 8000: Available"
fi

echo ""
echo "🚀 Ready to deploy? Run: ./scripts/local_deploy.sh"