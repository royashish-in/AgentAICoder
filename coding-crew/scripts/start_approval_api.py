#!/usr/bin/env python3
"""Start the approval API server."""

import uvicorn
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("🚀 Starting Coding Crew Approval API...")
    print("📡 API will be available at http://localhost:8000")
    print("📋 API docs at http://localhost:8000/docs")
    
    uvicorn.run(
        "web.backend.approval_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )