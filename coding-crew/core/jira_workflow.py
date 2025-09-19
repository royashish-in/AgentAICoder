#!/usr/bin/env python3
"""JIRA-enhanced workflow for AgentAI project."""

import asyncio
from typing import Dict, Any
from .jira_integration import get_jira_integration
from .workflow import WorkflowOrchestrator, WorkflowStage
import logging

logger = logging.getLogger(__name__)

class JiraEnhancedWorkflow(WorkflowOrchestrator):
    """Workflow enhanced with JIRA integration."""
    
    def __init__(self, jira_project: str = "KW"):
        super().__init__()
        self.jira_project = jira_project
        self.jira_context = None
    
    async def initialize_jira_context(self):
        """Initialize JIRA context for the workflow."""
        try:
            jira = await get_jira_integration()
            self.jira_context = await jira.get_requirements_context(self.jira_project)
            logger.info(f"Loaded JIRA context for project {self.jira_project}")
        except Exception as e:
            logger.error(f"Failed to load JIRA context: {e}")
            self.jira_context = "# JIRA context unavailable\n"
    
    async def create_enhanced_workflow(self, requirements: str) -> str:
        """Create workflow with JIRA enhancement."""
        if not self.jira_context:
            await self.initialize_jira_context()
        
        # Combine user requirements with JIRA context
        enhanced_requirements = f"""
# User Requirements
{requirements}

# JIRA Project Context
{self.jira_context}

# Analysis Instructions
Please analyze both the user requirements and the JIRA user stories to provide:
1. Technical architecture recommendations
2. Implementation approach that addresses JIRA stories
3. Technology stack suggestions
4. Development phases aligned with JIRA priorities
"""
        
        return self.create_workflow(enhanced_requirements)
    
    async def get_development_context(self, workflow_id: str) -> str:
        """Get JIRA-enhanced development context."""
        jira = await get_jira_integration()
        stories = await jira.get_user_stories(project=self.jira_project, limit=5)
        
        context = "# JIRA Stories for Implementation\n\n"
        for story in stories:
            context += f"## {story['key']}: {story['summary']}\n"
            context += f"Status: {story['status']}\n\n"
        
        return context
    
    async def get_testing_context(self, workflow_id: str) -> str:
        """Get JIRA-enhanced testing context."""
        jira = await get_jira_integration()
        stories = await jira.get_user_stories(project=self.jira_project, limit=5)
        
        context = "# JIRA Stories for Testing\n\n"
        for story in stories:
            context += f"## Test {story['key']}: {story['summary']}\n"
            context += f"Verify: {story['summary']}\n\n"
        
        return context
    
    async def get_jira_summary(self) -> Dict[str, Any]:
        """Get summary of JIRA integration."""
        try:
            jira = await get_jira_integration()
            stories = await jira.get_user_stories(project=self.jira_project)
            
            return {
                "project": self.jira_project,
                "total_stories": len(stories),
                "stories_by_status": self._group_by_status(stories),
                "recent_stories": stories[:5]
            }
        except Exception as e:
            logger.error(f"Failed to get JIRA summary: {e}")
            return {"error": str(e)}
    
    def _group_by_status(self, stories):
        """Group stories by status."""
        status_groups = {}
        for story in stories:
            status = story.get('status', 'Unknown')
            if status not in status_groups:
                status_groups[status] = 0
            status_groups[status] += 1
        return status_groups