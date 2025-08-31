# Coding Crew System

AI Agent Crew for Code Generation with Human-in-Loop Approval

## Quick Start

```bash
# Deploy the system
./scripts/deploy.sh

# Access at http://localhost:8000
```

## Features

- Complete workflow: Analysis → Approval → Development → Testing → Documentation
- Error recovery with retry logic and circuit breakers
- Production-ready deployment with Docker and Ollama

## API Endpoints

- `POST /workflows` - Create workflow
- `GET /workflows/{id}` - Get workflow status
- `POST /workflows/{id}/start-analysis` - Start analysis phase
- `POST /workflows/{id}/approve` - Human approval
- `GET /health` - Health check