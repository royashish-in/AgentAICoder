"""Structured logging with correlation IDs."""

import json
import uuid
from typing import Dict, Any, Optional
from loguru import logger

class StructuredLogger:
    """Structured logger with correlation ID tracking."""
    
    def generate_correlation_id(self) -> str:
        """Generate unique correlation ID."""
        return str(uuid.uuid4())
    
    def log_workflow_event(self, correlation_id: str, event: str, 
                          workflow_id: str, stage: str, **kwargs):
        """Log workflow events with structured format."""
        log_data = {
            "correlation_id": correlation_id,
            "event": event,
            "workflow_id": workflow_id,
            "stage": stage,
            **kwargs
        }
        logger.info(json.dumps(log_data))
    
    def log_performance_metrics(self, correlation_id: str, operation: str,
                               duration: float, memory_usage: int, **kwargs):
        """Log performance metrics with correlation."""
        log_data = {
            "correlation_id": correlation_id,
            "operation": operation,
            "duration": duration,
            "memory_usage": memory_usage,
            **kwargs
        }
        logger.info(json.dumps(log_data))
    
    def log_error(self, correlation_id: str, error: str, 
                  workflow_id: Optional[str] = None, stage: Optional[str] = None,
                  retry_count: Optional[int] = None, **kwargs):
        """Log errors with full context."""
        log_data = {
            "correlation_id": correlation_id,
            "error": error,
            **kwargs
        }
        
        if workflow_id:
            log_data["workflow_id"] = workflow_id
        if stage:
            log_data["stage"] = stage
        if retry_count is not None:
            log_data["retry_count"] = retry_count
            
        logger.error(json.dumps(log_data))