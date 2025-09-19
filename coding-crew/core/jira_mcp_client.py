"""JIRA MCP Client implementation."""

import asyncio
import json
import os
import base64
from typing import Dict, Any, Optional, List
from loguru import logger


class JiraMCPClient:
    """MCP client specifically for JIRA integration."""
    
    def __init__(self):
        self.mcp_url = "https://mcp.atlassian.com/v1/sse"
        self.jira_url = os.getenv("JIRA_URL")
        self.jira_email = os.getenv("JIRA_EMAIL") 
        self.jira_token = os.getenv("JIRA_API_TOKEN")
        self.timeout = 10
        self.cloud_id = None
    
    async def connect(self) -> bool:
        """Connect and authenticate with JIRA MCP."""
        try:
            # Get cloud ID for your JIRA instance
            self.cloud_id = await self._resolve_cloud_id()
            return self.cloud_id is not None
        except Exception as e:
            logger.error(f"JIRA MCP connection failed: {e}")
            return False
    
    async def get_user_stories(self, story_keys: List[str] = None) -> List[Dict[str, Any]]:
        """Get user stories from JIRA via MCP."""
        if not self.cloud_id:
            await self.connect()
        
        if not self.cloud_id:
            return []
        
        # Build JQL query
        if story_keys:
            jql = f"key in ({','.join(story_keys)})"
        else:
            jql = "issuetype = Story ORDER BY created DESC"
        
        return await self._search_issues(jql)
    
    async def _resolve_cloud_id(self) -> Optional[str]:
        """Resolve JIRA cloud ID via MCP."""
        try:
            # First try to get accessible resources
            result = await self._mcp_call("getAccessibleAtlassianResources", {})
            
            if result and "result" in result:
                resources = result["result"].get("data", [])
                # Find resource matching our JIRA URL
                for resource in resources:
                    if self.jira_url and resource.get("url", "").startswith(self.jira_url):
                        return resource.get("id")
                
                # Fallback to first available resource
                if resources:
                    return resources[0].get("id")
            
            # If no resources found, try using JIRA URL directly
            if self.jira_url:
                return self.jira_url
                
        except Exception as e:
            logger.warning(f"Cloud ID resolution failed: {e}")
        
        return None
    
    async def _search_issues(self, jql: str) -> List[Dict[str, Any]]:
        """Search JIRA issues via MCP."""
        try:
            result = await self._mcp_call("searchJiraIssuesUsingJql", {
                "cloudId": self.cloud_id,
                "jql": jql,
                "maxResults": 10,
                "fields": ["summary", "description", "status", "issuetype"]
            })
            
            if result and "result" in result:
                issues = result["result"].get("issues", [])
                return [{
                    "key": issue["key"],
                    "summary": issue["fields"]["summary"],
                    "description": issue["fields"].get("description", ""),
                    "status": issue["fields"]["status"]["name"],
                    "type": issue["fields"]["issuetype"]["name"]
                } for issue in issues]
                
        except Exception as e:
            logger.error(f"JIRA search failed: {e}")
        
        return []
    
    async def _mcp_call(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make authenticated MCP call."""
        try:
            # Set up environment with auth
            env = os.environ.copy()
            if self.jira_email and self.jira_token:
                # Add basic auth for Atlassian
                auth_string = f"{self.jira_email}:{self.jira_token}"
                auth_bytes = base64.b64encode(auth_string.encode()).decode()
                env["ATLASSIAN_AUTH"] = f"Basic {auth_bytes}"
            
            process = await asyncio.create_subprocess_exec(
                "npx", "-y", "mcp-remote", self.mcp_url,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": method, "arguments": params}
            }
            
            input_data = json.dumps(request) + "\n"
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input_data.encode()),
                timeout=self.timeout
            )
            
            # Parse JSON response
            for line in stdout.decode().strip().split("\n"):
                if line.strip():
                    try:
                        response = json.loads(line)
                        if "result" in response:
                            return response
                        elif "error" in response:
                            logger.error(f"MCP error: {response['error']}")
                            return None
                    except json.JSONDecodeError:
                        continue
            
        except Exception as e:
            logger.error(f"MCP call failed: {e}")
        
        return None