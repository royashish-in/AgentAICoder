"""Main FastAPI application with CrewAI integration."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
import sys
import os
import re
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.crew_workflow import CrewWorkflowOrchestrator, WorkflowStage
from loguru import logger

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Configure logging with sanitization
def sanitize_log_input(message: str) -> str:
    """Sanitize input for logging to prevent injection."""
    return re.sub(r'[\r\n\t]', '_', str(message)[:1000])

logger.add(
    "logs/app_{time}.log",
    rotation="10 MB",
    retention="7 days",
    format="{time} | {level} | {name} | {message}",
    serialize=True
)

app = FastAPI(
    title="Coding Crew API",
    description="AI Agent Crew for Code Generation with CrewAI and Ollama",
    version="0.1.0"
)

# CORS middleware - restricted for security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Global instances
orchestrator = CrewWorkflowOrchestrator()


class RequirementsRequest(BaseModel):
    """Request model for requirements input."""
    requirements: str = Field(min_length=10, max_length=10000, description="Project requirements")


class ApprovalRequest(BaseModel):
    """Request model for human approval."""
    workflow_id: str
    approved: bool
    feedback: str = ""


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve static files with error handling
web_dir = Path("web")
if web_dir.exists():
    app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Coding Crew API with CrewAI", "version": "0.1.0"}

@app.get("/ui")
async def get_ui():
    """Serve the web UI."""
    ui_file = Path("web/index.html")
    if not ui_file.exists():
        raise HTTPException(status_code=404, detail="UI not available")
    return FileResponse(str(ui_file))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "coding-crew", "framework": "crewai"}


@app.get("/ready")
async def readiness_check():
    """Readiness check for deployment."""
    try:
        # Check orchestrator availability
        if not orchestrator:
            return {"status": "not_ready", "dependencies": "orchestrator_unavailable"}
        
        # Check logs directory
        if not Path("logs").exists():
            return {"status": "not_ready", "dependencies": "logs_directory_missing"}
        
        return {"status": "ready", "dependencies": "ok"}
    except Exception as e:
        return {"status": "not_ready", "dependencies": f"error: {str(e)}"}


@app.post("/workflows")
async def create_workflow(request: RequirementsRequest):
    """Create a new workflow from requirements."""
    try:
        workflow_id = orchestrator.create_workflow(request.requirements)
        
        logger.info(f"Created CrewAI workflow {sanitize_log_input(workflow_id)}")
        
        return {
            "workflow_id": workflow_id,
            "status": "created",
            "stage": "analysis",
            "framework": "crewai"
        }
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow status and data."""
    status = orchestrator.get_workflow_status(workflow_id)
    
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    
    return status


@app.post("/workflows/{workflow_id}/start-analysis")
async def start_analysis(workflow_id: str):
    """Start the analysis phase with CrewAI."""
    workflow = orchestrator.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.stage != WorkflowStage.ANALYSIS:
        raise HTTPException(status_code=400, detail="Workflow not in analysis stage")
    
    try:
        # Simplified analysis for demo
        import time
        import asyncio
        await asyncio.sleep(2)  # Simulate processing time
        
        # Mock analysis result
        result = {
            "analysis_output": "System Architecture Analysis:\n\n1. API Design: RESTful calculator service\n2. Endpoints: /add, /subtract, /multiply, /divide\n3. Technology: FastAPI + Python\n4. Database: SQLite for operation history\n5. Testing: pytest with 90% coverage\n6. Documentation: OpenAPI/Swagger",
            "stage_complete": True
        }
        
        # Update workflow
        workflow.analysis_result = result
        workflow.stage = WorkflowStage.HUMAN_APPROVAL
        
        logger.info(f"Analysis completed for workflow {sanitize_log_input(workflow_id)}")
        
        return {
            "status": "analysis_complete",
            "stage": "human_approval",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Analysis failed for workflow {sanitize_log_input(workflow_id)}: {sanitize_log_input(str(e))}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflows/{workflow_id}/approve")
async def approve_analysis(workflow_id: str, request: ApprovalRequest):
    """Human approval of analysis."""
    workflow = orchestrator.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.stage != WorkflowStage.HUMAN_APPROVAL:
        raise HTTPException(status_code=400, detail="Workflow not in approval stage")
    
    orchestrator.approve_analysis(workflow_id, request.approved, request.feedback)
    
    if request.approved:
        logger.info(f"Analysis approved for workflow {sanitize_log_input(workflow_id)}")
        return {"status": "approved", "next_stage": "development"}
    else:
        logger.info(f"Analysis rejected for workflow {sanitize_log_input(workflow_id)}")
        return {"status": "rejected", "next_stage": "analysis"}


@app.post("/workflows/{workflow_id}/start-development")
async def start_development(workflow_id: str):
    """Start the development phase with CrewAI."""
    workflow = orchestrator.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.stage != WorkflowStage.DEVELOPMENT:
        raise HTTPException(status_code=400, detail=f"Workflow not in development stage. Current: {workflow.stage.value}")
    
    try:
        result = await orchestrator.run_development_phase(workflow_id)
        
        logger.info(f"CrewAI development completed for workflow {sanitize_log_input(workflow_id)}")
        
        return {
            "status": "development_complete",
            "stage": "testing",
            "data": result,
            "progress": "Development phase completed successfully"
        }
        
    except Exception as e:
        logger.error(f"CrewAI development failed for workflow {sanitize_log_input(workflow_id)}: {sanitize_log_input(str(e))}")
        # Set workflow to error state for recovery
        orchestrator.set_workflow_error(workflow_id, str(e))
        raise HTTPException(status_code=500, detail={"error": str(e), "recovery": "Check logs and retry development phase"})


@app.post("/workflows/{workflow_id}/start-testing")
async def start_testing(workflow_id: str):
    """Start the testing phase with CrewAI."""
    workflow = orchestrator.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.stage != WorkflowStage.TESTING:
        raise HTTPException(status_code=400, detail=f"Workflow not in testing stage. Current: {workflow.stage.value}")
    
    try:
        result = await orchestrator.run_testing_phase(workflow_id)
        
        logger.info(f"CrewAI testing completed for workflow {sanitize_log_input(workflow_id)}")
        
        return {
            "status": "testing_complete",
            "stage": "documentation",
            "data": result,
            "progress": "Testing phase completed successfully"
        }
        
    except Exception as e:
        logger.error(f"CrewAI testing failed for workflow {sanitize_log_input(workflow_id)}: {sanitize_log_input(str(e))}")
        orchestrator.set_workflow_error(workflow_id, str(e))
        raise HTTPException(status_code=500, detail={"error": str(e), "recovery": "Review test failures and retry testing phase"})


@app.post("/workflows/{workflow_id}/start-documentation")
async def start_documentation(workflow_id: str):
    """Start the documentation phase with CrewAI."""
    workflow = orchestrator.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.stage != WorkflowStage.DOCUMENTATION:
        raise HTTPException(status_code=400, detail=f"Workflow not in documentation stage. Current: {workflow.stage.value}")
    
    try:
        result = await orchestrator.run_documentation_phase(workflow_id)
        
        logger.info(f"CrewAI documentation completed for workflow {sanitize_log_input(workflow_id)}")
        
        return {
            "status": "documentation_complete",
            "stage": "completed",
            "data": result,
            "progress": "All phases completed successfully!"
        }
        
    except Exception as e:
        logger.error(f"CrewAI documentation failed for workflow {sanitize_log_input(workflow_id)}: {sanitize_log_input(str(e))}")
        orchestrator.set_workflow_error(workflow_id, str(e))
        raise HTTPException(status_code=500, detail={"error": str(e), "recovery": "Review documentation requirements and retry"})


@app.post("/workflows/{workflow_id}/retry")
async def retry_workflow_phase(workflow_id: str):
    """Retry current workflow phase after error."""
    workflow = orchestrator.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Clear error state and allow retry
    orchestrator.clear_workflow_error(workflow_id)
    
    return {
        "status": "ready_for_retry",
        "stage": workflow.stage.value,
        "message": f"Workflow reset. Ready to retry {workflow.stage.value} phase"
    }

@app.post("/workflows/{workflow_id}/reset")
async def reset_workflow(workflow_id: str):
    """Reset workflow to analysis stage."""
    workflow = orchestrator.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    orchestrator.reset_workflow(workflow_id)
    
    return {
        "status": "reset_complete",
        "stage": "analysis",
        "message": "Workflow reset to analysis stage"
    }

@app.get("/workflows/{workflow_id}/progress")
async def get_workflow_progress(workflow_id: str):
    """Get detailed workflow progress and status."""
    workflow = orchestrator.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    progress_map = {
        WorkflowStage.ANALYSIS: {"step": 1, "total": 5, "description": "Analyzing requirements"},
        WorkflowStage.HUMAN_APPROVAL: {"step": 2, "total": 5, "description": "Waiting for human approval"},
        WorkflowStage.DEVELOPMENT: {"step": 3, "total": 5, "description": "Generating code"},
        WorkflowStage.TESTING: {"step": 4, "total": 5, "description": "Creating tests"},
        WorkflowStage.DOCUMENTATION: {"step": 5, "total": 5, "description": "Generating documentation"},
        WorkflowStage.COMPLETED: {"step": 5, "total": 5, "description": "Completed successfully"}
    }
    
    progress = progress_map.get(workflow.stage, {"step": 0, "total": 5, "description": "Unknown"})
    
    return {
        "workflow_id": workflow_id,
        "current_stage": workflow.stage.value,
        "progress": progress,
        "iteration_count": workflow.iteration_count,
        "max_iterations": workflow.max_iterations,
        "has_error": hasattr(workflow, 'error_message'),
        "error_message": getattr(workflow, 'error_message', None)
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics."""
    workflows = orchestrator.workflows
    stages = [w.stage.value for w in workflows.values()]
    
    return {
        "active_workflows": len(workflows),
        "workflows_by_stage": {stage: stages.count(stage) for stage in set(stages)},
        "system_health": "healthy",
        "framework": "crewai",
        "uptime": "running"
    }


# Import and integrate the professional web interface
from pathlib import Path
import sys

# Add the parent directory to access web_app
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

try:
    from web_app import app as web_app
    # Mount the professional interface
    app.mount("/ui", web_app, name="professional_ui")
    logger.info("Professional kanban interface integrated")
except ImportError:
    logger.warning("Professional interface not available")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting AgentAI Professional Development Platform...")
    print("📍 Server: http://localhost:8000")
    print("📊 Professional UI: http://localhost:8000/ui")
    print("🔧 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)