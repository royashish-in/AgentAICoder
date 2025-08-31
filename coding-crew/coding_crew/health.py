"""Health check endpoints."""

from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "coding-crew",
        "version": "0.1.0"
    }

@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """Readiness check for deployment."""
    # TODO: Add checks for Ollama connectivity, database, etc.
    return {
        "status": "ready",
        "dependencies": "ok"
    }