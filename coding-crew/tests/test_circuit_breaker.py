"""TDD tests for circuit breaker - failing tests first."""

import pytest
from unittest.mock import Mock
import time

class TestCircuitBreaker:
    
    def test_circuit_breaker_closed_state_success(self):
        """Test circuit breaker in closed state with successful calls."""
        from core.circuit_breaker import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=3, timeout=1.0)
        
        # Mock successful function
        mock_func = Mock(return_value="success")
        
        result = cb.call(mock_func)
        
        assert result == "success"
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0
    
    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        from core.circuit_breaker import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=2, timeout=1.0)
        
        # Mock failing function
        mock_func = Mock(side_effect=Exception("service down"))
        
        # First failure
        with pytest.raises(Exception):
            cb.call(mock_func)
        assert cb.state == "CLOSED"
        
        # Second failure - should open circuit
        with pytest.raises(Exception):
            cb.call(mock_func)
        assert cb.state == "OPEN"
    
    def test_circuit_breaker_open_state_fast_fail(self):
        """Test circuit breaker fast-fails when open."""
        from core.circuit_breaker import CircuitBreaker
        from core.circuit_breaker import CircuitBreakerOpenError
        
        cb = CircuitBreaker(failure_threshold=1, timeout=1.0)
        
        # Force circuit to open
        cb.state = "OPEN"
        cb.last_failure_time = time.time()
        
        mock_func = Mock()
        
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(mock_func)
        
        # Function should not be called
        mock_func.assert_not_called()
    
    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker transitions to half-open after timeout."""
        from core.circuit_breaker import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=1, timeout=0.1)
        
        # Force circuit to open
        cb.state = "OPEN"
        cb.last_failure_time = time.time() - 0.2  # Past timeout
        
        # Mock successful function
        mock_func = Mock(return_value="recovered")
        
        result = cb.call(mock_func)
        
        assert result == "recovered"
        assert cb.state == "CLOSED"