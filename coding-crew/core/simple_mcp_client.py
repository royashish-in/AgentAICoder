"""Simplified MCP client for JIRA and GitHub integration."""

import asyncio
import json
from typing import Dict, Any, Optional
import httpx
from loguru import logger


class SimpleMCPClient:
    """Simplified MCP client for external service integration."""
    
    def __init__(self, service_name: str, server_url: str, auth_token: str):
        self.service_name = service_name
        self.server_url = server_url
        self.auth_token = auth_token
        self.client = httpx.AsyncClient(timeout=30.0)
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to MCP server."""
        try:
            response = await self.client.post(
                f"{self.server_url}/connect",
                json={"service": self.service_name, "token": self.auth_token}
            )
            self.connected = response.status_code == 200
            if self.connected:
                logger.info(f"Connected to {self.service_name} MCP server")
            return self.connected
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to {self.service_name}: {e}")
            return False
    
    async def query(self, action: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute query on MCP server."""
        if not self.connected:
            return None
        
        try:
            response = await self.client.post(
                f"{self.server_url}/query",
                json={"action": action, "params": params}
            )
            return response.json() if response.status_code == 200 else None
        except httpx.RequestError as e:
            logger.error(f"MCP query failed: {e}")
            return None
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        await self.client.aclose()
        self.connected = False


class JIRAClient(SimpleMCPClient):
    """JIRA MCP client."""
    
    def __init__(self, server_url: str, auth_token: str):
        super().__init__("jira", server_url, auth_token)
    
    async def search_issues(self, query: str) -> Optional[Dict[str, Any]]:
        """Search JIRA issues."""
        return await self.query("search", {"jql": query})
    
    async def create_issue(self, project: str, summary: str, description: str) -> Optional[Dict[str, Any]]:
        """Create JIRA issue."""
        return await self.query("create_issue", {
            "project": project,
            "summary": summary,
            "description": description
        })


class GitHubClient(SimpleMCPClient):
    """GitHub MCP client."""
    
    def __init__(self, server_url: str, auth_token: str):
        super().__init__("github", server_url, auth_token)
    
    async def search_repos(self, query: str) -> Optional[Dict[str, Any]]:
        """Search GitHub repositories."""
        return await self.query("search_repos", {"q": query})
    
    async def create_repo(self, name: str, description: str) -> Optional[Dict[str, Any]]:
        """Create GitHub repository."""
        return await self.query("create_repo", {
            "name": name,
            "description": description
        })