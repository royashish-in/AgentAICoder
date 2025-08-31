from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
import json
import uuid
from datetime import datetime
from typing import Optional
import sys
import os

# Add coding-crew to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'coding-crew'))

from config import extract_tech_stack_from_analysis, extract_timeline_from_analysis, extract_diagrams_from_analysis, get_workflow_config, get_delays_config
from utils.file_manager import ProjectFileManager
from utils.persistence import DataStore

app = FastAPI(title="AgentAI - Professional Development Platform")

# Mount static files
app.mount("/static", StaticFiles(directory="../web/static"), name="static")

class ProjectRequirements(BaseModel):
    project_name: str
    description: str
    target_users: Optional[str] = ""
    scale: Optional[str] = ""
    features: list[str]
    constraints: Optional[str] = ""

class WorkflowStatus(BaseModel):
    id: str
    project_name: str
    status: str
    current_phase: str
    progress: int
    created_at: str
    updated_at: str

class ApprovalRequest(BaseModel):
    analysis_id: str
    approved: bool
    rework: Optional[bool] = False
    feedback: str = ""

# Initialize persistence and file management
data_store = DataStore()
file_manager = ProjectFileManager()

# Load persisted data
data = data_store.load_data()
projects = data["projects"]
workflows = data["workflows"]
analyses = data["analyses"]
approvals = data["approvals"]

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AgentAI - Development Platform</title>
        <link rel="stylesheet" href="/static/style.css?v=2">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    </head>
    <body>
        <div class="app-container">
            <aside class="sidebar">
                <div class="sidebar-header">
                    <h2>AgentAI</h2>
                </div>
                <nav class="sidebar-nav">
                    <a href="#" onclick="showPage('dashboard')" class="nav-item active" data-page="dashboard">
                        <span class="nav-icon">📊</span>
                        <span>Dashboard</span>
                    </a>
                    <a href="#" onclick="showPage('new-project')" class="nav-item" data-page="new-project">
                        <span class="nav-icon">➕</span>
                        <span>New Project</span>
                    </a>
                    <a href="#" onclick="showPage('workflows')" class="nav-item" data-page="workflows">
                        <span class="nav-icon">⚡</span>
                        <span>Workflows</span>
                    </a>
                    <a href="#" onclick="showPage('approvals')" class="nav-item" data-page="approvals">
                        <span class="nav-icon">✅</span>
                        <span>Approvals</span>
                    </a>
                    <a href="#" onclick="showPage('projects')" class="nav-item" data-page="projects">
                        <span class="nav-icon">📁</span>
                        <span>Projects</span>
                    </a>
                </nav>
            </aside>
            
            <main class="main-content">
                <div id="dashboard-page" class="page active">
                    <header class="page-header">
                        <h1>Project Dashboard</h1>
                        <button class="btn btn-primary" onclick="showPage('new-project')">+ New Project</button>
                    </header>
                    
                    <div class="kanban-board">
                        <div class="kanban-column">
                            <div class="column-header">
                                <h3>Requirements Analysis</h3>
                                <span class="count" id="requirements-count">0</span>
                            </div>
                            <div class="column-content" id="requirements-column"></div>
                        </div>
                        
                        <div class="kanban-column">
                            <div class="column-header">
                                <h3>Human Approval</h3>
                                <span class="count" id="analysis-count">0</span>
                            </div>
                            <div class="column-content" id="analysis-column"></div>
                        </div>
                        
                        <div class="kanban-column">
                            <div class="column-header">
                                <h3>Development</h3>
                                <span class="count" id="development-count">0</span>
                            </div>
                            <div class="column-content" id="development-column"></div>
                        </div>
                        
                        <div class="kanban-column">
                            <div class="column-header">
                                <h3>Testing</h3>
                                <span class="count" id="testing-count">0</span>
                            </div>
                            <div class="column-content" id="testing-column"></div>
                        </div>
                        
                        <div class="kanban-column">
                            <div class="column-header">
                                <h3>Deployment</h3>
                                <span class="count" id="deployment-count">0</span>
                            </div>
                            <div class="column-content" id="deployment-column"></div>
                        </div>
                    </div>
                </div>
                
                <div id="new-project-page" class="page">
                    <header class="page-header">
                        <h1>Create New Project</h1>
                        <button class="btn btn-secondary" onclick="showPage('dashboard')">Back</button>
                    </header>
                    
                    <div class="form-container">
                        <div class="requirements-note">
                            <strong>AI-Powered Analysis:</strong> Our AI will analyze your requirements and recommend the optimal technology stack, architecture patterns, and development approach. You'll review and approve these recommendations before development begins.
                        </div>
                        <form id="project-form" class="project-form">
                            <div class="form-section">
                                <h3>Project Details</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="project-name">Project Name</label>
                                        <input type="text" id="project-name" required>
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="description">Description</label>
                                        <textarea id="description" rows="3" required placeholder="What do you want to build?"></textarea>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="form-section">
                                <h3>Requirements</h3>
                                <div class="form-grid">
                                    <div class="form-group">
                                        <label for="target-users">Target Users</label>
                                        <select id="target-users" required>
                                            <option value="">Select target users</option>
                                            <option value="end-consumers">End Consumers</option>
                                            <option value="business-users">Business Users</option>
                                            <option value="developers">Developers</option>
                                            <option value="administrators">Administrators</option>
                                            <option value="internal-teams">Internal Teams</option>
                                            <option value="external-partners">External Partners</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="scale">Expected Scale</label>
                                        <select id="scale" required>
                                            <option value="">Select expected usage</option>
                                            <option value="small">Small (< 100 users)</option>
                                            <option value="medium">Medium (100-10k users)</option>
                                            <option value="large">Large (10k+ users)</option>
                                            <option value="enterprise">Enterprise</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="constraints">Constraints & Preferences</label>
                                        <textarea id="constraints" rows="3" placeholder="Any specific requirements, constraints, or preferences (e.g., must be cloud-native, prefer open-source, budget constraints)..."></textarea>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="form-section">
                                <h3>Key Features</h3>
                                <div id="features-container">
                                    <div class="add-feature">
                                        <input type="text" id="feature-input" placeholder="Describe a key feature or capability...">
                                        <button type="button" onclick="addFeature()">Add</button>
                                    </div>
                                    <div id="features-list"></div>
                                </div>
                            </div>
                            
                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary btn-large">Analyze Requirements</button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <div id="workflows-page" class="page">
                    <header class="page-header">
                        <h1>Workflows</h1>
                        <button class="btn btn-primary" onclick="showPage('new-project')">New Project</button>
                    </header>
                    <div id="workflows-list"></div>
                </div>
                
                <div id="approvals-page" class="page">
                    <header class="page-header">
                        <h1>Approvals</h1>
                    </header>
                    <div id="analyses-list"></div>
                </div>
                
                <div id="projects-page" class="page">
                    <header class="page-header">
                        <h1>All Projects</h1>
                        <button class="btn btn-primary" onclick="showPage('new-project')">+ New Project</button>
                    </header>
                    <div id="projects-list"></div>
                </div>
            </main>
        </div>
        
        <script src="/static/app.js"></script>
        <style>
        .markdown-content { line-height: 1.6; }
        .markdown-content h1, .markdown-content h2, .markdown-content h3 { margin: 20px 0 10px 0; color: #1f2937; }
        .markdown-content h1 { font-size: 24px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }
        .markdown-content h2 { font-size: 20px; color: #3b82f6; }
        .markdown-content h3 { font-size: 18px; color: #6b7280; }
        .markdown-content p { margin: 12px 0; }
        .markdown-content ul, .markdown-content ol { margin: 12px 0; padding-left: 24px; }
        .markdown-content li { margin: 4px 0; }
        .markdown-content strong { color: #1f2937; font-weight: 600; }
        .markdown-content code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-family: 'Monaco', 'Consolas', monospace; }
        .markdown-content pre { background: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; border: 1px solid #e5e7eb; }
        .markdown-content blockquote { border-left: 4px solid #3b82f6; padding-left: 16px; margin: 16px 0; color: #6b7280; }
        </style>
    </body>
    </html>
    """

@app.post("/api/projects")
async def create_project(requirements: ProjectRequirements):
    project_id = str(uuid.uuid4())
    workflow_id = str(uuid.uuid4())
    requirement_id = f"REQ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    project_data = {
        "id": project_id,
        "requirement_id": requirement_id,
        "workflow_id": workflow_id,
        "created_at": datetime.now().isoformat(),
        "status": "analyzing",
        **requirements.dict()
    }
    
    workflow_data = {
        "id": workflow_id,
        "project_id": project_id,
        "project_name": requirements.project_name,
        "status": "analyzing",
        "current_phase": get_workflow_config()["requirements"]["name"],
        "progress": get_workflow_config()["requirements"]["progress"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Create project folder structure
    project_path = file_manager.create_project_folder(
        requirements.project_name, 
        requirement_id
    )
    project_data["project_path"] = str(project_path)
    
    projects[project_id] = project_data
    workflows[workflow_id] = workflow_data
    
    # Persist data
    data_store.save_projects(projects)
    data_store.save_workflows(workflows)
    
    # Simulate starting the analysis after a short delay
    import asyncio
    asyncio.create_task(simulate_analysis_delay(project_id))
    
    return {"project_id": project_id, "requirement_id": requirement_id, "workflow_id": workflow_id, "status": "created"}

async def simulate_analysis_delay(project_id: str):
    """Simulate AI analysis after a delay"""
    import asyncio
    await asyncio.sleep(get_delays_config()["analysis"])
    await trigger_analysis(project_id)

async def simulate_rework_analysis(project_id: str, feedback: str):
    """Simulate AI rework analysis incorporating feedback"""
    import asyncio
    await asyncio.sleep(get_delays_config()["rework"])
    await trigger_rework_analysis(project_id, feedback)

async def simulate_code_generation(project_id: str):
    """Simulate AI code generation after approval"""
    import asyncio
    await asyncio.sleep(get_delays_config()["code_generation"])
    await complete_code_generation(project_id)

async def complete_testing(project_id: str):
    """Complete testing phase and move to documentation"""
    import asyncio
    await asyncio.sleep(get_delays_config()["testing"])
    await generate_tests(project_id)

async def generate_tests(project_id: str):
    """Run iterative test cycle with issue detection and fixing"""
    if project_id not in projects:
        return
    
    project = projects[project_id]
    workflow_id = project["workflow_id"]
    
    try:
        from agents.test_cycle_crew import TestCycleCrew
        
        crew = TestCycleCrew()
        code_content = project.get('generated_code', '')
        cycle_result = crew.run_test_cycle(project, code_content)
        
        # Store test cycle results
        projects[project_id]["final_code"] = cycle_result["final_code"]
        projects[project_id]["generated_tests"] = cycle_result["final_tests"]
        projects[project_id]["test_iterations"] = cycle_result["iterations_completed"]
        projects[project_id]["issues_log"] = cycle_result["issues_log"]
        projects[project_id]["total_issues_fixed"] = cycle_result["total_issues_fixed"]
        
        # Update generated code with final refined version
        projects[project_id]["generated_code"] = cycle_result["final_code"]
        
        # Save refined code and tests to project folder
        if "project_path" in project:
            from pathlib import Path
            project_path = Path(project["project_path"])
            
            # Save refined code
            saved_code_files = file_manager.save_code_files(project_path, cycle_result["final_code"])
            projects[project_id]["saved_files"] = [str(f) for f in saved_code_files]
            
            # Save final tests
            saved_test_files = file_manager.save_tests(project_path, cycle_result["final_tests"])
            projects[project_id]["saved_test_files"] = [str(f) for f in saved_test_files]
            
            # Save issues log
            issues_file = project_path / "issues_log.json"
            issues_file.write_text(json.dumps(cycle_result["issues_log"], indent=2), encoding='utf-8')
        
        # Update workflow to documentation phase
        if workflow_id in workflows:
            workflows[workflow_id]["status"] = "documentation"
            workflows[workflow_id]["current_phase"] = "Documentation"
            workflows[workflow_id]["progress"] = 90
            workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
            data_store.save_workflows(workflows)
        
        projects[project_id]["status"] = "documentation"
        data_store.save_projects(projects)
        
        # Trigger documentation generation
        import asyncio
        asyncio.create_task(generate_documentation(project_id))
        
    except Exception as e:
        # Fallback - skip to documentation
        projects[project_id]["generated_tests"] = f"Test cycle failed: {str(e)}"
        projects[project_id]["test_files"] = []
        projects[project_id]["issues_log"] = []
        data_store.save_projects(projects)
        
        import asyncio
        asyncio.create_task(generate_documentation(project_id))

async def generate_documentation(project_id: str):
    """Generate comprehensive documentation"""
    if project_id not in projects:
        return
    
    project = projects[project_id]
    workflow_id = project["workflow_id"]
    
    try:
        from agents.documentation_crew import DocumentationCrew
        
        crew = DocumentationCrew()
        analysis = project.get('analysis', '')
        code_content = project.get('generated_code', '')
        tests = project.get('generated_tests', '')
        
        doc_result = crew.generate_documentation(project, analysis, code_content, tests)
        
        # Store generated documentation
        projects[project_id]["generated_docs"] = doc_result["documentation"]
        projects[project_id]["doc_files"] = doc_result["doc_files"]
        
        # Save documentation to project folder
        if "project_path" in project:
            from pathlib import Path
            project_path = Path(project["project_path"])
            saved_doc_files = file_manager.save_documentation(project_path, doc_result["documentation"])
            projects[project_id]["saved_doc_files"] = [str(f) for f in saved_doc_files]
        
        data_store.save_projects(projects)
        
        # Complete deployment
        import asyncio
        asyncio.create_task(complete_deployment(project_id))
        
    except Exception as e:
        # Fallback - complete deployment anyway
        projects[project_id]["generated_docs"] = f"Documentation generation failed: {str(e)}"
        projects[project_id]["doc_files"] = []
        data_store.save_projects(projects)
        
        import asyncio
        asyncio.create_task(complete_deployment(project_id))

@app.get("/api/projects")
async def get_projects():
    return sorted(projects.values(), key=lambda x: x['created_at'], reverse=True)

@app.get("/api/workflows")
async def get_workflows():
    return list(workflows.values())

@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflows[workflow_id]

@app.get("/api/analyses")
async def get_analyses():
    return list(analyses.values())

@app.post("/api/analyses")
async def submit_analysis(analysis_data: dict):
    analysis_id = str(uuid.uuid4())
    analysis_data["id"] = analysis_id
    analysis_data["timestamp"] = datetime.now().isoformat()
    analysis_data["status"] = "pending"
    analyses[analysis_id] = analysis_data
    return {"status": "submitted", "id": analysis_id}

@app.post("/api/approve/{analysis_id}")
async def approve_analysis(analysis_id: str, approval: ApprovalRequest):
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    approvals[analysis_id] = {
        "approved": approval.approved,
        "rework": approval.rework,
        "feedback": approval.feedback,
        "timestamp": datetime.now().isoformat(),
        "analysis_id": analysis_id
    }
    
    # Add to rework history
    if "rework_history" not in analyses[analysis_id]:
        analyses[analysis_id]["rework_history"] = []
    
    action = "rework" if approval.rework else ("approved" if approval.approved else "rejected")
    analyses[analysis_id]["rework_history"].append({
        "action": action,
        "feedback": approval.feedback,
        "timestamp": datetime.now().isoformat(),
        "actor": "Human Reviewer"
    })
    
    if approval.rework:
        analyses[analysis_id]["status"] = "rework"
        # Update workflow status back to analyzing for rework
        project_id = analyses[analysis_id].get("project_id")
        if project_id and project_id in projects:
            workflow_id = projects[project_id]["workflow_id"]
            if workflow_id in workflows:
                workflows[workflow_id].update({
                    "status": "analyzing",
                    "current_phase": get_workflow_config()["requirements"]["name"],
                    "progress": get_workflow_config()["requirements"]["progress"],
                    "updated_at": datetime.now().isoformat()
                })
                projects[project_id]["status"] = "analyzing"
                
                # Trigger rework analysis with feedback
                import asyncio
                asyncio.create_task(simulate_rework_analysis(project_id, approval.feedback))
    else:
        analyses[analysis_id]["status"] = "approved" if approval.approved else "rejected"
        # Update workflow when approved
        if approval.approved:
            project_id = analyses[analysis_id].get("project_id")
            if project_id and project_id in projects:
                workflow_id = projects[project_id]["workflow_id"]
                if workflow_id in workflows:
                    workflows[workflow_id].update({
                        "status": "development",
                        "current_phase": get_workflow_config()["development"]["name"],
                        "progress": get_workflow_config()["development"]["progress"],
                        "updated_at": datetime.now().isoformat()
                    })
                    projects[project_id]["status"] = "development"
                    
                    # Trigger code generation
                    import asyncio
                    asyncio.create_task(simulate_code_generation(project_id))
    
    return {"status": "recorded", "approved": approval.approved, "rework": approval.rework}

@app.get("/api/approval-status/{analysis_id}")
async def get_approval_status(analysis_id: str):
    if analysis_id not in approvals:
        return {"status": "pending"}
    return approvals[analysis_id]

@app.post("/api/trigger-analysis/{project_id}")
async def trigger_analysis(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    
    analysis_content = ""
    
    try:
        # Use CrewAI for real analysis
        from agents.analysis_crew import AnalysisCrew
        
        crew = AnalysisCrew()
        analysis_content = crew.analyze_requirements(project)
        
        # Extract tech stack and diagrams from analysis
        tech_stack = extract_tech_stack_from_analysis(analysis_content)
        timeline = extract_timeline_from_analysis(analysis_content)
        diagrams = extract_diagrams_from_analysis(analysis_content)
        
        analysis_data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "title": f"AI Architecture Analysis for {project['project_name']}",
            "content": analysis_content,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "recommended_tech_stack": tech_stack,
            "estimated_timeline": timeline,
            "diagrams": diagrams,
            "rework_history": [{
                "action": "submitted",
                "feedback": "AI analysis completed using CrewAI and Ollama",
                "timestamp": datetime.now().isoformat(),
                "actor": "AI System (CrewAI)"
            }]
        }
        
    except Exception as e:
        # Fallback to basic analysis if CrewAI fails
        analysis_content = f"Analysis failed with CrewAI: {str(e)}\n\nFallback analysis for {project['project_name']}"
        analysis_data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "title": f"Basic Analysis for {project['project_name']}",
            "content": analysis_content,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "recommended_tech_stack": ["Python", "FastAPI"],
            "estimated_timeline": "2-4 weeks",
            "rework_history": [{
                "action": "submitted",
                "feedback": "Fallback analysis due to AI system error",
                "timestamp": datetime.now().isoformat(),
                "actor": "Fallback System"
            }]
        }
    
    analyses[analysis_data["id"]] = analysis_data
    
    # Update workflow status
    workflow_id = project["workflow_id"]
    if workflow_id in workflows:
        workflows[workflow_id]["status"] = "analysis_complete"
        workflows[workflow_id]["current_phase"] = "Human Approval"
        workflows[workflow_id]["progress"] = 50
        workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
    
    # Update project status and store analysis
    projects[project_id]["status"] = "analysis_complete"
    projects[project_id]["analysis"] = analysis_content
    
    # Save analysis to project folder
    if "project_path" in project:
        from pathlib import Path
        project_path = Path(project["project_path"])
        file_manager.save_analysis(project_path, analysis_content)
    
    return {"analysis_id": analysis_data["id"], "status": "analysis_complete", "analysis": analysis_content}

@app.post("/api/trigger-rework-analysis/{project_id}")
async def trigger_rework_analysis(project_id: str, feedback: str = ""):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    
    try:
        # Use CrewAI for real rework analysis
        from agents.analysis_crew import AnalysisCrew
        
        crew = AnalysisCrew()
        rework_content = crew.rework_analysis(project, feedback)
        
        analysis_data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "title": f"AI Revised Analysis for {project['project_name']}",
            "content": rework_content,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "recommended_tech_stack": extract_tech_stack_from_analysis(rework_content),
            "estimated_timeline": extract_timeline_from_analysis(rework_content),
            "diagrams": extract_diagrams_from_analysis(rework_content),
            "rework_history": [{
                "action": "rework_submitted",
                "feedback": f"AI rework incorporating feedback: {feedback}",
                "timestamp": datetime.now().isoformat(),
                "actor": "AI System (CrewAI)"
            }]
        }
        
    except Exception as e:
        # Fallback rework analysis
        analysis_data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "title": f"Fallback Rework for {project['project_name']}",
            "content": f"Rework failed with CrewAI: {str(e)}\n\nFeedback: {feedback}\n\nFallback rework analysis.",
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "recommended_tech_stack": ["Python"],
            "estimated_timeline": "2-3 weeks",
            "rework_history": [{
                "action": "rework_submitted",
                "feedback": f"Fallback rework due to AI error: {feedback}",
                "timestamp": datetime.now().isoformat(),
                "actor": "Fallback System"
            }]
        }
    
    analyses[analysis_data["id"]] = analysis_data
    
    # Update workflow status
    workflow_id = project["workflow_id"]
    if workflow_id in workflows:
        workflows[workflow_id]["status"] = "analysis_complete"
        workflows[workflow_id]["current_phase"] = "Human Approval"
        workflows[workflow_id]["progress"] = 50
        workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
    
    projects[project_id]["status"] = "analysis_complete"
    projects[project_id]["analysis"] = rework_content
    
    return {"analysis_id": analysis_data["id"], "status": "rework_complete", "analysis": rework_content}

@app.post("/api/complete-code-generation/{project_id}")
async def complete_code_generation(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    workflow_id = project["workflow_id"]
    
    try:
        # Use DevelopmentCrew for real code generation
        from agents.development_crew import DevelopmentCrew
        
        crew = DevelopmentCrew()
        analysis = project.get('analysis', '')
        code_result = crew.generate_code(project, analysis)
        
        # Store generated code
        projects[project_id]["generated_code"] = code_result["code"]
        projects[project_id]["files_generated"] = code_result["files_generated"]
        
        # Save code files to project folder
        if "project_path" in project:
            from pathlib import Path
            project_path = Path(project["project_path"])
            saved_files = file_manager.save_code_files(project_path, code_result["code"])
            projects[project_id]["saved_files"] = [str(f) for f in saved_files]
        
        # Update workflow to testing phase
        if workflow_id in workflows:
            workflows[workflow_id]["status"] = "testing"
            workflows[workflow_id]["current_phase"] = get_workflow_config()["testing"]["name"]
            workflows[workflow_id]["progress"] = get_workflow_config()["testing"]["progress"]
            workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
            
            # Trigger testing phase after delay
            import asyncio
            asyncio.create_task(complete_testing(project_id))
        
        projects[project_id]["status"] = "testing"
        
        return {
            "status": "code_generation_complete", 
            "project_id": project_id,
            "files_generated": code_result["files_generated"]
        }
        
    except Exception as e:
        # Fallback if code generation fails
        projects[project_id]["generated_code"] = f"Code generation failed: {str(e)}"
        projects[project_id]["files_generated"] = []
        
        return {
            "status": "code_generation_failed", 
            "project_id": project_id,
            "error": str(e)
        }

@app.post("/api/complete-deployment/{project_id}")
async def complete_deployment(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    workflow_id = project["workflow_id"]
    
    # Update workflow to completed
    if workflow_id in workflows:
        workflows[workflow_id]["status"] = "completed"
        workflows[workflow_id]["current_phase"] = get_workflow_config()["deployment"]["name"]
        workflows[workflow_id]["progress"] = get_workflow_config()["deployment"]["progress"]
        workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
    
    projects[project_id]["status"] = "completed"
    
    return {"status": "deployment_complete", "project_id": project_id}

@app.get("/api/projects/{project_id}/code")
async def get_generated_code(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    
    # Get project folder summary if available
    folder_summary = {}
    if "project_path" in project:
        from pathlib import Path
        project_path = Path(project["project_path"])
        if project_path.exists():
            folder_summary = file_manager.get_project_summary(project_path)
    
    return {
        "project_id": project_id,
        "project_name": project.get("project_name", "Unknown"),
        "generated_code": project.get("generated_code", "No code generated yet"),
        "final_code": project.get("final_code", ""),
        "files_generated": project.get("files_generated", []),
        "saved_files": project.get("saved_files", []),
        "project_path": project.get("project_path", ""),
        "folder_summary": folder_summary,
        "test_iterations": project.get("test_iterations", 0),
        "total_issues_fixed": project.get("total_issues_fixed", 0),
        "issues_log": project.get("issues_log", []),
        "status": project.get("status", "unknown")
    }

@app.get("/api/dashboard-stats")
async def get_dashboard_stats():
    active_projects = len([p for p in projects.values()])
    pending_approvals = len([a for a in analyses.values() if a.get("status") == "pending"])
    completed_workflows = len([w for w in workflows.values() if w.get("status") == "completed"])
    
    return {
        "active_projects": active_projects,
        "pending_approvals": pending_approvals,
        "completed_workflows": completed_workflows
    }

@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    
    # Get project folder summary
    folder_summary = {}
    if "project_path" in project:
        from pathlib import Path
        project_path = Path(project["project_path"])
        if project_path.exists():
            folder_summary = file_manager.get_project_summary(project_path)
    
    return {
        **project,
        "folder_summary": folder_summary
    }

@app.get("/api/projects/{project_id}/diagrams")
async def get_project_diagrams(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    diagrams = []
    
    if "project_path" in project:
        from pathlib import Path
        diagrams_dir = Path(project["project_path"]) / "analysis" / "diagrams"
        if diagrams_dir.exists():
            for diagram_file in diagrams_dir.glob("*.drawio"):
                diagrams.append({
                    "name": diagram_file.stem,
                    "filename": diagram_file.name,
                    "content": diagram_file.read_text(encoding='utf-8')
                })
    
    return {"diagrams": diagrams}

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    workflow_id = project.get("workflow_id")
    
    # Delete project folder and all artifacts
    if "project_path" in project:
        from pathlib import Path
        import shutil
        project_path = Path(project["project_path"])
        if project_path.exists():
            try:
                shutil.rmtree(project_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to delete project files: {str(e)}")
    
    # Remove from tracking
    del projects[project_id]
    
    if workflow_id and workflow_id in workflows:
        del workflows[workflow_id]
    
    # Remove related analyses and approvals
    analyses_to_remove = [aid for aid, analysis in analyses.items() if analysis.get("project_id") == project_id]
    for aid in analyses_to_remove:
        del analyses[aid]
        if aid in approvals:
            del approvals[aid]
    
    # Persist changes
    data_store.save_projects(projects)
    data_store.save_workflows(workflows)
    data_store.save_analyses(analyses)
    data_store.save_approvals(approvals)
    
    return {"status": "deleted", "project_id": project_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)