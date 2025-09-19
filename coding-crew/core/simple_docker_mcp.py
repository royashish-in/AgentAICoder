"""Simple Docker MCP client for JIRA."""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()


class SimpleDockerMCP:
    """Simple Docker MCP client."""
    
    def __init__(self):
        self.jira_url = os.getenv("JIRA_URL")
        self.jira_username = os.getenv("JIRA_USERNAME") or os.getenv("JIRA_EMAIL") 
        self.jira_token = os.getenv("JIRA_API_TOKEN")
    
    async def get_stories(self) -> List[Dict[str, Any]]:
        """Get JIRA stories via Docker MCP."""
        if not all([self.jira_url, self.jira_username, self.jira_token]):
            return []
        
        try:
            # Docker command
            cmd = [
                "docker", "run", "-i", "--rm", "--env-file", "coding-crew/.env", "ghcr.io/sooperset/mcp-atlassian:latest",
                # Environment variables loaded via --env-file
            ]
            
            # MCP requests
            requests = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "searchJiraIssuesUsingJql", "arguments": {"jql": "ORDER BY created DESC", "maxResults": 5}}}
            ]
            
            input_data = "\n".join(json.dumps(req) for req in requests) + "\n"
            
            # Run Docker container
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input_data.encode()),
                timeout=20
            )
            
            # Parse responses
            stories = []
            for line in stdout.decode().strip().split("\n"):
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get("id") == 2 and "result" in response:
                            issues = response["result"].get("issues", [])
                            stories = [{
                                "key": issue["key"],
                                "summary": issue["fields"]["summary"],
                                "status": issue["fields"]["status"]["name"]
                            } for issue in issues]
                            break
                    except json.JSONDecodeError:
                        continue
            
            return stories
            
        except Exception as e:
            print(f"Docker MCP error: {e}")
            return []