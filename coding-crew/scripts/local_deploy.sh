#!/bin/bash
set -e

echo "🚀 Local Deployment - Coding Crew System"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install Ollama first:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "🔄 Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Pull required models if not present
echo "📥 Checking required models..."
if ! ollama list | grep -q "llama3.1:8b"; then
    echo "📥 Pulling llama3.1:8b..."
    ollama pull llama3.1:8b
fi

if ! ollama list | grep -q "qwen2.5-coder:1.5b-base"; then
    echo "📥 Pulling qwen2.5-coder:1.5b-base..."
    ollama pull qwen2.5-coder:1.5b-base
fi

# Create environment file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Create data directories
mkdir -p data logs

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Start the application
echo "🏃 Starting Coding Crew System..."
echo "🌐 Access at: http://localhost:8000"
echo "📊 Health check: http://localhost:8000/health"
echo "📋 API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

uv run uvicorn coding_crew.main:app --host 0.0.0.0 --port 8000 --reload