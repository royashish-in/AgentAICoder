"""Tests for analysis agent."""

import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analysis_agent import AnalysisAgent


class TestAnalysisAgent:
    """Test cases for AnalysisAgent."""
    
    def test_agent_initialization(self):
        """Test analysis agent initialization."""
        agent = AnalysisAgent()
        
        assert agent.agent_type == "analysis"
        assert agent.agent_id is not None
    
    @pytest.mark.asyncio
    async def test_process_requirements(self):
        """Test requirements processing."""
        agent = AnalysisAgent()
        input_data = {"requirements": "# Test Project\nBuild a web app"}
        
        result = await agent.process(input_data)
        
        assert "parsed_requirements" in result
        assert "workload_analysis" in result
        assert "system_diagrams" in result
        assert result["analysis_complete"] is True