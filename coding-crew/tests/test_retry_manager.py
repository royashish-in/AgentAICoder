"""TDD tests for retry manager - write failing tests first."""

import pytest
from unittest.mock import Mock
import time

class TestRetryManager:
    
    def test_retry_success_on_first_attempt(self):
        """Test successful operation on first attempt."""
        # This test will fail until we implement RetryManager
        from core.retry_manager import RetryManager
        
        retry_manager = RetryManager(max_attempts=3, delay=0.1)
        
        # Mock function that succeeds immediately
        mock_func = Mock(return_value="success")
        
        result = retry_manager.execute(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test successful operation after initial failures."""
        from core.retry_manager import RetryManager
        
        retry_manager = RetryManager(max_attempts=3, delay=0.1)
        
        # Mock function that fails twice then succeeds
        mock_func = Mock(side_effect=[Exception("fail"), Exception("fail"), "success"])
        
        result = retry_manager.execute(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_exhausted_attempts(self):
        """Test retry exhaustion after max attempts."""
        from core.retry_manager import RetryManager
        
        retry_manager = RetryManager(max_attempts=2, delay=0.1)
        
        # Mock function that always fails
        mock_func = Mock(side_effect=Exception("always fails"))
        
        with pytest.raises(Exception, match="always fails"):
            retry_manager.execute(mock_func)
        
        assert mock_func.call_count == 2
    
    def test_exponential_backoff(self):
        """Test exponential backoff delay calculation."""
        from core.retry_manager import RetryManager
        
        retry_manager = RetryManager(max_attempts=3, delay=0.1, exponential=True)
        
        # Test delay calculation
        assert retry_manager._calculate_delay(0) == 0.1
        assert retry_manager._calculate_delay(1) == 0.2
        assert retry_manager._calculate_delay(2) == 0.4