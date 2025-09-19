"""Enhanced workflow with MCP integration."""

from typing import Dict, Any, Optional
from loguru import logger

from .workflow import WorkflowOrchestrator, WorkflowStage
from .mcp_service import MCPService


class EnhancedWorkflowOrchestrator(WorkflowOrchestrator):
    """Workflow orchestrator enhanced with MCP integration."""
    
    def __init__(self):
        super().__init__()
        self.mcp_service = MCPService()
        self.mcp_initialized = False
    
    async def initialize_mcp(self) -> bool:
        """Initialize MCP services."""
        self.mcp_initialized = await self.mcp_service.initialize()
        if self.mcp_initialized:
            logger.info("MCP services initialized successfully")
        else:
            logger.info("MCP services not available, using standard workflow")
        return self.mcp_initialized
    
    async def create_enhanced_workflow(self, requirements: str, project_name: str) -> str:
        """Create workflow with MCP context."""
        workflow_id = self.create_workflow(requirements)
        
        # Add MCP context if available
        if self.mcp_initialized:
            try:
                context = await self.mcp_service.get_project_context(project_name)
                self.update_workflow(workflow_id, data={
                    "requirements": requirements,
                    "project_name": project_name,
                    "mcp_context": context
                })
                logger.info(f"Added MCP context to workflow {workflow_id}")
            except Exception as e:
                logger.error(f"Failed to get MCP context: {e}")
        
        return workflow_id
    
    async def execute_development_with_artifacts(self, workflow_id: str) -> Dict[str, Any]:
        """Execute development phase with MCP artifact creation."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        results = {"artifacts_created": False}
        
        # Create external artifacts if MCP is available
        if self.mcp_initialized and workflow.data.get("project_name"):
            try:
                project_data = {
                    "name": workflow.data["project_name"],
                    "description": workflow.data.get("requirements", ""),
                    "create_jira_issue": True,
                    "create_github_repo": True
                }
                
                artifacts = await self.mcp_service.create_project_artifacts(project_data)
                results["external_artifacts"] = artifacts
                results["artifacts_created"] = bool(artifacts)
                
                # Update workflow with artifact info
                workflow_data = workflow.data.copy()
                workflow_data["external_artifacts"] = artifacts
                self.update_workflow(workflow_id, data=workflow_data)
                
                logger.info(f"Created external artifacts for workflow {workflow_id}")
                
            except Exception as e:
                logger.error(f"Failed to create external artifacts: {e}")
                results["error"] = str(e)
        
        return results
    
    async def cleanup(self):
        """Cleanup MCP connections."""
        if self.mcp_service:
            await self.mcp_service.cleanup()
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """Get MCP service status."""
        return {
            "initialized": self.mcp_initialized,
            "available": self.mcp_service.is_available() if self.mcp_service else False
        }