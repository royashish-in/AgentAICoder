"""MCP-enhanced agents that integrate with external services."""

import os
from crewai import Agent
from core.llm_config import get_analysis_llm, get_coding_llm
from core.mcp_manager import MCPManager
from typing import Dict, Any, Optional

# Configure environment for CrewAI + Ollama
os.environ["OPENAI_API_KEY"] = "sk-fake-key-for-ollama"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"


class MCPEnhancedAnalysisAgent:
    """Analysis agent enhanced with MCP integration."""
    
    def __init__(self, mcp_manager: MCPManager):
        self.mcp_manager = mcp_manager
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the enhanced analysis agent."""
        return Agent(
            role='MCP-Enhanced Requirements Analyst',
            goal='Analyze requirements using external context from JIRA and GitHub to create comprehensive system architecture',
            backstory="""You are an expert system architect with access to external project management and code repository systems.
            You can query JIRA for existing project context, requirements, and issues, and GitHub for similar projects and code patterns.
            You use this external context to create more informed and comprehensive system designs.""",
            verbose=True,
            allow_delegation=False,
            llm=get_analysis_llm(),
            max_iter=5
        )
    
    async def analyze_with_context(self, requirements: str, project_name: str) -> Dict[str, Any]:
        """Analyze requirements with external MCP context."""
        # Get external context
        external_context = await self.mcp_manager.get_project_context(project_name, requirements)
        
        # Enhance requirements with external context
        enhanced_requirements = self._enhance_requirements(requirements, external_context)
        
        # Use the agent to analyze enhanced requirements
        # Note: This would integrate with CrewAI's task execution
        return {
            "original_requirements": requirements,
            "external_context": external_context,
            "enhanced_requirements": enhanced_requirements,
            "analysis_agent": self.agent
        }
    
    def _enhance_requirements(self, requirements: str, context: Dict[str, Any]) -> str:
        """Enhance requirements with external context."""
        enhanced = f"# Enhanced Requirements Analysis\n\n## Original Requirements\n{requirements}\n\n"
        
        if context.get("jira_context"):
            enhanced += "## JIRA Context\n"
            jira_data = context["jira_context"]
            if jira_data.get("issues"):
                enhanced += "### Related Issues:\n"
                for issue in jira_data["issues"][:5]:  # Limit to top 5
                    enhanced += f"- {issue.get('key', 'N/A')}: {issue.get('summary', 'N/A')}\n"
            enhanced += "\n"
        
        if context.get("github_context"):
            enhanced += "## GitHub Context\n"
            github_data = context["github_context"]
            if github_data.get("repositories"):
                enhanced += "### Similar Repositories:\n"
                for repo in github_data["repositories"][:3]:  # Limit to top 3
                    enhanced += f"- {repo.get('name', 'N/A')}: {repo.get('description', 'N/A')}\n"
            enhanced += "\n"
        
        enhanced += "## Analysis Instructions\n"
        enhanced += "Please analyze the requirements considering the external context provided above. "
        enhanced += "Identify patterns, potential conflicts, and opportunities for reuse or integration."
        
        return enhanced


class MCPEnhancedDevelopmentAgent:
    """Development agent enhanced with MCP integration."""
    
    def __init__(self, mcp_manager: MCPManager):
        self.mcp_manager = mcp_manager
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the enhanced development agent."""
        return Agent(
            role='MCP-Enhanced Senior Developer',
            goal='Generate code and create project artifacts in external systems like JIRA and GitHub',
            backstory="""You are a senior developer who not only writes excellent code but also manages project artifacts.
            You can create JIRA issues for tracking development tasks and set up GitHub repositories with proper structure.
            You ensure that development work is properly tracked and organized across all project management tools.""",
            verbose=True,
            allow_delegation=False,
            llm=get_coding_llm(),
            max_iter=5
        )
    
    async def develop_with_artifacts(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Develop project and create external artifacts."""
        # Create external project artifacts
        artifacts = await self.mcp_manager.create_project_artifacts(project_data)
        
        return {
            "project_data": project_data,
            "external_artifacts": artifacts,
            "development_agent": self.agent
        }


def create_mcp_enhanced_agents(mcp_manager: Optional[MCPManager] = None) -> Dict[str, Any]:
    """Create MCP-enhanced agents."""
    if not mcp_manager:
        mcp_manager = MCPManager()
    
    return {
        "analysis_agent": MCPEnhancedAnalysisAgent(mcp_manager),
        "development_agent": MCPEnhancedDevelopmentAgent(mcp_manager),
        "mcp_manager": mcp_manager
    }