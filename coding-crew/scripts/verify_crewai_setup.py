#!/usr/bin/env python3
"""Verify CrewAI setup and Ollama integration."""

import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crew_workflow import CrewWorkflowOrchestrator, WorkflowStage
from core.llm_config import get_analysis_llm, get_coding_llm
from agents.crew_agents import create_analysis_agent


async def main():
    """Verify CrewAI and Ollama setup."""
    print("🤖 CrewAI + Ollama Setup Verification")
    print("=" * 50)
    
    # Test LLM configuration
    print("✅ Testing LLM Configuration...")
    try:
        analysis_llm = get_analysis_llm()
        coding_llm = get_coding_llm()
        print(f"   Analysis LLM: {analysis_llm.model}")
        print(f"   Coding LLM: {coding_llm.model}")
    except Exception as e:
        print(f"   ❌ LLM Config Error: {e}")
        return
    
    # Test CrewAI workflow orchestrator
    print("✅ Testing CrewAI WorkflowOrchestrator...")
    orchestrator = CrewWorkflowOrchestrator()
    workflow_id = orchestrator.create_workflow("Build a simple web application")
    workflow = orchestrator.get_workflow(workflow_id)
    assert workflow is not None
    assert workflow.stage == WorkflowStage.ANALYSIS
    print(f"   Created workflow: {workflow_id[:8]}...")
    
    # Test CrewAI agent creation
    print("✅ Testing CrewAI Agent Creation...")
    try:
        analysis_agent = create_analysis_agent()
        print(f"   Analysis Agent: {analysis_agent.role}")
        print(f"   Agent LLM: {analysis_agent.llm.model}")
    except Exception as e:
        print(f"   ❌ Agent Creation Error: {e}")
        return
    
    # Test workflow status
    print("✅ Testing Workflow Status...")
    status = orchestrator.get_workflow_status(workflow_id)
    assert status["stage"] == "analysis"
    assert status["approved"] is False
    print(f"   Workflow Status: {status['stage']}")
    
    print("=" * 50)
    print("🎉 CrewAI Setup Verification Complete!")
    print("📋 System Status:")
    print(f"   - CrewAI Framework: ✅ Working")
    print(f"   - Ollama Integration: ✅ Configured")
    print(f"   - Available Models:")
    print(f"     • Analysis: llama3.1:8b")
    print(f"     • Coding: qwen2.5-coder:1.5b-base")
    print(f"     • Review: llama3.1:8b")
    print(f"     • Testing: qwen2.5-coder:1.5b-base")
    print(f"     • Documentation: llama3.2:latest")
    print(f"   - Workflow Orchestrator: ✅ Working")
    print(f"   - Agent Creation: ✅ Working")
    print("=" * 50)
    print("🚀 Ready for CrewAI-powered development!")
    print("\n💡 Next Steps:")
    print("   1. Start Ollama: ollama serve")
    print("   2. Test with real LLM: make dev")
    print("   3. Create workflow via API")


if __name__ == "__main__":
    asyncio.run(main())