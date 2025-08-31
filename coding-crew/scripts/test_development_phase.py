#!/usr/bin/env python3
"""Test the development phase with iterative code generation and review."""

import asyncio
from core.crew_workflow import CrewWorkflowOrchestrator
from loguru import logger

async def test_development_phase():
    """Test development phase with sample approved analysis."""
    
    print("🔧 Testing Development Phase")
    print("=" * 50)
    
    # Create workflow orchestrator
    orchestrator = CrewWorkflowOrchestrator()
    
    # Sample approved analysis
    sample_analysis = """
    # Todo Application System Analysis
    
    ## Architecture Overview
    - **Frontend**: React.js with TypeScript
    - **Backend**: FastAPI with Python
    - **Database**: SQLite for development, PostgreSQL for production
    - **Authentication**: JWT tokens
    
    ## Components
    1. **User Management**: Registration, login, profile management
    2. **Task Management**: CRUD operations for todos
    3. **API Layer**: RESTful endpoints with validation
    4. **Database Layer**: ORM with migrations
    
    ## Technology Stack
    - Frontend: React 18, TypeScript, Tailwind CSS
    - Backend: FastAPI, SQLAlchemy, Pydantic
    - Database: SQLite/PostgreSQL
    - Testing: pytest, React Testing Library
    """
    
    try:
        # Create workflow
        workflow_id = orchestrator.create_workflow("Build a todo application")
        
        # Simulate approved analysis
        workflow = orchestrator.get_workflow(workflow_id)
        workflow.analysis_result = {
            "analysis_output": sample_analysis,
            "stage_complete": True
        }
        workflow.approved = True
        workflow.stage = workflow.stage.__class__.DEVELOPMENT
        
        print(f"✅ Created workflow: {workflow_id[:8]}...")
        print("🧠 Running Development Phase (this may take 3-5 minutes)...")
        
        # Run development phase
        result = await orchestrator.run_development_phase(workflow_id)
        
        print("\n" + "=" * 50)
        print("📋 Development Results")
        print("=" * 50)
        
        print(f"Iterations: {result.get('iterations', 'N/A')}")
        print(f"Approved: {result.get('approved', False)}")
        print(f"Stage Complete: {result.get('stage_complete', False)}")
        
        if result.get('code_output'):
            print(f"\n📝 Generated Code (first 500 chars):")
            print("-" * 30)
            print(result['code_output'][:500] + "..." if len(result['code_output']) > 500 else result['code_output'])
        
        if result.get('review_output'):
            print(f"\n🔍 Code Review (first 500 chars):")
            print("-" * 30)
            print(result['review_output'][:500] + "..." if len(result['review_output']) > 500 else result['review_output'])
        
        print("\n✅ Development phase test completed!")
        
    except Exception as e:
        print(f"\n❌ Development phase test failed: {e}")
        logger.error(f"Development test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_development_phase())