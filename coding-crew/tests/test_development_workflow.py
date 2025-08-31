"""Tests for development workflow."""

import pytest
from unittest.mock import Mock, patch
from core.development_workflow import DevelopmentWorkflow

class TestDevelopmentWorkflow:
    
    def setup_method(self):
        """Setup test workflow."""
        self.workflow = DevelopmentWorkflow(max_iterations=3)
    
    def test_workflow_initialization(self):
        """Test workflow initialization."""
        assert self.workflow.max_iterations == 3
        assert self.workflow.coding_agent is not None
        assert self.workflow.review_agent is not None
    
    def test_is_code_approved_positive(self):
        """Test code approval detection - positive cases."""
        approved_reviews = [
            "Code is approved and ready for production",
            "Meets quality standards, no critical issues found",
            "Acceptable quality, ready to proceed"
        ]
        
        for review in approved_reviews:
            assert self.workflow._is_code_approved(review) == True
    
    def test_is_code_approved_negative(self):
        """Test code approval detection - negative cases."""
        rejected_reviews = [
            "Critical security vulnerabilities found",
            "Code needs significant improvements",
            "Multiple issues require attention"
        ]
        
        for review in rejected_reviews:
            assert self.workflow._is_code_approved(review) == False
    
    def test_is_code_approved_empty(self):
        """Test code approval with empty review."""
        assert self.workflow._is_code_approved("") == False
        assert self.workflow._is_code_approved(None) == False
    
    @patch('core.development_workflow.Crew')
    def test_generate_code_success(self, mock_crew_class):
        """Test successful code generation."""
        # Setup mock
        mock_crew = Mock()
        mock_crew_class.return_value = mock_crew
        mock_result = Mock()
        mock_result.raw = "Generated code content"
        mock_crew.kickoff.return_value = mock_result
        
        # Test code generation
        result = self.workflow._generate_code("Sample analysis")
        
        assert result == "Generated code content"
        mock_crew.kickoff.assert_called_once()
    
    @patch('core.development_workflow.Crew')
    def test_review_code_success(self, mock_crew_class):
        """Test successful code review."""
        # Setup mock
        mock_crew = Mock()
        mock_crew_class.return_value = mock_crew
        mock_result = Mock()
        mock_result.raw = "Code review results"
        mock_crew.kickoff.return_value = mock_result
        
        # Test code review
        result = self.workflow._review_code("Sample code")
        
        assert result == "Code review results"
        mock_crew.kickoff.assert_called_once()
    
    @patch.object(DevelopmentWorkflow, '_generate_code')
    @patch.object(DevelopmentWorkflow, '_review_code')
    @patch.object(DevelopmentWorkflow, '_is_code_approved')
    def test_development_cycle_approved_first_iteration(self, mock_approved, mock_review, mock_generate):
        """Test development cycle with approval on first iteration."""
        # Setup mocks
        mock_generate.return_value = "Generated code"
        mock_review.return_value = "Code approved"
        mock_approved.return_value = True
        
        # Run development cycle
        result = self.workflow.run_development_cycle("Sample analysis")
        
        # Verify results
        assert result["iterations"] == 1
        assert result["approved"] == True
        assert result["max_iterations_reached"] == False
        assert mock_generate.call_count == 1
        assert mock_review.call_count == 1
    
    @patch.object(DevelopmentWorkflow, '_generate_code')
    @patch.object(DevelopmentWorkflow, '_review_code')
    @patch.object(DevelopmentWorkflow, '_is_code_approved')
    def test_development_cycle_max_iterations(self, mock_approved, mock_review, mock_generate):
        """Test development cycle reaching max iterations."""
        # Setup mocks - never approve
        mock_generate.return_value = "Generated code"
        mock_review.return_value = "Code needs improvement"
        mock_approved.return_value = False
        
        # Run development cycle
        result = self.workflow.run_development_cycle("Sample analysis")
        
        # Verify results
        assert result["iterations"] == 3  # max_iterations
        assert result["approved"] == False
        assert result["max_iterations_reached"] == True
        assert mock_generate.call_count == 3
        assert mock_review.call_count == 3