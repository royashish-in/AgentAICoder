#!/usr/bin/env python3
"""Start the web interface for human approval workflow."""

import subprocess
import sys
import time
import requests
from pathlib import Path

def start_backend():
    """Start FastAPI backend server."""
    print("🚀 Starting FastAPI backend...")
    backend_path = Path("web/backend")
    
    # Start uvicorn server
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "approval_api:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ]
    
    return subprocess.Popen(cmd, cwd=backend_path)

def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get("http://localhost:8000/api/analysis/pending", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Start the complete web interface."""
    print("🌐 Starting Coding Crew Web Interface")
    print("=" * 50)
    
    # Start backend
    backend_process = start_backend()
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    for i in range(30):
        if check_backend():
            print("✅ Backend is running on http://localhost:8000")
            break
        time.sleep(1)
    else:
        print("❌ Backend failed to start")
        backend_process.terminate()
        return
    
    print("\n📋 Web Interface Ready:")
    print("  • Backend API: http://localhost:8000")
    print("  • API Docs: http://localhost:8000/docs")
    print("  • Approval Endpoint: http://localhost:8000/api/analysis/pending")
    
    print("\n🎯 Test the approval workflow:")
    print("  1. Visit http://localhost:8000/api/analysis/pending")
    print("  2. Review the analysis and diagrams")
    print("  3. Submit approval/rejection")
    
    try:
        print("\n⌨️  Press Ctrl+C to stop the server")
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping web interface...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ Web interface stopped")

if __name__ == "__main__":
    main()