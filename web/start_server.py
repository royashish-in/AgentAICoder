#!/usr/bin/env python3
"""
Professional AgentAI Web Interface Startup Script
"""
import uvicorn
from app import app

if __name__ == "__main__":
    print("🚀 Starting AgentAI Professional Development Platform...")
    print("📍 Server will be available at: http://localhost:8002")
    print("📊 Dashboard: http://localhost:8002")
    print("🔧 API Docs: http://localhost:8002/docs")
    print("\n" + "="*50)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )