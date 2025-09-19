#!/usr/bin/env python3
"""JIRA-enhanced agents for AgentAI project."""

from ..core.jira_integration import get_jira_integration
import asyncio

class JiraEnhancedAnalysisAgent:
    """Analysis agent enhanced with JIRA requirements."""
    
    @staticmethod
    def get_agent_config():
        return {
            "role": "JIRA-Enhanced Requirements Analyst",
            "goal": "Analyze project requirements using JIRA user stories and provide comprehensive technical analysis",
            "backstory": """You are an expert requirements analyst who specializes in analyzing JIRA user stories 
            and translating them into technical specifications. You have access to live JIRA data and can 
            provide context-aware analysis based on actual project requirements."""
        }
    
    @staticmethod
    async def get_jira_context(project: str = "KW") -> str:
        """Get JIRA requirements context for analysis."""
        jira = await get_jira_integration()
        return await jira.get_requirements_context(project)

class JiraDevelopmentAgent:
    """Development agent that uses JIRA stories for code generation."""
    
    @staticmethod
    def get_agent_config():
        return {
            "role": "JIRA-Aware Developer",
            "goal": "Generate code that implements JIRA user stories with full traceability",
            "backstory": """You are a senior developer who creates code directly from JIRA user stories. 
            You understand acceptance criteria, user needs, and can trace every piece of code back to 
            specific JIRA requirements."""
        }
    
    @staticmethod
    async def get_story_details(story_key: str) -> dict:
        """Get detailed JIRA story for implementation."""
        jira = await get_jira_integration()
        return await jira.get_issue(story_key)

class JiraTestingAgent:
    """Testing agent that creates tests based on JIRA acceptance criteria."""
    
    @staticmethod
    def get_agent_config():
        return {
            "role": "JIRA-Based Test Engineer",
            "goal": "Create comprehensive tests that validate JIRA user story acceptance criteria",
            "backstory": """You are a test engineer who creates tests directly from JIRA user stories. 
            You understand user acceptance criteria and create tests that ensure every requirement 
            is properly validated."""
        }
    
    @staticmethod
    async def get_testing_context(project: str = "KW") -> str:
        """Get JIRA stories formatted for test creation."""
        jira = await get_jira_integration()
        stories = await jira.get_user_stories(project=project)
        
        context = "# Test Requirements from JIRA\n\n"
        for story in stories:
            context += f"## Test for {story['key']}\n"
            context += f"**User Story:** {story['summary']}\n"
            context += f"**Status:** {story['status']}\n"
            context += "**Test Scenarios to Cover:**\n"
            context += f"- Verify: {story['summary']}\n"
            context += f"- Validate user can achieve the goal described\n"
            context += f"- Test edge cases and error conditions\n\n"
        
        return context