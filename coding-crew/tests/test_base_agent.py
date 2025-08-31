"""Tests for base agent functionality."""

import pytest
import sys
import os
from unittest.mock import AsyncMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_agent import BaseAgent


class MockAgent(BaseAgent):
    """Mock implementation of BaseAgent for testing."""
    
    async def process(self, input_data):
        return {"result": "test_output", "input": input_data}


class TestBaseAgent:
    """Test cases for BaseAgent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = MockAgent("test_agent")
        
        assert agent.agent_type == "test_agent"
        assert agent.agent_id is not None
        assert len(agent.agent_id) > 0
        assert agent.config == {}
        assert agent.state == {}
    
    def test_agent_initialization_with_config(self):
        """Test agent initialization with config."""
        config = {"test_param": "test_value"}
        agent = MockAgent("test_agent", config)
        
        assert agent.config == config
    
    @pytest.mark.asyncio
    async def test_agent_execute_success(self):
        """Test successful agent execution."""
        agent = MockAgent("test_agent")
        input_data = {"test": "data"}
        correlation_id = "test_correlation"
        
        result = await agent.execute(input_data, correlation_id)
        
        assert result["result"] == "test_output"
        assert result["input"] == input_data
    
    @pytest.mark.asyncio
    async def test_agent_execute_failure(self):
        """Test agent execution with failure."""
        agent = MockAgent("test_agent")
        
        # Mock process to raise exception
        agent.process = AsyncMock(side_effect=Exception("Test error"))
        
        with pytest.raises(Exception, match="Test error"):
            await agent.execute({"test": "data"}, "test_correlation")