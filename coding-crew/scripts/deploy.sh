#!/bin/bash
set -e

echo "🚀 Deploying Coding Crew System"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env from example..."
    cp .env.example .env
    echo "📝 Please edit .env with your configuration"
fi

# Create data directories
mkdir -p data logs

# Build and start services
echo "🔨 Building containers..."
docker-compose -f docker-compose.prod.yml build

echo "🏃 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo "🏥 Checking service health..."
docker-compose -f docker-compose.prod.yml ps

# Pull Ollama models
echo "📥 Pulling required Ollama models..."
docker-compose -f docker-compose.prod.yml exec ollama ollama pull llama3.1:8b
docker-compose -f docker-compose.prod.yml exec ollama ollama pull qwen2.5-coder:1.5b-base

echo "✅ Deployment complete!"
echo "🌐 Access the application at: http://localhost:8000"
echo "📊 View logs with: docker-compose -f docker-compose.prod.yml logs -f"