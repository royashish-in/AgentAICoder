"""Workflow orchestrator for managing agent interactions."""

from typing import Dict, Any, List, Optional
from uuid import uuid4
from enum import Enum
from loguru import logger
from pydantic import BaseModel
import time
import asyncio

from .mcp_integration import MCPIntegration


class WorkflowStage(Enum):
    """Workflow stages."""
    ANALYSIS = "analysis"
    HUMAN_APPROVAL = "human_approval"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    COMPLETED = "completed"


class WorkflowState(BaseModel):
    """Workflow state tracking."""
    workflow_id: str
    correlation_id: str
    stage: WorkflowStage
    iteration_count: int
    max_iterations: int
    data: Dict[str, Any]
    approved: bool = False
    completed: bool = False
    error_message: Optional[str] = None
    created_at: float = 0
    updated_at: float = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.created_at:
            self.created_at = time.time()
        self.updated_at = time.time()


class WorkflowOrchestrator:
    """Orchestrates the multi-agent workflow."""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowState] = {}
        self.mcp = MCPIntegration()
        
    def create_workflow(self, requirements: str) -> str:
        """Create a new workflow."""
        workflow_id = str(uuid4())
        correlation_id = f"workflow_{workflow_id[:8]}"
        
        state = WorkflowState(
            workflow_id=workflow_id,
            correlation_id=correlation_id,
            stage=WorkflowStage.ANALYSIS,
            iteration_count=0,
            max_iterations=5,
            data={"requirements": requirements}
        )
        
        self.workflows[workflow_id] = state
        
        logger.info(
            f"Created workflow {workflow_id}",
            extra={
                "workflow_id": workflow_id,
                "correlation_id": correlation_id,
                "stage": state.stage.value
            }
        )
        
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state."""
        return self.workflows.get(workflow_id)
    
    def update_workflow(self, workflow_id: str, **updates) -> None:
        """Update workflow state."""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            
            # Validate updates against Pydantic model
            for key, value in updates.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)
            
            workflow.updated_at = time.time()
            
            logger.info(
                f"Updated workflow {workflow_id}",
                extra={
                    "workflow_id": workflow_id,
                    "correlation_id": workflow.correlation_id,
                    "updates": updates
                }
            )
    
    def advance_stage(self, workflow_id: str, next_stage: WorkflowStage) -> None:
        """Advance workflow to next stage."""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow {workflow_id} not found for stage advancement")
            return
            
        workflow = self.workflows[workflow_id]
        old_stage = workflow.stage
        workflow.stage = next_stage
        workflow.iteration_count = 0  # Reset iteration count for new stage
        workflow.updated_at = time.time()
        
        logger.info(
            f"Advanced workflow {workflow_id} from {old_stage.value} to {next_stage.value}",
            extra={
                "workflow_id": workflow_id,
                "correlation_id": workflow.correlation_id,
                "old_stage": old_stage.value,
                "new_stage": next_stage.value
            }
        )
    
    def increment_iteration(self, workflow_id: str) -> bool:
        """Increment iteration count and check if max reached."""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow {workflow_id} not found for iteration increment")
            return True
            
        workflow = self.workflows[workflow_id]
        workflow.iteration_count += 1
        workflow.updated_at = time.time()
        
        max_reached = workflow.iteration_count >= workflow.max_iterations
        
        logger.info(
            f"Incremented iteration for workflow {workflow_id}",
            extra={
                "workflow_id": workflow_id,
                "correlation_id": workflow.correlation_id,
                "iteration": workflow.iteration_count,
                "max_iterations": workflow.max_iterations,
                "max_reached": max_reached
            }
        )
        
        return max_reached
    
    def set_workflow_error(self, workflow_id: str, error_message: str) -> None:
        """Set workflow error state."""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow.error_message = error_message
            workflow.updated_at = time.time()
            
            logger.error(
                f"Workflow {workflow_id} error: {error_message}",
                extra={
                    "workflow_id": workflow_id,
                    "correlation_id": workflow.correlation_id,
                    "error": error_message
                }
            )
    
    def clear_workflow_error(self, workflow_id: str) -> None:
        """Clear workflow error state."""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow.error_message = None
            workflow.updated_at = time.time()
            
            logger.info(f"Cleared error for workflow {workflow_id}")
    
    def reset_workflow(self, workflow_id: str) -> None:
        """Reset workflow to analysis stage."""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow.stage = WorkflowStage.ANALYSIS
            workflow.iteration_count = 0
            workflow.approved = False
            workflow.completed = False
            workflow.error_message = None
            workflow.updated_at = time.time()
            
            logger.info(f"Reset workflow {workflow_id} to analysis stage")
    
    async def create_workflow_with_context(self, requirements: str, project_name: str = None) -> str:
        """Create workflow with MCP context if available."""
        workflow_id = self.create_workflow(requirements)
        
        if project_name and self.mcp.enabled:
            try:
                context = await self.mcp.get_project_context(project_name)
                self.update_workflow(workflow_id, data={
                    "requirements": requirements,
                    "project_name": project_name,
                    "mcp_context": context
                })
                logger.info(f"Added MCP context to workflow {workflow_id}")
            except Exception as e:
                logger.error(f"Failed to get MCP context: {e}")
        
        return workflow_id
    
    async def create_external_artifacts(self, workflow_id: str) -> Dict[str, Any]:
        """Create external artifacts for workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow or not self.mcp.enabled:
            return {"created": False, "reason": "MCP not available"}
        
        project_data = {
            "name": workflow.data.get("project_name", "Unknown Project"),
            "description": workflow.data.get("requirements", "")
        }
        
        try:
            artifacts = await self.mcp.create_project_artifacts(project_data)
            
            # Update workflow with artifacts
            workflow_data = workflow.data.copy()
            workflow_data["external_artifacts"] = artifacts
            self.update_workflow(workflow_id, data=workflow_data)
            
            return {"created": True, "artifacts": artifacts}
        except Exception as e:
            logger.error(f"Failed to create external artifacts: {e}")
            return {"created": False, "error": str(e)}