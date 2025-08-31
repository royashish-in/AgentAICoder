"""TDD tests for structured logging with correlation IDs."""

import pytest
from unittest.mock import Mock, patch
import json

class TestStructuredLogger:
    
    def test_correlation_id_generation(self):
        """Test correlation ID is generated for each request."""
        from core.structured_logger import StructuredLogger
        
        logger = StructuredLogger()
        
        correlation_id = logger.generate_correlation_id()
        
        assert correlation_id is not None
        assert len(correlation_id) == 36  # UUID length
        assert isinstance(correlation_id, str)
    
    def test_structured_log_format(self):
        """Test logs are structured with correlation ID."""
        from core.structured_logger import StructuredLogger
        
        logger = StructuredLogger()
        
        with patch('loguru.logger.info') as mock_log:
            logger.log_workflow_event(
                correlation_id="test-123",
                event="workflow_started",
                workflow_id="wf-456",
                stage="analysis"
            )
            
            # Verify structured log was called
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0][0]
            
            # Parse JSON log
            log_data = json.loads(call_args)
            assert log_data["correlation_id"] == "test-123"
            assert log_data["event"] == "workflow_started"
            assert log_data["workflow_id"] == "wf-456"
            assert log_data["stage"] == "analysis"
    
    def test_performance_metrics_logging(self):
        """Test performance metrics are logged with correlation."""
        from core.structured_logger import StructuredLogger
        
        logger = StructuredLogger()
        
        with patch('loguru.logger.info') as mock_log:
            logger.log_performance_metrics(
                correlation_id="perf-123",
                operation="llm_call",
                duration=2.5,
                memory_usage=1024
            )
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0][0]
            
            log_data = json.loads(call_args)
            assert log_data["correlation_id"] == "perf-123"
            assert log_data["operation"] == "llm_call"
            assert log_data["duration"] == 2.5
            assert log_data["memory_usage"] == 1024
    
    def test_error_logging_with_context(self):
        """Test error logging includes full context."""
        from core.structured_logger import StructuredLogger
        
        logger = StructuredLogger()
        
        with patch('loguru.logger.error') as mock_log:
            logger.log_error(
                correlation_id="err-123",
                error="Connection failed",
                workflow_id="wf-789",
                stage="development",
                retry_count=2
            )
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0][0]
            
            log_data = json.loads(call_args)
            assert log_data["correlation_id"] == "err-123"
            assert log_data["error"] == "Connection failed"
            assert log_data["workflow_id"] == "wf-789"
            assert log_data["retry_count"] == 2