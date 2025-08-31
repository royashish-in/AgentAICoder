#!/usr/bin/env python3
"""Test the web interface with live server."""

import subprocess
import sys
import time
import requests
from pathlib import Path

def test_web_interface():
    """Test the complete web interface."""
    print("🌐 Testing Web Interface")
    print("=" * 40)
    
    # Start server in background
    print("🚀 Starting FastAPI server...")
    server = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "web.backend.approval_api:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test API endpoint
        print("📡 Testing API endpoint...")
        response = requests.get("http://localhost:8000/api/analysis/pending")
        if response.status_code == 200:
            print("✅ API endpoint working")
            data = response.json()
            print(f"✅ Analysis data loaded: {len(data['analysis'])} chars")
            print(f"✅ System diagram: {len(data['system_diagrams']['system_architecture'])} chars")
            print(f"✅ Quality score: {sum(data['system_diagrams']['quality_validation'].values())}/5")
        else:
            print(f"❌ API failed: {response.status_code}")
        
        # Test frontend
        print("🎨 Testing frontend...")
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200 and "Analysis Review" in response.text:
            print("✅ Frontend HTML served successfully")
            print("✅ Contains approval interface")
        else:
            print(f"❌ Frontend failed: {response.status_code}")
        
        print("\n🎯 Web Interface Ready!")
        print("Visit: http://localhost:8000")
        print("API: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        server.terminate()
        server.wait()
        print("🛑 Server stopped")

if __name__ == "__main__":
    test_web_interface()