#!/usr/bin/env python3
"""Setup Atlassian CLI authentication for MCP."""

import subprocess
import sys
import os

def setup_atlassian_auth():
    """Setup Atlassian authentication."""
    print("=== Atlassian MCP Authentication Setup ===")
    print("This will authenticate with Atlassian for MCP access")
    print()
    
    try:
        # Check if already authenticated
        result = subprocess.run([
            "npx", "-y", "@atlassian/cli", "auth", "status"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Already authenticated with Atlassian")
            return True
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("🔐 Starting Atlassian authentication...")
    print("This will open a browser window for login")
    
    try:
        # Run Atlassian CLI auth
        result = subprocess.run([
            "npx", "-y", "@atlassian/cli", "auth", "login"
        ], timeout=120)
        
        if result.returncode == 0:
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Authentication timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if setup_atlassian_auth():
        print("\n🎉 Ready to use MCP with your JIRA instance!")
        print("Run: python test_mcp_config.py")
    else:
        print("\n💡 Manual setup:")
        print("1. Run: npx @atlassian/cli auth login")
        print("2. Follow browser authentication")
        print("3. Test with: python test_mcp_config.py")