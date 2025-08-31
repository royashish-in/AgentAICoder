"""TDD tests for performance monitoring."""

import pytest
from unittest.mock import Mock
import time

class TestPerformanceMonitor:
    
    def test_execution_time_tracking(self):
        """Test tracking function execution time."""
        from core.performance_monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result, metrics = monitor.track_execution(slow_function)
        
        assert result == "done"
        assert metrics["execution_time"] >= 0.1
        assert "memory_usage" in metrics
    
    def test_memory_usage_tracking(self):
        """Test memory usage monitoring."""
        from core.performance_monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        def memory_function():
            # Allocate some memory
            data = [i for i in range(10000)]
            return len(data)
        
        result, metrics = monitor.track_execution(memory_function)
        
        assert result == 10000
        assert metrics["memory_usage"] > 0
        assert "peak_memory" in metrics
    
    def test_performance_threshold_alerts(self):
        """Test performance threshold monitoring."""
        from core.performance_monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor(time_threshold=0.05)
        
        def slow_function():
            time.sleep(0.1)  # Exceeds threshold
            return "slow"
        
        result, metrics = monitor.track_execution(slow_function)
        
        assert result == "slow"
        assert metrics["threshold_exceeded"] == True
        assert metrics["execution_time"] > 0.05