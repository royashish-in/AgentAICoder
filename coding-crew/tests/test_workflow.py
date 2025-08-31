"""Tests for workflow orchestrator."""

import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.workflow import WorkflowOrchestrator, WorkflowStage


class TestWorkflowOrchestrator:
    """Test cases for WorkflowOrchestrator."""
    
    def test_create_workflow(self):
        """Test workflow creation."""
        orchestrator = WorkflowOrchestrator()
        requirements = "Test requirements"
        
        workflow_id = orchestrator.create_workflow(requirements)
        
        assert workflow_id is not None
        assert len(workflow_id) > 0
        assert workflow_id in orchestrator.workflows
        
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow is not None
        assert workflow.stage == WorkflowStage.ANALYSIS
        assert workflow.data["requirements"] == requirements
    
    def test_get_workflow_not_found(self):
        """Test getting non-existent workflow."""
        orchestrator = WorkflowOrchestrator()
        
        result = orchestrator.get_workflow("non_existent_id")
        
        assert result is None
    
    def test_update_workflow(self):
        """Test workflow update."""
        orchestrator = WorkflowOrchestrator()
        workflow_id = orchestrator.create_workflow("Test")
        
        orchestrator.update_workflow(workflow_id, approved=True)
        
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow.approved is True
    
    def test_advance_stage(self):
        """Test stage advancement."""
        orchestrator = WorkflowOrchestrator()
        workflow_id = orchestrator.create_workflow("Test")
        
        orchestrator.advance_stage(workflow_id, WorkflowStage.HUMAN_APPROVAL)
        
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow.stage == WorkflowStage.HUMAN_APPROVAL
        assert workflow.iteration_count == 0
    
    def test_increment_iteration(self):
        """Test iteration increment."""
        orchestrator = WorkflowOrchestrator()
        workflow_id = orchestrator.create_workflow("Test")
        
        # Test normal increment
        max_reached = orchestrator.increment_iteration(workflow_id)
        assert max_reached is False
        
        workflow = orchestrator.get_workflow(workflow_id)
        assert workflow.iteration_count == 1
        
        # Test max iterations reached
        workflow.iteration_count = 4
        max_reached = orchestrator.increment_iteration(workflow_id)
        assert max_reached is True
        assert workflow.iteration_count == 5