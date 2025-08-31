"""Tests for CrewAI workflow orchestrator."""

import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crew_workflow import CrewWorkflowOrchestrator, WorkflowStage


class TestCrewWorkflowOrchestrator:
    """Test cases for CrewWorkflowOrchestrator."""
    
    def test_create_workflow(self):
        """Test CrewAI workflow creation."""
        orchestrator = CrewWorkflowOrchestrator()
        requirements = "Build a web application with user authentication"
        
        workflow_id = orchestrator.create_workflow(requirements)
        
        assert workflow_id is not None
        assert len(workflow_id) > 0
        assert workflow_id in orchestrator.workflows
        
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow is not None
        assert workflow.stage == WorkflowStage.ANALYSIS
        assert workflow.requirements == requirements
        assert workflow.approved is False
        assert workflow.completed is False
    
    def test_get_workflow_not_found(self):
        """Test getting non-existent workflow."""
        orchestrator = CrewWorkflowOrchestrator()
        
        result = orchestrator.get_workflow("non_existent_id")
        
        assert result is None
    
    def test_approve_analysis(self):
        """Test analysis approval."""
        orchestrator = CrewWorkflowOrchestrator()
        workflow_id = orchestrator.create_workflow("Test requirements")
        
        # Simulate analysis completion
        workflow = orchestrator.get_workflow(workflow_id)
        workflow.stage = WorkflowStage.HUMAN_APPROVAL
        
        # Test approval
        orchestrator.approve_analysis(workflow_id, True)
        
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow.approved is True
        assert workflow.stage == WorkflowStage.DEVELOPMENT
    
    def test_reject_analysis(self):
        """Test analysis rejection."""
        orchestrator = CrewWorkflowOrchestrator()
        workflow_id = orchestrator.create_workflow("Test requirements")
        
        # Simulate analysis completion
        workflow = orchestrator.get_workflow(workflow_id)
        workflow.stage = WorkflowStage.HUMAN_APPROVAL
        
        # Test rejection
        orchestrator.approve_analysis(workflow_id, False)
        
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow.approved is False
        assert workflow.stage == WorkflowStage.ANALYSIS
    
    def test_get_workflow_status(self):
        """Test workflow status retrieval."""
        orchestrator = CrewWorkflowOrchestrator()
        workflow_id = orchestrator.create_workflow("Test requirements")
        
        status = orchestrator.get_workflow_status(workflow_id)
        
        assert status["workflow_id"] == workflow_id
        assert status["stage"] == "analysis"
        assert status["approved"] is False
        assert status["completed"] is False
        assert status["has_analysis"] is False
        assert status["has_code"] is False
        assert status["has_tests"] is False
        assert status["has_documentation"] is False
    
    def test_get_workflow_status_not_found(self):
        """Test workflow status for non-existent workflow."""
        orchestrator = CrewWorkflowOrchestrator()
        
        status = orchestrator.get_workflow_status("non_existent_id")
        
        assert "error" in status
        assert status["error"] == "Workflow not found"