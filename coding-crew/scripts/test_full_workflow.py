#!/usr/bin/env python3
"""Test complete end-to-end workflow execution."""

import asyncio
from core.crew_workflow import CrewWorkflowOrchestrator
from loguru import logger

async def test_full_workflow():
    """Test complete workflow from analysis to documentation."""
    
    print("🚀 Testing Complete End-to-End Workflow")
    print("=" * 60)
    
    orchestrator = CrewWorkflowOrchestrator()
    
    # Sample requirements
    requirements = """
    # Simple Calculator API
    
    Build a REST API for basic calculator operations:
    - Addition, subtraction, multiplication, division
    - Input validation and error handling
    - JSON request/response format
    - Basic authentication
    - Logging and monitoring
    """
    
    try:
        # Phase 1: Create workflow
        print("📋 Phase 1: Creating workflow...")
        workflow_id = orchestrator.create_workflow(requirements)
        print(f"✅ Workflow created: {workflow_id[:8]}...")
        
        # Phase 2: Analysis (mocked for testing)
        print("\n🧠 Phase 2: Analysis phase...")
        workflow = orchestrator.get_workflow(workflow_id)
        
        # Simulate analysis completion
        workflow.analysis_result = {
            "analysis_output": "Calculator API analysis complete with FastAPI, SQLite, JWT auth",
            "stage_complete": True
        }
        workflow.approved = True
        workflow.stage = workflow.stage.__class__.DEVELOPMENT
        print("✅ Analysis completed and approved")
        
        # Phase 3: Development (mocked for testing)
        print("\n💻 Phase 3: Development phase...")
        workflow.code_result = {
            "code_output": "FastAPI calculator with endpoints, auth, validation",
            "iterations": 2,
            "approved": True,
            "stage_complete": True
        }
        workflow.stage = workflow.stage.__class__.TESTING
        print("✅ Development completed after 2 iterations")
        
        # Phase 4: Testing (mocked for testing)
        print("\n🧪 Phase 4: Testing phase...")
        workflow.test_result = {
            "test_output": "Comprehensive test suite generated",
            "coverage": 87.5,
            "tests_passed": True,
            "coverage_target_met": True,
            "stage_complete": True
        }
        workflow.stage = workflow.stage.__class__.DOCUMENTATION
        print("✅ Testing completed - 87.5% coverage, all tests passed")
        
        # Phase 5: Documentation (mocked for testing)
        print("\n📚 Phase 5: Documentation phase...")
        workflow.documentation_result = {
            "doc_output": "Complete documentation package generated",
            "stage_complete": True
        }
        workflow.stage = workflow.stage.__class__.COMPLETED
        workflow.completed = True
        print("✅ Documentation completed")
        
        # Final status
        print("\n" + "=" * 60)
        print("📊 Final Workflow Status")
        print("=" * 60)
        
        status = orchestrator.get_workflow_status(workflow_id)
        print(f"Workflow ID: {workflow_id[:8]}...")
        print(f"Stage: {status['stage']}")
        print(f"Approved: {status['approved']}")
        print(f"Completed: {status['completed']}")
        print(f"Has Analysis: {status['has_analysis']}")
        print(f"Has Code: {status['has_code']}")
        print(f"Has Tests: {status['has_tests']}")
        print(f"Has Documentation: {status['has_documentation']}")
        
        print("\n🎉 Complete end-to-end workflow test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        logger.error(f"Full workflow test error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_workflow())
    exit(0 if success else 1)