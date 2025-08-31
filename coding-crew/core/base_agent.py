"""Base agent class with common functionality."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import uuid4
import time
from loguru import logger


class BaseAgent(ABC):
    """Base class for all agents in the coding crew system."""
    
    def __init__(self, agent_type: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = str(uuid4())
        self.agent_type = agent_type
        self.config = config or {}
        self.state: Dict[str, Any] = {}
        
        logger.info(f"Initialized {agent_type} agent with ID: {self.agent_id}")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        pass
    
    async def execute(self, input_data: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
        """Execute agent processing with logging and error handling."""
        start_time = time.time()
        
        logger.info(
            f"Agent {self.agent_type} starting execution",
            extra={
                "agent_id": self.agent_id,
                "correlation_id": correlation_id,
                "input_size": len(str(input_data))
            }
        )
        
        try:
            result = await self.process(input_data)
            duration = time.time() - start_time
            
            logger.info(
                f"Agent {self.agent_type} completed successfully",
                extra={
                    "agent_id": self.agent_id,
                    "correlation_id": correlation_id,
                    "duration_ms": int(duration * 1000),
                    "output_size": len(str(result))
                }
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f"Agent {self.agent_type} failed",
                extra={
                    "agent_id": self.agent_id,
                    "correlation_id": correlation_id,
                    "duration_ms": int(duration * 1000),
                    "error": str(e)
                }
            )
            raise