#!/usr/bin/env python3
"""Debug environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

print("=== Environment Debug ===")
print(f"JIRA_URL: {os.getenv('JIRA_URL')}")
print(f"JIRA_EMAIL: {os.getenv('JIRA_EMAIL')}")
print(f"JIRA_API_TOKEN: {'SET' if os.getenv('JIRA_API_TOKEN') else 'NOT SET'}")
print(f"MCP_ENABLED: {os.getenv('MCP_ENABLED')}")
print(f"MCP_SERVER_TYPE: {os.getenv('MCP_SERVER_TYPE')}")