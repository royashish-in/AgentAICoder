"""MCP (Model Context Protocol) client for connecting to external services."""

import asyncio
import json
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import httpx
from loguru import logger


class MCPClient(ABC):
    """Base MCP client for connecting to MCP servers."""
    
    def __init__(self, server_url: str, auth_config: Dict[str, Any]):
        self.server_url = server_url
        self.auth_config = auth_config
        self.session_id: Optional[str] = None
        self.client = httpx.AsyncClient()
        
    async def connect(self) -> bool:
        """Establish connection to MCP server."""
        try:
            response = await self.client.post(
                f"{self.server_url}/mcp/initialize",
                json={
                    "protocol_version": "1.0",
                    "client_info": {"name": "AgentAI", "version": "0.1.0"},
                    "auth": self.auth_config
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                logger.info(f"Connected to MCP server: {self.server_url}")
                return True
            else:
                logger.error(f"Failed to connect to MCP server: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"MCP connection error: {e}")
            return False
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        if not self.session_id:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.client.post(
                f"{self.server_url}/mcp/tools/call",
                json={
                    "session_id": self.session_id,
                    "tool": tool_name,
                    "parameters": parameters
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise RuntimeError(f"Tool call failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"MCP tool call error: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools on the MCP server."""
        if not self.session_id:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.client.get(
                f"{self.server_url}/mcp/tools",
                params={"session_id": self.session_id}
            )
            
            if response.status_code == 200:
                return response.json().get("tools", [])
            else:
                raise RuntimeError(f"Failed to list tools: {response.status_code}")
                
        except Exception as e:
            logger.error(f"MCP list tools error: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.session_id:
            try:
                await self.client.post(
                    f"{self.server_url}/mcp/disconnect",
                    json={"session_id": self.session_id}
                )
            except Exception as e:
                logger.error(f"MCP disconnect error: {e}")
            finally:
                self.session_id = None
                await self.client.aclose()
    
    @abstractmethod
    async def get_context(self, query: str) -> Dict[str, Any]:
        """Get context from the external service."""
        pass


class JIRAMCPClient(MCPClient):
    """MCP client for JIRA integration."""
    
    async def get_context(self, query: str) -> Dict[str, Any]:
        """Get JIRA context for project requirements."""
        return await self.call_tool("jira_search", {
            "query": query,
            "fields": ["summary", "description", "status", "assignee", "labels"]
        })
    
    async def create_issue(self, project_key: str, summary: str, description: str, 
                          issue_type: str = "Task") -> Dict[str, Any]:
        """Create a new JIRA issue."""
        return await self.call_tool("jira_create_issue", {
            "project": project_key,
            "summary": summary,
            "description": description,
            "issuetype": issue_type
        })
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing JIRA issue."""
        return await self.call_tool("jira_update_issue", {
            "issue_key": issue_key,
            "fields": fields
        })


class GitHubMCPClient(MCPClient):
    """MCP client for GitHub integration."""
    
    async def get_context(self, query: str) -> Dict[str, Any]:
        """Get GitHub context for project requirements."""
        return await self.call_tool("github_search", {
            "query": query,
            "type": "repositories"
        })
    
    async def create_repository(self, name: str, description: str, 
                               private: bool = False) -> Dict[str, Any]:
        """Create a new GitHub repository."""
        return await self.call_tool("github_create_repo", {
            "name": name,
            "description": description,
            "private": private
        })
    
    async def create_issue(self, repo: str, title: str, body: str, 
                          labels: List[str] = None) -> Dict[str, Any]:
        """Create a GitHub issue."""
        return await self.call_tool("github_create_issue", {
            "repository": repo,
            "title": title,
            "body": body,
            "labels": labels or []
        })
    
    async def create_pull_request(self, repo: str, title: str, body: str,
                                 head: str, base: str = "main") -> Dict[str, Any]:
        """Create a GitHub pull request."""
        return await self.call_tool("github_create_pr", {
            "repository": repo,
            "title": title,
            "body": body,
            "head": head,
            "base": base
        })