"""Centralized error handling and recovery."""

from typing import Callable, Any
from .retry_manager import RetryManager
from .circuit_breaker import CircuitBreaker

class ErrorHandler:
    """Centralized error handling with retry and circuit breaker."""
    
    def __init__(self, use_circuit_breaker: bool = False):
        self.retry_manager = RetryManager(max_attempts=3, delay=0.1)
        self.circuit_breaker = CircuitBreaker(failure_threshold=3) if use_circuit_breaker else None
    
    def handle_with_recovery(self, func: Callable, *args, **kwargs) -> Any:
        """Handle function execution with error recovery."""
        
        def execute_func():
            if self.circuit_breaker:
                return self.circuit_breaker.call(func, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        # Check if error is retryable
        try:
            return execute_func()
        except Exception as e:
            if self._is_retryable_error(e):
                return self.retry_manager.execute(execute_func)
            else:
                raise e
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if error is retryable."""
        retryable_errors = (ConnectionError, TimeoutError, OSError)
        return isinstance(error, retryable_errors)