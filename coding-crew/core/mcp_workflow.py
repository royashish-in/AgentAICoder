"""MCP-integrated workflow for enhanced project development."""

import asyncio
from typing import Dict, Any, List
from loguru import logger

from .mcp_manager import MCPManager
from ..agents.mcp_enhanced_agents import create_mcp_enhanced_agents
from .workflow import BaseWorkflow


class MCPIntegratedWorkflow(BaseWorkflow):
    """Workflow that integrates MCP services for enhanced development."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.mcp_manager = MCPManager()
        self.mcp_agents = None
        self._mcp_connected = False
    
    async def initialize(self) -> bool:
        """Initialize MCP connections and agents."""
        try:
            # Connect to MCP services
            if await self.mcp_manager.connect_all():
                self._mcp_connected = True
                self.mcp_agents = create_mcp_enhanced_agents(self.mcp_manager)
                logger.info("MCP workflow initialized successfully")
                return True
            else:
                logger.warning("MCP services not available, falling back to standard workflow")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize MCP workflow: {e}")
            return False
    
    async def analyze_requirements_with_context(self, requirements: str, project_name: str) -> Dict[str, Any]:
        """Analyze requirements with external context from MCP services."""
        if not self._mcp_connected:
            raise RuntimeError("MCP services not connected")
        
        analysis_agent = self.mcp_agents["analysis_agent"]
        return await analysis_agent.analyze_with_context(requirements, project_name)
    
    async def create_project_with_artifacts(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create project with external artifacts in JIRA and GitHub."""
        if not self._mcp_connected:
            raise RuntimeError("MCP services not connected")
        
        development_agent = self.mcp_agents["development_agent"]
        return await development_agent.develop_with_artifacts(project_data)
    
    async def execute_enhanced_workflow(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete MCP-enhanced workflow."""
        workflow_id = request_data.get("workflow_id", "unknown")
        project_name = request_data.get("project_name", "Unknown Project")
        requirements = request_data.get("requirements", "")
        
        logger.info(f"Starting MCP-enhanced workflow: {workflow_id}")
        
        try:
            # Phase 1: Enhanced Requirements Analysis
            logger.info("Phase 1: Enhanced Requirements Analysis with MCP context")
            analysis_result = await self.analyze_requirements_with_context(requirements, project_name)
            
            # Phase 2: Human Approval (if enabled)
            if self.config.get("features", {}).get("enable_human_approval", True):
                logger.info("Phase 2: Waiting for human approval")
                # This would integrate with your existing approval workflow
                approval_result = await self._wait_for_approval(analysis_result)
                if not approval_result.get("approved", False):
                    return {"status": "rejected", "reason": approval_result.get("reason")}
            
            # Phase 3: Development with External Artifacts
            logger.info("Phase 3: Development with external artifact creation")
            project_data = {
                "name": project_name,
                "description": requirements,
                "create_jira_epic": True,
                "create_github_repo": True,
                "development_tasks": self._extract_development_tasks(analysis_result),
                "github_issues": self._extract_github_issues(analysis_result)
            }
            
            development_result = await self.create_project_with_artifacts(project_data)
            
            # Phase 4: Testing and Documentation
            logger.info("Phase 4: Testing and Documentation")
            # Use existing testing and documentation workflows
            
            return {
                "status": "completed",
                "workflow_id": workflow_id,
                "analysis": analysis_result,
                "development": development_result,
                "external_artifacts": development_result.get("external_artifacts", {}),
                "mcp_services": self.mcp_manager.get_available_services()
            }
            
        except Exception as e:
            logger.error(f"MCP workflow failed: {e}")
            return {
                "status": "failed",
                "workflow_id": workflow_id,
                "error": str(e)
            }
    
    def _extract_development_tasks(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract development tasks from analysis result."""
        # This would parse the analysis to extract specific development tasks
        return [
            {"summary": "Set up project structure", "description": "Initialize project with proper structure"},
            {"summary": "Implement core functionality", "description": "Develop main application features"},
            {"summary": "Add tests", "description": "Create comprehensive test suite"},
            {"summary": "Documentation", "description": "Create project documentation"}
        ]
    
    def _extract_github_issues(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract GitHub issues from analysis result."""
        # This would parse the analysis to extract specific GitHub issues
        return [
            {"title": "Setup CI/CD Pipeline", "body": "Configure automated testing and deployment", "labels": ["enhancement"]},
            {"title": "Add Documentation", "body": "Create comprehensive project documentation", "labels": ["documentation"]},
            {"title": "Security Review", "body": "Conduct security analysis and implement fixes", "labels": ["security"]}
        ]
    
    async def _wait_for_approval(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for human approval (placeholder for existing approval system)."""
        # This would integrate with your existing approval workflow
        return {"approved": True, "reason": "Auto-approved for demo"}
    
    async def cleanup(self):
        """Cleanup MCP connections."""
        if self.mcp_manager:
            await self.mcp_manager.disconnect_all()
        logger.info("MCP workflow cleanup completed")