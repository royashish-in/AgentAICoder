"""TDD tests for centralized error handler."""

import pytest
from unittest.mock import Mock

class TestErrorHandler:
    
    def test_handle_transient_error_with_retry(self):
        """Test handling transient errors with retry."""
        from core.error_handler import ErrorHandler
        
        handler = ErrorHandler()
        
        # Mock function that fails once then succeeds
        mock_func = Mock(side_effect=[ConnectionError("network"), "success"])
        
        result = handler.handle_with_recovery(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 2
    
    def test_handle_permanent_error_no_retry(self):
        """Test handling permanent errors without retry."""
        from core.error_handler import ErrorHandler
        
        handler = ErrorHandler()
        
        # Mock function with permanent error
        mock_func = Mock(side_effect=ValueError("invalid input"))
        
        with pytest.raises(ValueError):
            handler.handle_with_recovery(mock_func)
        
        assert mock_func.call_count == 1  # No retry for permanent errors
    
    def test_circuit_breaker_integration(self):
        """Test error handler integrates with circuit breaker."""
        from core.error_handler import ErrorHandler
        
        handler = ErrorHandler(use_circuit_breaker=True)
        
        # Mock function that always fails
        mock_func = Mock(side_effect=Exception("service down"))
        
        # Should fail multiple times then circuit break
        for _ in range(3):
            with pytest.raises(Exception):
                handler.handle_with_recovery(mock_func)
        
        # Circuit should now be open
        from core.circuit_breaker import CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            handler.handle_with_recovery(mock_func)