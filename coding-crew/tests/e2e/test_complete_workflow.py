"""End-to-end workflow tests."""

import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.crew_workflow import CrewWorkflowOrchestrator, WorkflowStage


class TestCompleteWorkflow:
    """Test complete workflow scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_simple_web_app_workflow(self):
        """Test complete workflow for simple web app."""
        orchestrator = CrewWorkflowOrchestrator()
        
        # Create workflow
        requirements = """
        # Simple Web Application
        
        Build a web application with the following features:
        - User registration and login system
        - User dashboard with profile management
        - Basic CRUD operations for user data
        - Responsive design for mobile and desktop
        - SQLite database for data storage
        """
        
        workflow_id = orchestrator.create_workflow(requirements)
        workflow = orchestrator.get_workflow(workflow_id)
        
        assert workflow is not None
        assert workflow.stage == WorkflowStage.ANALYSIS
        assert workflow.requirements == requirements
        
        # Test workflow status
        status = orchestrator.get_workflow_status(workflow_id)
        assert status["stage"] == "analysis"
        assert status["has_analysis"] is False
        
        # Note: Actual CrewAI execution would require Ollama running
        # This test validates the workflow structure without LLM calls
    
    def test_workflow_state_transitions(self):
        """Test workflow state transitions."""
        orchestrator = CrewWorkflowOrchestrator()
        
        # Create workflow
        workflow_id = orchestrator.create_workflow("Build an API service")
        
        # Test initial state
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow.stage == WorkflowStage.ANALYSIS
        
        # Simulate analysis completion
        workflow.stage = WorkflowStage.HUMAN_APPROVAL
        workflow.analysis_result = {"analysis_complete": True}
        
        # Test approval
        orchestrator.approve_analysis(workflow_id, True)
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow.approved is True
        assert workflow.stage == WorkflowStage.DEVELOPMENT
        
        # Test rejection
        workflow.stage = WorkflowStage.HUMAN_APPROVAL
        orchestrator.approve_analysis(workflow_id, False)
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow.approved is False
        assert workflow.stage == WorkflowStage.ANALYSIS
    
    def test_workflow_error_handling(self):
        """Test workflow error handling."""
        orchestrator = CrewWorkflowOrchestrator()
        
        # Test invalid workflow operations
        with pytest.raises(ValueError, match="not found"):
            orchestrator.approve_analysis("invalid-id", True)
        
        # Test workflow status for non-existent workflow
        status = orchestrator.get_workflow_status("invalid-id")
        assert "error" in status
        assert status["error"] == "Workflow not found"
    
    def test_multiple_workflows(self):
        """Test handling multiple concurrent workflows."""
        orchestrator = CrewWorkflowOrchestrator()
        
        # Create multiple workflows
        workflow_ids = []
        for i in range(3):
            requirements = f"Build application {i+1}"
            workflow_id = orchestrator.create_workflow(requirements)
            workflow_ids.append(workflow_id)
        
        # Verify all workflows exist
        assert len(orchestrator.workflows) == 3
        
        for workflow_id in workflow_ids:
            workflow = orchestrator.get_workflow(workflow_id)
            assert workflow is not None
            assert workflow.stage == WorkflowStage.ANALYSIS
        
        # Test independent workflow operations
        orchestrator.workflows[workflow_ids[0]].stage = WorkflowStage.HUMAN_APPROVAL
        orchestrator.approve_analysis(workflow_ids[0], True)
        
        # Verify only first workflow is approved
        assert orchestrator.get_workflow(workflow_ids[0]).approved is True
        assert orchestrator.get_workflow(workflow_ids[1]).approved is False
        assert orchestrator.get_workflow(workflow_ids[2]).approved is False