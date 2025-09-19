#!/usr/bin/env python3
"""Main entry point for JIRA-enhanced AgentAI."""

import asyncio
import sys
from pathlib import Path
from core.jira_workflow import JiraEnhancedWorkflow
from core.jira_integration import get_jira_integration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run JIRA-enhanced AgentAI workflow."""
    print("🚀 Starting JIRA-Enhanced AgentAI")
    
    # Get user requirements
    requirements = input("\nEnter your project requirements: ")
    project_id = f"JIRA-{hash(requirements) % 10000:04d}"
    
    try:
        # Initialize JIRA-enhanced workflow
        workflow = JiraEnhancedWorkflow(project_id, jira_project="KW")
        
        print(f"\n📋 Loading JIRA context from project KW...")
        await workflow.initialize_jira_context()
        
        # Get JIRA summary
        jira_summary = await workflow.get_jira_summary()
        print(f"✅ Loaded {jira_summary['total_stories']} JIRA user stories")
        print(f"   Status: {jira_summary['stories_by_status']}")
        
        # Run enhanced workflow phases
        print(f"\n🔍 Running JIRA-enhanced analysis...")
        analysis_result = await workflow.run_analysis_phase(requirements)
        
        print(f"\n💻 Running JIRA-aware development...")
        development_result = await workflow.run_development_phase(analysis_result)
        
        print(f"\n🧪 Running JIRA-based testing...")
        testing_result = await workflow.run_testing_phase(development_result)
        
        print(f"\n✅ JIRA-Enhanced AgentAI completed successfully!")
        print(f"   Project ID: {project_id}")
        print(f"   JIRA Stories Integrated: {jira_summary['total_stories']}")
        
        return {
            "project_id": project_id,
            "jira_summary": jira_summary,
            "analysis": analysis_result,
            "development": development_result,
            "testing": testing_result
        }
        
    except Exception as e:
        logger.error(f"JIRA-Enhanced workflow failed: {e}")
        raise
    
    finally:
        # Cleanup JIRA connection
        try:
            jira = await get_jira_integration()
            await jira.close()
        except:
            pass

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n📊 Final Result: {result['project_id']}")