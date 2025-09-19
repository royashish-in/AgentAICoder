"""Docker-based MCP client for JIRA."""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DockerMCPClient:
    """MCP client using Docker Atlassian server."""
    
    def __init__(self):
        self.docker_image = "mcp/atlassian"
        self.jira_url = os.getenv("JIRA_URL", "")
        self.jira_username = os.getenv("JIRA_EMAIL", "")
        self.jira_token = os.getenv("JIRA_API_TOKEN", "")
        
        print(f"DEBUG - JIRA_URL: {self.jira_url}")
        print(f"DEBUG - JIRA_USERNAME: {self.jira_username}")
        print(f"DEBUG - JIRA_TOKEN: {'SET' if self.jira_token else 'NOT SET'}")
    
    async def get_user_stories(self, story_keys: List[str] = None) -> List[Dict[str, Any]]:
        """Get user stories via Docker MCP server."""
        # Build JQL query
        if story_keys:
            jql = f"key in ({','.join(story_keys)})"
        else:
            jql = "issuetype = Story ORDER BY created DESC"
        
        return await self._search_issues(jql)
    
    async def _search_issues(self, jql: str) -> List[Dict[str, Any]]:
        """Search JIRA issues via Docker MCP."""
        try:
            result = await self._docker_mcp_call("searchJiraIssuesUsingJql", {
                "jql": jql,
                "maxResults": 10
            })
            
            if result and "result" in result:
                issues = result["result"].get("issues", [])
                return [{
                    "key": issue["key"],
                    "summary": issue["fields"]["summary"],
                    "description": issue["fields"].get("description", ""),
                    "status": issue["fields"]["status"]["name"]
                } for issue in issues]
                
        except Exception as e:
            logger.error(f"Docker MCP search failed: {e}")
        
        return []
    
    async def _docker_mcp_call(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make MCP call via Docker."""
        try:
            # Build Docker command
            docker_cmd = ["docker", "run", "-i", "--rm"]
            
            # Environment variables are passed as command line args instead
            
            # Add JIRA parameters
            docker_cmd.extend([
                self.docker_image,
                "--jira-url", self.jira_url,
                "--jira-username", self.jira_username
            ])
            
            # Add token
            if self.jira_token:
                docker_cmd.extend(["--jira-token", self.jira_token])
            
            # Use current environment
            env = os.environ.copy()
            
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Send initialization first
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "AgentAI", "version": "1.0.0"}
                }
            }
            
            # Send tool call request
            tool_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": method, "arguments": params}
            }
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(tool_request) + "\n"
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input_data.encode()),
                timeout=30
            )
            
            # Parse response
            for line in stdout.decode().strip().split("\n"):
                if line.strip():
                    try:
                        response = json.loads(line)
                        if "result" in response:
                            return response
                    except json.JSONDecodeError:
                        continue
            
        except Exception as e:
            logger.error(f"Docker MCP call failed: {e}")
            # Debug output
            if 'stdout' in locals():
                logger.error(f"Docker stdout: {stdout.decode()}")
            if 'stderr' in locals():
                logger.error(f"Docker stderr: {stderr.decode()}")
        
        # Always show debug info
        if 'stdout' in locals() and 'stderr' in locals():
            print(f"DEBUG - Docker stdout: {stdout.decode()[:500]}")
            print(f"DEBUG - Docker stderr: {stderr.decode()[:500]}")
            print(f"DEBUG - Docker command: {' '.join(docker_cmd)}")
        
        return None