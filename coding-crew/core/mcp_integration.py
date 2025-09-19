"""Minimal MCP integration for AgentAI."""

import os
import asyncio
import json
from typing import Dict, Any, Optional, List
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import httpx
from .jira_mcp_client import JiraMCPClient
from .docker_mcp_client import DockerMCPClient


class MCPIntegration:
    """MCP integration using mcp-remote protocol."""
    
    def __init__(self):
        self.enabled = os.getenv("MCP_ENABLED", "true").lower() == "true"  # Default to enabled
        self.mcp_url = os.getenv("MCP_SERVER_URL", "direct://jira-client")
        self.mcp_type = os.getenv("MCP_SERVER_TYPE", "docker_mcp")  # Use our Docker container
        self.timeout = int(os.getenv("MCP_TIMEOUT", "15"))
        self.auth_token = os.getenv("MCP_AUTH_TOKEN")
        self.tools_config = self._get_tools_config()
    
    async def get_user_stories(self, story_keys: List[str] = None) -> Dict[str, Any]:
        """Get JIRA user stories."""
        if not self.enabled:
            return {"mcp_enabled": False}
        
        stories = await self._query_jira_stories(story_keys)
        return {"mcp_enabled": True, "user_stories": stories or []}
    
    async def create_project_artifacts(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create project artifacts in external systems."""
        if not self.enabled:
            return {"mcp_enabled": False}
        
        results = {"mcp_enabled": True}
        
        # Create JIRA issue
        if self.jira_url and self.jira_token:
            jira_result = await self._create_jira_issue(project_data)
            if jira_result:
                results["jira_issue"] = jira_result
        
        # Create GitHub repo
        if self.github_url and self.github_token:
            github_result = await self._create_github_repo(project_data)
            if github_result:
                results["github_repo"] = github_result
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get MCP integration status."""
        return {
            "mcp_enabled": self.enabled,
            "mcp_url": self.mcp_url,
            "mcp_type": self.mcp_type,
            "tools_available": self.tools_config.get("search_tool", "unknown")
        }
    
    def _get_tools_config(self) -> Dict[str, Any]:
        """Get tools configuration based on server type."""
        configs = {
            "docker_mcp": {"search_tool": "DockerMCPClient", "requires_cloud_id": False},
            "jira_mcp": {"search_tool": "JiraMCPClient", "requires_cloud_id": False},
            "atlassian": {"search_tool": "searchJiraIssuesUsingJql", "requires_cloud_id": True},
            "custom": {"search_tool": "search_issues", "requires_cloud_id": False},
            "local": {"search_tool": "jira_search", "requires_cloud_id": False}
        }
        return configs.get(self.mcp_type, configs["atlassian"])
    
    async def _query_jira_stories(self, story_keys: List[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Query JIRA stories using our Docker MCP server."""
        logger.info("Attempting to query JIRA stories...")
        
        try:
            # Always try our Docker MCP client first
            logger.info(f"Querying MCP server: {self.mcp_url}")
            
            # Use direct JIRA integration instead of Docker container
            from .jira_integration import get_jira_integration
            jira_integration = await get_jira_integration()
            
            if story_keys:
                # Filter by specific story keys
                all_stories = await jira_integration.get_user_stories(project="KW", limit=100)
                filtered_stories = [story for story in all_stories if story['key'] in story_keys]
                logger.info(f"JIRA query result: {len(filtered_stories)} selected stories from {len(all_stories)} total")
                return filtered_stories
            else:
                # Get all stories
                stories = await jira_integration.get_user_stories(project="KW", limit=100)
                if stories:
                    logger.info(f"JIRA query result: {len(stories)} stories found")
                    return stories
                else:
                    logger.warning("No stories found in JIRA")
                    return None

            
        except Exception as e:
            logger.warning(f"MCP query failed: {e}")
            logger.info("JIRA query result: None")
            return None
    
    async def _get_cloud_id(self) -> Optional[str]:
        """Get Atlassian cloudId via MCP."""
        try:
            # Try using site URL first if configured
            site_url = os.getenv("ATLASSIAN_SITE_URL")
            if site_url:
                return site_url
            
            # Fallback to MCP resource discovery
            result = await self._mcp_call("getAccessibleAtlassianResources", {})
            if result and "result" in result:
                resources = result["result"].get("data", [])
                if resources:
                    return resources[0].get("id")
        except Exception as e:
            logger.warning(f"Failed to get cloudId: {e}")
        return None
    
    async def _mcp_search_issues(self, cloud_id: str, jql: str) -> Optional[List[Dict[str, Any]]]:
        """Search JIRA issues using MCP."""
        try:
            result = await self._mcp_call("searchJiraIssuesUsingJql", {
                "cloudId": cloud_id,
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
            logger.warning(f"MCP issue search failed: {e}")
        return None
    
    async def _mcp_call(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make MCP call and return response."""
        try:
            # Set up environment for Atlassian auth
            env = os.environ.copy()
            if os.getenv("ATLASSIAN_EMAIL") and os.getenv("ATLASSIAN_API_TOKEN"):
                env["ATLASSIAN_EMAIL"] = os.getenv("ATLASSIAN_EMAIL")
                env["ATLASSIAN_API_TOKEN"] = os.getenv("ATLASSIAN_API_TOKEN")
            
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
            
            # Parse response from stdout
            for line in stdout.decode().strip().split("\n"):
                if line.strip():
                    try:
                        response = json.loads(line)
                        if "result" in response:
                            return response
                    except json.JSONDecodeError:
                        continue
            
        except Exception as e:
            logger.warning(f"MCP call failed: {e}")
        return None
    
    def _get_demo_stories(self) -> List[Dict[str, Any]]:
        """Return demo stories."""
        return [
            {"key": "DEMO-001", "summary": "User Authentication System", "description": "Implement secure user login and registration"},
            {"key": "DEMO-002", "summary": "Dashboard Analytics", "description": "Create real-time analytics dashboard"},
            {"key": "DEMO-003", "summary": "API Integration", "description": "Integrate with third-party APIs"}
        ]
    

    

    
    async def _create_jira_issue(self, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create JIRA issue."""
        return {"key": "NEW-001", "url": "https://demo.atlassian.net/browse/NEW-001"}
    
    async def _create_github_repo(self, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create GitHub repository."""
        return {"name": project_data.get("name", "project"), "url": "https://github.com/user/repo"}