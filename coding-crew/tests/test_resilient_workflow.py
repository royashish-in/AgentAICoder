"""TDD tests for resilient workflow integration."""

import pytest
from unittest.mock import Mock, patch

class TestResilientWorkflow:
    
    def test_llm_call_with_retry_on_failure(self):
        """Test LLM calls retry on transient failures."""
        from core.resilient_workflow import ResilientWorkflowOrchestrator
        
        orchestrator = ResilientWorkflowOrchestrator()
        
        # Mock LLM that fails once then succeeds
        with patch('crewai.Crew') as mock_crew_class:
            mock_crew = Mock()
            mock_crew_class.return_value = mock_crew
            mock_crew.kickoff.side_effect = [ConnectionError("network"), Mock(raw="success")]
            
            workflow_id = orchestrator.create_workflow("test requirements")
            
            # Should retry and succeed
            result = orchestrator._execute_crew_with_resilience(mock_crew)
            
            assert result.raw == "success"
            assert mock_crew.kickoff.call_count == 2
    
    def test_circuit_breaker_protects_llm_calls(self):
        """Test circuit breaker protects against repeated LLM failures."""
        from core.resilient_workflow import ResilientWorkflowOrchestrator
        from core.circuit_breaker import CircuitBreakerOpenError
        
        orchestrator = ResilientWorkflowOrchestrator(use_circuit_breaker=True)
        
        with patch('crewai.Crew') as mock_crew_class:
            mock_crew = Mock()
            mock_crew_class.return_value = mock_crew
            mock_crew.kickoff.side_effect = Exception("service down")
            
            # Multiple failures should open circuit
            for _ in range(3):
                with pytest.raises(Exception):
                    orchestrator._execute_crew_with_resilience(mock_crew)
            
            # Circuit should now be open
            with pytest.raises(CircuitBreakerOpenError):
                orchestrator._execute_crew_with_resilience(mock_crew)
    
    def test_workflow_recovery_from_failure(self):
        """Test workflow can recover from phase failures."""
        from core.resilient_workflow import ResilientWorkflowOrchestrator
        
        orchestrator = ResilientWorkflowOrchestrator()
        
        workflow_id = orchestrator.create_workflow("test requirements")
        
        # Mock the error handler to simulate retry behavior
        with patch.object(orchestrator.error_handler, 'handle_with_recovery') as mock_handler:
            mock_result = Mock()
            mock_result.raw = "recovered"
            mock_handler.return_value = mock_result
            
            # Should recover from failure
            result = orchestrator._run_analysis_with_recovery(workflow_id)
            
            assert "recovered" in str(result["analysis_output"])
            assert mock_handler.call_count == 1