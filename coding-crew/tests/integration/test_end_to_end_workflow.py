"""End-to-end workflow integration tests."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from core.crew_workflow import CrewWorkflowOrchestrator, WorkflowStage

class TestEndToEndWorkflow:
    
    def setup_method(self):
        """Setup test orchestrator."""
        self.orchestrator = CrewWorkflowOrchestrator()
    
    def test_workflow_creation(self):
        """Test workflow creation and initial state."""
        requirements = "Build a simple web application"
        workflow_id = self.orchestrator.create_workflow(requirements)
        
        workflow = self.orchestrator.get_workflow(workflow_id)
        assert workflow is not None
        assert workflow.requirements == requirements
        assert workflow.stage == WorkflowStage.ANALYSIS
        assert workflow.approved == False
        assert workflow.completed == False
    
    @patch('core.crew_workflow.Crew')
    @patch('core.crew_workflow.DiagramIntegration')
    @patch('core.crew_workflow.ApprovalClient')
    def test_analysis_phase_success(self, mock_approval, mock_diagram, mock_crew_class):
        """Test successful analysis phase execution."""
        # Setup mocks
        mock_crew = Mock()
        mock_crew_class.return_value = mock_crew
        mock_crew.kickoff.return_value = Mock(raw="Analysis complete")
        
        mock_diagram_instance = Mock()
        mock_diagram.return_value = mock_diagram_instance
        mock_diagram_instance.enhance_analysis_with_diagrams.return_value = "Enhanced analysis"
        
        mock_approval_instance = Mock()
        mock_approval.return_value = mock_approval_instance
        mock_approval_instance.submit_for_approval.return_value = "approval-123"
        mock_approval_instance.wait_for_approval.return_value = {"approved": True, "feedback": "Good"}
        
        # Create workflow and run analysis
        workflow_id = self.orchestrator.create_workflow("Test requirements")
        
        # Run analysis phase
        result = asyncio.run(self.orchestrator.run_analysis_phase(workflow_id))
        
        # Verify results
        assert result is not None
        assert "analysis_output" in result
        workflow = self.orchestrator.get_workflow(workflow_id)
        assert workflow.approved == True
        assert workflow.stage == WorkflowStage.DEVELOPMENT
    
    @patch('core.development_workflow.Crew')
    def test_development_phase_success(self, mock_crew_class):
        """Test successful development phase execution."""
        # Setup mock
        mock_crew = Mock()
        mock_crew_class.return_value = mock_crew
        mock_crew.kickoff.return_value = Mock(raw="Generated code")
        
        # Create workflow with approved analysis
        workflow_id = self.orchestrator.create_workflow("Test requirements")
        workflow = self.orchestrator.get_workflow(workflow_id)
        workflow.analysis_result = {"analysis_output": "Test analysis"}
        workflow.approved = True
        workflow.stage = WorkflowStage.DEVELOPMENT
        
        # Run development phase
        result = asyncio.run(self.orchestrator.run_development_phase(workflow_id))
        
        # Verify results
        assert result is not None
        assert "code_output" in result
        workflow = self.orchestrator.get_workflow(workflow_id)
        assert workflow.stage == WorkflowStage.TESTING
    
    @patch('core.testing_workflow.Crew')
    def test_testing_phase_success(self, mock_crew_class):
        """Test successful testing phase execution."""
        # Setup mock
        mock_crew = Mock()
        mock_crew_class.return_value = mock_crew
        mock_crew.kickoff.return_value = Mock(raw="Tests generated - 85% coverage, all tests passed")
        
        # Create workflow with code result
        workflow_id = self.orchestrator.create_workflow("Test requirements")
        workflow = self.orchestrator.get_workflow(workflow_id)
        workflow.code_result = {"code_output": "Test code"}
        workflow.stage = WorkflowStage.TESTING
        
        # Run testing phase
        result = asyncio.run(self.orchestrator.run_testing_phase(workflow_id))
        
        # Verify results
        assert result is not None
        assert "test_output" in result
        assert "coverage" in result
        workflow = self.orchestrator.get_workflow(workflow_id)
        assert workflow.stage == WorkflowStage.DOCUMENTATION
    
    @patch('core.documentation_workflow.Crew')
    def test_documentation_phase_success(self, mock_crew_class):
        """Test successful documentation phase execution."""
        # Setup mock
        mock_crew = Mock()
        mock_crew_class.return_value = mock_crew
        mock_crew.kickoff.return_value = Mock(raw="Documentation generated")
        
        # Create workflow with test result
        workflow_id = self.orchestrator.create_workflow("Test requirements")
        workflow = self.orchestrator.get_workflow(workflow_id)
        workflow.code_result = {"code_output": "Test code"}
        workflow.test_result = {"test_output": "Test results"}
        workflow.stage = WorkflowStage.DOCUMENTATION
        
        # Run documentation phase
        result = asyncio.run(self.orchestrator.run_documentation_phase(workflow_id))
        
        # Verify results
        assert result is not None
        assert "doc_output" in result
        workflow = self.orchestrator.get_workflow(workflow_id)
        assert workflow.stage == WorkflowStage.COMPLETED
        assert workflow.completed == True
    
    def test_workflow_status_tracking(self):
        """Test workflow status tracking throughout phases."""
        workflow_id = self.orchestrator.create_workflow("Test requirements")
        
        # Initial status
        status = self.orchestrator.get_workflow_status(workflow_id)
        assert status["stage"] == "analysis"
        assert status["approved"] == False
        assert status["completed"] == False
        
        # Simulate phase progression
        workflow = self.orchestrator.get_workflow(workflow_id)
        workflow.analysis_result = {"analysis_output": "Test"}
        workflow.approved = True
        workflow.stage = WorkflowStage.DEVELOPMENT
        
        status = self.orchestrator.get_workflow_status(workflow_id)
        assert status["stage"] == "development"
        assert status["approved"] == True
        assert status["has_analysis"] == True
    
    def test_error_handling_invalid_workflow(self):
        """Test error handling for invalid workflow operations."""
        # Test non-existent workflow
        with pytest.raises(ValueError):
            asyncio.run(self.orchestrator.run_development_phase("invalid-id"))
        
        # Test unapproved workflow
        workflow_id = self.orchestrator.create_workflow("Test")
        with pytest.raises(ValueError):
            asyncio.run(self.orchestrator.run_development_phase(workflow_id))