#!/usr/bin/env python3
"""Test live CrewAI workflow with Ollama."""

import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crew_workflow import CrewWorkflowOrchestrator
from loguru import logger


async def test_live_analysis():
    """Test live analysis with Ollama."""
    print("🤖 Testing Live CrewAI + Ollama Workflow")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = CrewWorkflowOrchestrator()
    
    # Simple requirements for testing
    requirements = """
    # Simple Todo Application
    
    Build a web-based todo application with the following features:
    - User can add new tasks
    - User can mark tasks as complete
    - User can delete tasks
    - Tasks are stored in a database
    - Simple web interface
    """
    
    print("📋 Requirements:")
    print(requirements)
    print("\n🔄 Starting Analysis Phase...")
    
    try:
        # Create workflow
        workflow_id = orchestrator.create_workflow(requirements)
        print(f"✅ Created workflow: {workflow_id[:8]}...")
        
        # Run analysis phase with real LLMs
        print("🧠 Running CrewAI Analysis (this may take 2-3 minutes)...")
        result = await orchestrator.run_analysis_phase(workflow_id)
        
        print("\n🎉 Analysis Complete!")
        print("=" * 50)
        print("📊 Results:")
        print(f"- Analysis Output Length: {len(str(result))} characters")
        print(f"- Stage Complete: {result.get('stage_complete', False)}")
        
        # Show first 500 characters of output
        output = str(result.get('analysis_output', ''))
        if output:
            print(f"\n📝 Analysis Preview (first 500 chars):")
            print("-" * 30)
            print(output[:500] + "..." if len(output) > 500 else output)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        logger.error(f"Live workflow test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚨 Make sure Ollama is running: ollama serve")
    print("⏳ This test will take 2-3 minutes with real LLM inference...\n")
    
    success = asyncio.run(test_live_analysis())
    
    if success:
        print("\n✅ Live workflow test successful!")
        print("🎯 Next: Build draw.io diagram generation")
    else:
        print("\n❌ Live workflow test failed")
        print("💡 Check if Ollama is running and models are available")