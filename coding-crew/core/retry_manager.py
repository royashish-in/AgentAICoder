"""Retry manager with exponential backoff."""

import time
from typing import Callable, Any

class RetryManager:
    """Manages retry logic with configurable backoff."""
    
    def __init__(self, max_attempts: int = 3, delay: float = 1.0, exponential: bool = False):
        self.max_attempts = max_attempts
        self.delay = delay
        self.exponential = exponential
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Don't sleep on last attempt
                if attempt < self.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
        
        # Re-raise the last exception if all attempts failed
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt."""
        if self.exponential:
            return self.delay * (2 ** attempt)
        return self.delay