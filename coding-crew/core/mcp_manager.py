"""MCP Manager for handling multiple MCP client connections."""

import os
from typing import Dict, Any, Optional, List
import yaml
from loguru import logger

from .mcp_client import JIRAMCPClient, GitHubMCPClient


class MCPManager:
    """Manager for MCP client connections."""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.jira_client: Optional[JIRAMCPClient] = None
        self.github_client: Optional[GitHubMCPClient] = None
        self._connected = False
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load MCP configuration."""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "settings.yaml"
            )
        
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Expand environment variables
        mcp_config = config.get('mcp', {})
        for service, service_config in mcp_config.items():
            if 'auth' in service_config:
                for key, value in service_config['auth'].items():
                    if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                        env_var = value[2:-1]
                        service_config['auth'][key] = os.getenv(env_var, value)
        
        return config
    
    async def connect_all(self) -> bool:
        """Connect to all configured MCP servers."""
        success = True
        
        # Connect to JIRA if configured
        if 'jira' in self.config.get('mcp', {}):
            jira_config = self.config['mcp']['jira']
            self.jira_client = JIRAMCPClient(
                server_url=jira_config['server_url'],
                auth_config=jira_config['auth']
            )
            
            if not await self.jira_client.connect():
                logger.error("Failed to connect to JIRA MCP server")
                success = False
        
        # Connect to GitHub if configured
        if 'github' in self.config.get('mcp', {}):
            github_config = self.config['mcp']['github']
            self.github_client = GitHubMCPClient(
                server_url=github_config['server_url'],
                auth_config=github_config['auth']
            )
            
            if not await self.github_client.connect():
                logger.error("Failed to connect to GitHub MCP server")
                success = False
        
        self._connected = success
        return success
    
    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        if self.jira_client:
            await self.jira_client.disconnect()
            self.jira_client = None
        
        if self.github_client:
            await self.github_client.disconnect()
            self.github_client = None
        
        self._connected = False
    
    async def get_project_context(self, project_name: str, requirements: str) -> Dict[str, Any]:
        """Get project context from all connected services."""
        context = {
            "project_name": project_name,
            "requirements": requirements,
            "jira_context": None,
            "github_context": None
        }
        
        # Get JIRA context
        if self.jira_client:
            try:
                jira_context = await self.jira_client.get_context(
                    f"project = {self.config['mcp']['jira'].get('project_key', '')} AND text ~ \"{project_name}\""
                )
                context["jira_context"] = jira_context
            except Exception as e:
                logger.error(f"Failed to get JIRA context: {e}")
        
        # Get GitHub context
        if self.github_client:
            try:
                github_context = await self.github_client.get_context(
                    f"{project_name} in:name,description"
                )
                context["github_context"] = github_context
            except Exception as e:
                logger.error(f"Failed to get GitHub context: {e}")
        
        return context
    
    async def create_project_artifacts(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create project artifacts in external systems."""
        results = {}
        
        # Create JIRA epic/issues
        if self.jira_client and project_data.get("create_jira_epic"):
            try:
                epic_result = await self.jira_client.create_issue(
                    project_key=self.config['mcp']['jira'].get('project_key'),
                    summary=f"Epic: {project_data['name']}",
                    description=project_data.get('description', ''),
                    issue_type="Epic"
                )
                results["jira_epic"] = epic_result
                
                # Create development tasks
                for task in project_data.get('development_tasks', []):
                    task_result = await self.jira_client.create_issue(
                        project_key=self.config['mcp']['jira'].get('project_key'),
                        summary=task['summary'],
                        description=task.get('description', ''),
                        issue_type="Task"
                    )
                    results.setdefault("jira_tasks", []).append(task_result)
                    
            except Exception as e:
                logger.error(f"Failed to create JIRA artifacts: {e}")
        
        # Create GitHub repository
        if self.github_client and project_data.get("create_github_repo"):
            try:
                repo_result = await self.github_client.create_repository(
                    name=project_data['name'].lower().replace(' ', '-'),
                    description=project_data.get('description', ''),
                    private=project_data.get('private_repo', False)
                )
                results["github_repo"] = repo_result
                
                # Create initial issues
                for issue in project_data.get('github_issues', []):
                    issue_result = await self.github_client.create_issue(
                        repo=f"{self.config['mcp']['github'].get('organization')}/{project_data['name'].lower().replace(' ', '-')}",
                        title=issue['title'],
                        body=issue.get('body', ''),
                        labels=issue.get('labels', [])
                    )
                    results.setdefault("github_issues", []).append(issue_result)
                    
            except Exception as e:
                logger.error(f"Failed to create GitHub artifacts: {e}")
        
        return results
    
    def is_connected(self) -> bool:
        """Check if MCP manager is connected."""
        return self._connected
    
    def get_available_services(self) -> List[str]:
        """Get list of available MCP services."""
        services = []
        if self.jira_client and self.jira_client.session_id:
            services.append("jira")
        if self.github_client and self.github_client.session_id:
            services.append("github")
        return services