#!/usr/bin/env python3
"""JIRA integration for AgentAI project using MCP server."""

import json
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class JiraIntegration:
    """JIRA integration using MCP server."""
    
    def __init__(self, server_path: str = None):
        # Use direct JIRA client instead of MCP server
        self.server_path = None  # Not needed for direct client
        self.process = None
        self.initialized = False
    
    async def start(self):
        """Initialize JIRA client."""
        try:
            # Use direct JIRA client from installed package
            from jira import JIRA
            import os
            
            jira_url = os.getenv("JIRA_URL")
            jira_username = os.getenv("JIRA_USERNAME")
            jira_token = os.getenv("JIRA_API_TOKEN")
            
            if jira_url and jira_username and jira_token:
                self.jira_client = JIRA(
                    server=jira_url,
                    basic_auth=(jira_username, jira_token)
                )
                self.initialized = True
                logger.info("JIRA client initialized successfully")
            else:
                logger.warning("JIRA credentials not configured, using demo mode")
                self.jira_client = None
                self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize JIRA client: {e}")
            self.jira_client = None
            self.initialized = True  # Continue in demo mode
    

    
    async def get_user_stories(self, project: str = None, limit: int = 100) -> List[Dict]:
        """Get user stories from JIRA."""
        if not self.initialized:
            await self.start()
            
        if not self.jira_client:
            # Return demo data if no JIRA client
            return [
                {"key": "KW-1", "summary": "User Authentication System", "status": "To Do", "description": "Implement secure user login and registration with JWT tokens"},
                {"key": "KW-2", "summary": "Dashboard Analytics", "status": "In Progress", "description": "Create real-time analytics dashboard with charts and metrics"},
                {"key": "KW-3", "summary": "API Integration", "status": "To Do", "description": "Integrate with third-party APIs for data synchronization"},
                {"key": "KW-4", "summary": "Mobile Responsive Design", "status": "Done", "description": "Ensure application works on mobile devices"},
                {"key": "KW-5", "summary": "Data Export Feature", "status": "To Do", "description": "Allow users to export data in CSV and PDF formats"}
            ]
            
        try:
            # Use bounded query - get recent issues from last 365 days
            if project:
                jql = f"project = {project} AND created >= -365d ORDER BY created DESC"
            else:
                # Get from any project but bounded by time
                jql = "created >= -365d ORDER BY created DESC"
            
            issues = self.jira_client.search_issues(jql, maxResults=limit)
            
            return [{
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "description": getattr(issue.fields, 'description', '') or ''
            } for issue in issues]
            
        except Exception as e:
            logger.error(f"Failed to get user stories: {e}")
            return []
    
    async def get_issue(self, key: str) -> Dict:
        """Get specific JIRA issue."""
        if not self.initialized:
            await self.start()
            
        if not self.jira_client:
            return {"key": key, "summary": "Demo Issue", "status": "To Do", "description": "Demo description"}
            
        try:
            issue = self.jira_client.issue(key)
            return {
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "description": getattr(issue.fields, 'description', '') or '',
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                "created": str(issue.fields.created)
            }
        except Exception as e:
            logger.error(f"Failed to get issue {key}: {e}")
            return {"error": str(e)}
    
    async def get_requirements_context(self, project: str = "KW") -> str:
        """Get formatted requirements context from JIRA stories."""
        stories = await self.get_user_stories(project=project)
        
        context = f"# JIRA Requirements - Project {project}\n\n"
        context += f"Total User Stories: {len(stories)}\n\n"
        
        for story in stories:
            context += f"## {story['key']}: {story['summary']}\n"
            context += f"**Status:** {story['status']}\n"
            if story.get('description'):
                context += f"**Description:** {story['description']}\n"
            context += "\n"
        
        return context
    
    async def close(self):
        """Close the JIRA client."""
        if hasattr(self, 'jira_client') and self.jira_client:
            # JIRA client doesn't need explicit closing
            self.jira_client = None
            self.initialized = False
            logger.info("JIRA client closed")

# Singleton instance
_jira_integration = None

async def get_jira_integration() -> JiraIntegration:
    """Get singleton JIRA integration instance."""
    global _jira_integration
    if _jira_integration is None:
        _jira_integration = JiraIntegration()
        await _jira_integration.start()
    return _jira_integration