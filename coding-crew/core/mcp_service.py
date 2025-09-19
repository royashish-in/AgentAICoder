"""MCP integration service for AgentAI."""

import os
from typing import Dict, Any, Optional
from loguru import logger

from .simple_mcp_client import JIRAClient, GitHubClient


class MCPService:
    """Service for managing MCP integrations."""
    
    def __init__(self):
        self.jira_client: Optional[JIRAClient] = None
        self.github_client: Optional[GitHubClient] = None
        self.enabled = os.getenv("MCP_ENABLED", "false").lower() == "true"
    
    async def initialize(self) -> bool:
        """Initialize MCP connections."""
        if not self.enabled:
            logger.info("MCP integration disabled")
            return False
        
        success = True
        
        # Initialize JIRA client
        jira_url = os.getenv("JIRA_MCP_URL")
        jira_token = os.getenv("JIRA_TOKEN")
        if jira_url and jira_token:
            self.jira_client = JIRAClient(jira_url, jira_token)
            if not await self.jira_client.connect():
                success = False
        
        # Initialize GitHub client
        github_url = os.getenv("GITHUB_MCP_URL")
        github_token = os.getenv("GITHUB_TOKEN")
        if github_url and github_token:
            self.github_client = GitHubClient(github_url, github_token)
            if not await self.github_client.connect():
                success = False
        
        return success
    
    async def get_project_context(self, project_name: str) -> Dict[str, Any]:
        """Get project context from external services."""
        context = {"project_name": project_name}
        
        # Get JIRA context
        if self.jira_client:
            jira_data = await self.jira_client.search_issues(f'text ~ "{project_name}"')
            if jira_data:
                context["jira"] = jira_data
        
        # Get GitHub context
        if self.github_client:
            github_data = await self.github_client.search_repos(project_name)
            if github_data:
                context["github"] = github_data
        
        return context
    
    async def create_project_artifacts(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create project artifacts in external systems."""
        results = {}
        
        # Create JIRA issue
        if self.jira_client and project_data.get("create_jira_issue"):
            jira_result = await self.jira_client.create_issue(
                project=os.getenv("JIRA_PROJECT", "DEV"),
                summary=f"Project: {project_data['name']}",
                description=project_data.get("description", "")
            )
            if jira_result:
                results["jira_issue"] = jira_result
        
        # Create GitHub repo
        if self.github_client and project_data.get("create_github_repo"):
            github_result = await self.github_client.create_repo(
                name=project_data["name"].lower().replace(" ", "-"),
                description=project_data.get("description", "")
            )
            if github_result:
                results["github_repo"] = github_result
        
        return results
    
    async def cleanup(self):
        """Cleanup MCP connections."""
        if self.jira_client:
            await self.jira_client.disconnect()
        if self.github_client:
            await self.github_client.disconnect()
    
    def is_available(self) -> bool:
        """Check if MCP services are available."""
        return self.enabled and (self.jira_client or self.github_client)