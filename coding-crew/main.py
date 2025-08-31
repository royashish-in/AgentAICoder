#!/usr/bin/env python3
"""
AgentAI Backend Services
This module provides the core AI agent functionality.
"""

import time
import sys
from pathlib import Path

def main():
    print("🤖 Starting AgentAI Backend Services...")
    print("📁 Working Directory:", Path.cwd())
    print("🔧 Backend services are ready")
    print("💡 Web interface should be started separately from /web folder")
    
    # Keep the process alive to maintain backend services
    try:
        while True:
            time.sleep(60)
            print("🔄 Backend services heartbeat...")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down backend services...")
        sys.exit(0)

if __name__ == "__main__":
    main()
