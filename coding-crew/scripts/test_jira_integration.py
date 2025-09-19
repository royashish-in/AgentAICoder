#!/usr/bin/env python3
"""Test JIRA integration with AgentAI project."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.jira_integration import get_jira_integration
from core.jira_workflow import JiraEnhancedWorkflow

async def test_jira_integration():
    """Test JIRA integration functionality."""
    print("=== Testing JIRA Integration with AgentAI ===")
    
    try:
        # Test 1: Basic JIRA connection
        print("\n1. Testing JIRA connection...")
        jira = await get_jira_integration()
        stories = await jira.get_user_stories(project="KW", limit=3)
        print(f"✅ Connected to JIRA - Found {len(stories)} stories")
        
        for story in stories:
            print(f"   - {story['key']}: {story['summary']}")
        
        # Test 2: Get specific issue
        print("\n2. Testing specific issue retrieval...")
        if stories:
            issue = await jira.get_issue(stories[0]['key'])
            print(f"✅ Retrieved issue: {issue['key']} - {issue['status']}")
        
        # Test 3: Requirements context
        print("\n3. Testing requirements context generation...")
        context = await jira.get_requirements_context("KW")
        print(f"✅ Generated context ({len(context)} characters)")
        print(f"   Preview: {context[:200]}...")
        
        # Test 4: JIRA-enhanced workflow
        print("\n4. Testing JIRA-enhanced workflow...")
        workflow = JiraEnhancedWorkflow("KW")
        await workflow.initialize_jira_context()
        print("✅ JIRA workflow initialized")
        
        # Test 5: JIRA summary
        summary = await workflow.get_jira_summary()
        print(f"✅ JIRA summary: {summary['total_stories']} stories")
        print(f"   Status breakdown: {summary['stories_by_status']}")
        
        # Test 6: Agent context
        print("\n6. Testing agent JIRA context...")
        agent_context = await jira.get_requirements_context("KW")
        print(f"✅ Agent context generated ({len(agent_context)} characters)")
        
        print("\n=== All JIRA integration tests passed! ===")
        
    except Exception as e:
        print(f"❌ JIRA integration test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'jira' in locals():
            await jira.close()

if __name__ == "__main__":
    asyncio.run(test_jira_integration())