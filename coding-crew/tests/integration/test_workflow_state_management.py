"""Test workflow state management and transitions."""

import pytest
from unittest.mock import Mock

# Mock workflow stages
class MockWorkflowStage:
    ANALYSIS = "analysis"
    HUMAN_APPROVAL = "human_approval" 
    DEVELOPMENT = "development"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    COMPLETED = "completed"

# Mock workflow state
class MockWorkflowState:
    def __init__(self, workflow_id, requirements):
        self.workflow_id = workflow_id
        self.requirements = requirements
        self.stage = MockWorkflowStage.ANALYSIS
        self.approved = False
        self.completed = False
        self.analysis_result = None
        self.code_result = None
        self.test_result = None
        self.documentation_result = None

# Mock orchestrator
class MockOrchestrator:
    def __init__(self):
        self.workflows = {}
    
    def create_workflow(self, requirements):
        workflow_id = f"test-{len(self.workflows)}"
        self.workflows[workflow_id] = MockWorkflowState(workflow_id, requirements)
        return workflow_id
    
    def get_workflow(self, workflow_id):
        return self.workflows.get(workflow_id)
    
    def get_workflow_status(self, workflow_id):
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        return {
            "workflow_id": workflow.workflow_id,
            "stage": workflow.stage,
            "approved": workflow.approved,
            "completed": workflow.completed,
            "has_analysis": workflow.analysis_result is not None,
            "has_code": workflow.code_result is not None,
            "has_tests": workflow.test_result is not None,
            "has_documentation": workflow.documentation_result is not None
        }

class TestWorkflowStateManagement:
    
    def setup_method(self):
        """Setup test orchestrator."""
        self.orchestrator = MockOrchestrator()
    
    def test_workflow_creation_and_initial_state(self):
        """Test workflow creation and initial state."""
        requirements = "Build a web application"
        workflow_id = self.orchestrator.create_workflow(requirements)
        
        workflow = self.orchestrator.get_workflow(workflow_id)
        assert workflow is not None
        assert workflow.requirements == requirements
        assert workflow.stage == MockWorkflowStage.ANALYSIS
        assert workflow.approved == False
        assert workflow.completed == False
    
    def test_workflow_stage_transitions(self):
        """Test proper stage transitions through workflow."""
        workflow_id = self.orchestrator.create_workflow("Test app")
        workflow = self.orchestrator.get_workflow(workflow_id)
        
        # Analysis -> Human Approval -> Development
        workflow.analysis_result = {"analysis": "Complete"}
        workflow.stage = MockWorkflowStage.HUMAN_APPROVAL
        workflow.approved = True
        workflow.stage = MockWorkflowStage.DEVELOPMENT
        
        # Development -> Testing
        workflow.code_result = {"code": "Generated"}
        workflow.stage = MockWorkflowStage.TESTING
        
        # Testing -> Documentation
        workflow.test_result = {"tests": "Complete"}
        workflow.stage = MockWorkflowStage.DOCUMENTATION
        
        # Documentation -> Completed
        workflow.documentation_result = {"docs": "Generated"}
        workflow.stage = MockWorkflowStage.COMPLETED
        workflow.completed = True
        
        # Verify final state
        assert workflow.stage == MockWorkflowStage.COMPLETED
        assert workflow.completed == True
    
    def test_workflow_status_tracking(self):
        """Test workflow status tracking throughout phases."""
        workflow_id = self.orchestrator.create_workflow("Test requirements")
        
        # Initial status
        status = self.orchestrator.get_workflow_status(workflow_id)
        assert status["stage"] == "analysis"
        assert status["approved"] == False
        assert status["completed"] == False
        assert status["has_analysis"] == False
        
        # After analysis
        workflow = self.orchestrator.get_workflow(workflow_id)
        workflow.analysis_result = {"analysis": "Complete"}
        workflow.approved = True
        workflow.stage = MockWorkflowStage.DEVELOPMENT
        
        status = self.orchestrator.get_workflow_status(workflow_id)
        assert status["stage"] == "development"
        assert status["approved"] == True
        assert status["has_analysis"] == True
        assert status["has_code"] == False
        
        # After development
        workflow.code_result = {"code": "Generated"}
        workflow.stage = MockWorkflowStage.TESTING
        
        status = self.orchestrator.get_workflow_status(workflow_id)
        assert status["has_code"] == True
        assert status["has_tests"] == False
        
        # After testing
        workflow.test_result = {"tests": "Complete"}
        workflow.stage = MockWorkflowStage.DOCUMENTATION
        
        status = self.orchestrator.get_workflow_status(workflow_id)
        assert status["has_tests"] == True
        assert status["has_documentation"] == False
        
        # After documentation
        workflow.documentation_result = {"docs": "Generated"}
        workflow.stage = MockWorkflowStage.COMPLETED
        workflow.completed = True
        
        status = self.orchestrator.get_workflow_status(workflow_id)
        assert status["has_documentation"] == True
        assert status["completed"] == True
    
    def test_multiple_workflows_isolation(self):
        """Test that multiple workflows are properly isolated."""
        # Create multiple workflows
        id1 = self.orchestrator.create_workflow("App 1")
        id2 = self.orchestrator.create_workflow("App 2")
        
        # Modify first workflow
        workflow1 = self.orchestrator.get_workflow(id1)
        workflow1.analysis_result = {"analysis": "App 1 analysis"}
        workflow1.approved = True
        
        # Verify second workflow is unaffected
        workflow2 = self.orchestrator.get_workflow(id2)
        assert workflow2.analysis_result is None
        assert workflow2.approved == False
        
        # Verify status isolation
        status1 = self.orchestrator.get_workflow_status(id1)
        status2 = self.orchestrator.get_workflow_status(id2)
        
        assert status1["approved"] == True
        assert status2["approved"] == False
        assert status1["has_analysis"] == True
        assert status2["has_analysis"] == False
    
    def test_workflow_not_found(self):
        """Test handling of non-existent workflow."""
        status = self.orchestrator.get_workflow_status("invalid-id")
        assert "error" in status
        assert status["error"] == "Workflow not found"
        
        workflow = self.orchestrator.get_workflow("invalid-id")
        assert workflow is None