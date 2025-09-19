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
from dotenv import load_dotenv
from dataclasses import asdict
from loguru import logger

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'coding-crew', '.env'))

# Add coding-crew to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'coding-crew'))

# Import security framework
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'coding-crew', 'core'))
from security import InputSanitizer, SecurityValidator
from exceptions import ValidationError, ProjectNotFoundError, WorkflowError
from complexity_reducer import ComplexityReducer, WorkflowManager
from cache_manager import cache_manager
from async_processor import async_processor, async_analyze_requirements, async_generate_code
from local_metrics import local_metrics, Timer, timed_operation

from config import extract_tech_stack_from_analysis, extract_timeline_from_analysis, extract_diagrams_from_analysis, get_workflow_config, get_delays_config

def extract_test_plan_from_analysis(analysis_content: str) -> str:
    """Extract test plan from analysis content."""
    import re
    
    # Look for test plan sections
    test_patterns = [
        r'## Test Strategy[\s\S]*?(?=##|$)',
        r'## Test Plan[\s\S]*?(?=##|$)',
        r'Test scenarios[\s\S]*?(?=\n\n|$)',
        r'Testing approach[\s\S]*?(?=\n\n|$)'
    ]
    
    for pattern in test_patterns:
        match = re.search(pattern, analysis_content, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return "No test plan found in analysis"
from utils.file_manager import ProjectFileManager
from utils.persistence import DataStore

app = FastAPI(title="AgentAI - Professional Development Platform")

# Mount static files
app.mount("/static", StaticFiles(directory="../web/static"), name="static")

# Include security dashboard
from security_dashboard import router as security_router
app.include_router(security_router, prefix="/security")

# Initialize security components
input_sanitizer = InputSanitizer()
security_validator = SecurityValidator()
complexity_reducer = ComplexityReducer()
workflow_manager = WorkflowManager()

# Initialize Phase 3B and Phase 4 components
from debugging_assistant import DebuggingAssistant
from smart_refactoring import SmartRefactoring
from intelligent_documentation import IntelligentDocumentation
from project_manager import ProjectManager
from security_framework import SecurityFramework
from collaboration import CollaborationManager

debugging_assistant = DebuggingAssistant()
smart_refactoring = SmartRefactoring()
intelligent_docs = IntelligentDocumentation()
project_manager = ProjectManager()
security_framework = SecurityFramework()
collaboration_manager = CollaborationManager()

# Initialize Phase 3B and Phase 4 components
from debugging_assistant import DebuggingAssistant
from smart_refactoring import SmartRefactoring
from intelligent_documentation import IntelligentDocumentation
from project_manager import ProjectManager
from security_framework import SecurityFramework
from collaboration import CollaborationManager

debugging_assistant = DebuggingAssistant()
smart_refactoring = SmartRefactoring()
intelligent_docs = IntelligentDocumentation()
project_manager = ProjectManager()
security_framework = SecurityFramework()
collaboration_manager = CollaborationManager()

# Initialize performance components
@app.on_event("startup")
async def startup_event():
    await async_processor.start()
    local_metrics.start_collection()
    logger.info("AgentAI performance systems started")

@app.on_event("shutdown")
async def shutdown_event():
    await async_processor.stop()
    local_metrics.stop_collection()
    logger.info("AgentAI performance systems stopped")

class ProjectRequirements(BaseModel):
    project_name: str
    description: str
    target_users: Optional[str] = ""
    scale: Optional[str] = ""
    features: list[str]
    constraints: Optional[str] = ""
    user_story_keys: Optional[list[str]] = []

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
import os
data_dir = os.path.join(os.path.dirname(__file__), "data")
data_store = DataStore(data_dir)
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
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap">
        <link rel="stylesheet" href="/static/style.css?v=12">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/pako@2.1.0/dist/pako.min.js"></script>
    </head>
    <body>
        <div class="app-container">
            <aside class="sidebar">
                <div class="sidebar-header">
                    <h2>AgentAI</h2>
                </div>
                <nav class="sidebar-nav">
                    <a href="#" onclick="showPage('dashboard')" class="nav-item active" data-page="dashboard">
                        <i data-lucide="layout-dashboard"></i>
                        <span>Dashboard</span>
                    </a>
                    <a href="#" onclick="showPage('new-project')" class="nav-item" data-page="new-project">
                        <i data-lucide="plus-circle"></i>
                        <span>New Project</span>
                    </a>
                    <a href="#" onclick="showPage('workflows')" class="nav-item" data-page="workflows">
                        <i data-lucide="workflow"></i>
                        <span>Workflows</span>
                    </a>
                    <a href="#" onclick="showPage('approvals')" class="nav-item" data-page="approvals">
                        <i data-lucide="check-circle"></i>
                        <span>Approvals</span>
                    </a>
                    <a href="#" onclick="showPage('projects')" class="nav-item" data-page="projects">
                        <i data-lucide="folder"></i>
                        <span>Projects</span>
                    </a>
                    <a href="#" onclick="showPage('metrics')" class="nav-item" data-page="metrics">
                        <i data-lucide="bar-chart-3"></i>
                        <span>Metrics</span>
                    </a>
                    <a href="#" onclick="showPage('chat')" class="nav-item" data-page="chat">
                        <i data-lucide="message-circle"></i>
                        <span>AI Chat</span>
                    </a>
                    <a href="#" onclick="showPage('ai-insights')" class="nav-item" data-page="ai-insights">
                        <i data-lucide="brain"></i>
                        <span>AI Insights</span>
                    </a>
                </nav>
            </aside>
            
            <main class="main-content">
                <div id="dashboard-page" class="page active">
                    <nav class="breadcrumbs">
                        <span class="breadcrumb-item active">
                            <i data-lucide="home"></i>
                            Dashboard
                        </span>
                    </nav>
                    <header class="page-header">
                        <h1>Project Dashboard</h1>
                        <button class="btn btn-primary" onclick="showPage('new-project')">
                            <i data-lucide="plus"></i>
                            New Project
                        </button>
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
                    <nav class="breadcrumbs">
                        <a href="#" onclick="showPage('dashboard')" class="breadcrumb-item">
                            <i data-lucide="home"></i>
                            Dashboard
                        </a>
                        <span class="breadcrumb-separator">›</span>
                        <span class="breadcrumb-item active">New Project</span>
                    </nav>
                    <header class="page-header">
                        <h1>Create New Project</h1>
                        <button class="btn btn-secondary" onclick="showPage('dashboard')">Back</button>
                    </header>
                    
                    <div class="form-container">
                        
                        <div id="jira-mode" class="mode-section">
                            <div id="user-stories-list"></div>
                            <button type="button" id="load-stories-btn" class="btn btn-secondary">Load JIRA Stories</button>
                        </div>
                        
                        <div id="manual-mode" class="mode-section" style="display: none;">
                            <div class="requirements-note">
                                <strong>AI-Powered Analysis:</strong> Our AI will analyze your requirements and recommend the optimal technology stack, architecture patterns, and development approach.
                            </div>
                        </div>
                        
                        <div id="jira-mode-note" class="mode-section" style="display: none;">
                            <div class="requirements-note">
                                <strong>JIRA Integration:</strong> Select user stories from your JIRA project. Our AI will analyze the stories and generate the complete project structure.
                            </div>
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
                                <div class="form-row manual-only">
                                    <div class="form-group">
                                        <label for="description">Description</label>
                                        <textarea id="description" rows="3" required placeholder="What do you want to build?"></textarea>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="form-section manual-only">
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
                            
                            <div class="form-section manual-only" id="features-section">
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
                    <nav class="breadcrumbs">
                        <a href="#" onclick="showPage('dashboard')" class="breadcrumb-item">
                            <i data-lucide="home"></i>
                            Dashboard
                        </a>
                        <span class="breadcrumb-separator">›</span>
                        <span class="breadcrumb-item active">Workflows</span>
                    </nav>
                    <header class="page-header">
                        <h1>Workflows</h1>
                        <button class="btn btn-primary" onclick="showPage('new-project')">
                            <i data-lucide="plus"></i>
                            New Project
                        </button>
                    </header>
                    <div id="workflows-list"></div>
                </div>
                
                <div id="approvals-page" class="page">
                    <nav class="breadcrumbs">
                        <a href="#" onclick="showPage('dashboard')" class="breadcrumb-item">
                            <i data-lucide="home"></i>
                            Dashboard
                        </a>
                        <span class="breadcrumb-separator">›</span>
                        <span class="breadcrumb-item active">Approvals</span>
                    </nav>
                    <header class="page-header">
                        <h1>Approvals</h1>
                    </header>
                    <div id="analyses-list"></div>
                </div>
                
                <div id="projects-page" class="page">
                    <nav class="breadcrumbs">
                        <a href="#" onclick="showPage('dashboard')" class="breadcrumb-item">
                            <i data-lucide="home"></i>
                            Dashboard
                        </a>
                        <span class="breadcrumb-separator">›</span>
                        <span class="breadcrumb-item active">Projects</span>
                    </nav>
                    <header class="page-header">
                        <h1>All Projects</h1>
                        <button class="btn btn-primary" onclick="showPage('new-project')">
                            <i data-lucide="plus"></i>
                            New Project
                        </button>
                    </header>
                    <div id="projects-list"></div>
                </div>
                
                <div id="metrics-page" class="page">
                    <nav class="breadcrumbs">
                        <a href="#" onclick="showPage('dashboard')" class="breadcrumb-item">
                            <i data-lucide="home"></i>
                            Dashboard
                        </a>
                        <span class="breadcrumb-separator">›</span>
                        <span class="breadcrumb-item active">Metrics</span>
                    </nav>
                    <header class="page-header">
                        <h1>System Metrics</h1>
                        <button class="btn btn-secondary" onclick="loadMetrics()">Refresh</button>
                    </header>
                    <div id="metrics-content">
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <h3>Performance</h3>
                                <div id="performance-metrics">Loading...</div>
                            </div>
                            <div class="metric-card">
                                <h3>LLM Usage</h3>
                                <div id="llm-metrics">Loading...</div>
                            </div>
                            <div class="metric-card">
                                <h3>Workflows</h3>
                                <div id="workflow-metrics">Loading...</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="chat-page" class="page">
                    <nav class="breadcrumbs">
                        <a href="#" onclick="showPage('dashboard')" class="breadcrumb-item">
                            <i data-lucide="home"></i>
                            Dashboard
                        </a>
                        <span class="breadcrumb-separator">›</span>
                        <span class="breadcrumb-item active">AI Chat</span>
                    </nav>
                    <header class="page-header">
                        <h1>AI Assistant</h1>
                        <button class="btn btn-secondary" onclick="app.clearChat()">Clear Chat</button>
                    </header>
                    <div class="chat-container">
                        <div id="chat-messages" class="chat-messages"></div>
                        <div class="chat-input-container">
                            <input type="text" id="chat-input" placeholder="Ask me about your projects, requirements, or technical questions..." onkeypress="if(event.key==='Enter') app.sendMessage()">
                            <button onclick="app.sendMessage()" class="btn btn-primary">Send</button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
        
        <!-- Requirement Source Modal -->
        <div id="requirement-modal" class="modal" style="display: none;">
            <div class="modal-content">
                <button class="modal-close" onclick="app.closeModal()">
                    <i data-lucide="x"></i>
                </button>
                <h2>How would you like to define your project requirements?</h2>
                <div class="project-options">
                    <div class="option-card" onclick="app.selectRequirementSource('jira'); event.stopPropagation();">
                        <i data-lucide="link"></i>
                        <h3>Fetch from JIRA</h3>
                        <p>Import user stories from your JIRA project</p>
                    </div>
                    <div class="option-card" onclick="app.selectRequirementSource('manual'); event.stopPropagation();">
                        <i data-lucide="edit-3"></i>
                        <h3>Manual Entry</h3>
                        <p>Enter requirements and features manually</p>
                    </div>
                </div>
                <div class="modal-actions">
                    <button class="btn-secondary" onclick="app.closeModal()">Cancel</button>
                    <button class="btn-primary" id="continue-btn" disabled onclick="app.continueWithSelection(); return false;">Continue</button>
                </div>
            </div>
        </div>
        
        <script src="/static/app.js?v=4"></script>
        <script>
        lucide.createIcons();
        
        async function loadMetrics() {
            console.log('Global loadMetrics called');
            if (window.app && window.app.loadMetrics) {
                await window.app.loadMetrics();
            } else {
                console.error('App instance not available');
            }
        }
        
        function formatPerformanceMetrics(metrics) {
            if (!metrics || Object.keys(metrics).length === 0) {
                return '<p>No performance data available</p>';
            }
            
            let html = '';
            for (const [operation, data] of Object.entries(metrics)) {
                html += `
                    <div class="metric-item">
                        <strong>${operation}</strong><br>
                        Avg Duration: ${data.avg_duration_ms.toFixed(0)}ms<br>
                        Count: ${data.count}<br>
                        CPU: ${data.avg_cpu_percent.toFixed(1)}%
                    </div>
                `;
            }
            return html;
        }
        
        function formatLLMMetrics(metrics) {
            if (!metrics || Object.keys(metrics).length === 0) {
                return '<p>No LLM data available</p>';
            }
            
            let html = '';
            for (const [model, data] of Object.entries(metrics)) {
                html += `
                    <div class="metric-item">
                        <strong>${model}</strong><br>
                        Calls: ${data.total_calls}<br>
                        Success Rate: ${(data.success_rate * 100).toFixed(1)}%<br>
                        Tokens: ${data.total_tokens}
                    </div>
                `;
            }
            return html;
        }
        
        function formatWorkflowMetrics(metrics) {
            return '<p>Workflow metrics coming soon</p>';
        }
        
        // Initialize metrics when page loads
        setTimeout(() => {
            if (document.getElementById('metrics-page') && document.getElementById('metrics-page').classList.contains('active')) {
                loadMetrics();
            }
        }, 100);
        </script>
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
        .requirement-source-section { margin-bottom: 30px; }
        .requirement-source-section h3 { margin-bottom: 20px; color: #1f2937; }
        .source-options { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .source-option { position: relative; }
        .source-option input[type="radio"] { position: absolute; opacity: 0; }
        .source-card { display: block; padding: 20px; border: 2px solid #e5e7eb; border-radius: 12px; cursor: pointer; transition: all 0.2s; text-align: center; }
        .source-card:hover { border-color: #3b82f6; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15); }
        .source-option input:checked + .source-card { border-color: #3b82f6; background: #eff6ff; }
        .source-icon { font-size: 32px; margin-bottom: 12px; }
        .source-title { font-weight: 600; font-size: 16px; color: #1f2937; margin-bottom: 8px; }
        .source-description { font-size: 14px; color: #6b7280; }
        .mode-section { margin-bottom: 20px; padding: 16px; border: 1px solid #e5e7eb; border-radius: 8px; background: #fafbfc; }
        .jira-stories-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .stories-actions { display: flex; gap: 8px; }
        .stories-container { max-height: 400px; overflow-y: auto; border: 1px solid #e5e7eb; border-radius: 8px; }
        .story-item { margin: 0; padding: 12px; border-bottom: 1px solid #f3f4f6; }
        .story-item:last-child { border-bottom: none; }
        .story-item.jira-story { background: #f0f9ff; }
        .story-item.demo-story { background: #fef3c7; }
        .story-content { margin-left: 8px; }
        .story-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
        .story-key { color: #1f2937; font-weight: 600; }
        .story-status { padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; }
        .story-status.status-to-do { background: #f3f4f6; color: #374151; }
        .story-status.status-in-progress { background: #dbeafe; color: #1e40af; }
        .story-status.status-done { background: #d1fae5; color: #065f46; }
        .story-summary { font-weight: 500; color: #1f2937; margin-bottom: 4px; }
        .story-description { font-size: 12px; color: #6b7280; line-height: 1.4; }
        .selection-summary { margin-top: 10px; padding: 8px; background: #f9fafb; border-radius: 4px; text-align: center; font-weight: 500; }
        .error-state { text-align: center; padding: 20px; color: #dc2626; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric-card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-item { margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 4px; }
        .chat-container { display: flex; flex-direction: column; height: calc(100vh - 200px); }
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 15px; }
        .chat-message { margin-bottom: 15px; }
        .chat-message.user { text-align: right; }
        .chat-message.user .message-content { background: #007bff; color: white; display: inline-block; padding: 10px 15px; border-radius: 18px; max-width: 70%; }
        .chat-message.assistant .message-content { background: #f8f9fa; display: inline-block; padding: 10px 15px; border-radius: 18px; max-width: 70%; }
        .message-time { font-size: 11px; color: #6b7280; margin-top: 5px; }
        .chat-input-container { display: flex; gap: 10px; }
        .chat-input-container input { flex: 1; padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px; }
        .chat-input-container button { padding: 12px 20px; }
        .modern-analysis-card { background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin: 16px 0; overflow: hidden; }
        .modern-approval-container { background: white; }
        .approval-tabs { display: flex; border-bottom: 1px solid #e5e7eb; background: #f8fafc; }
        .approval-tabs .tab-btn { flex: 1; padding: 16px; border: none; background: none; cursor: pointer; font-weight: 500; color: #6b7280; transition: all 0.2s; }
        .approval-tabs .tab-btn.active { color: #007bff; border-bottom: 2px solid #007bff; background: white; }
        .approval-tab-content { display: none; padding: 24px; }
        .approval-tab-content.active { display: block; }
        .analysis-summary { background: #fafbfc; padding: 20px; border-radius: 8px; }
        .architect-chat { min-height: 300px; }
        .chat-header { text-align: center; padding: 16px; border-bottom: 1px solid #e5e7eb; }
        .chat-header h4 { margin: 0 0 8px 0; color: #1f2937; }
        .chat-header p { margin: 0; color: #6b7280; font-size: 14px; }
        .mini-chat-messages { height: 200px; overflow-y: auto; padding: 16px; border: 1px solid #e5e7eb; border-radius: 8px; margin: 16px 0; background: #fafbfc; }
        .mini-chat-input { display: flex; gap: 8px; }
        .mini-chat-input input { flex: 1; padding: 10px; border: 1px solid #e5e7eb; border-radius: 6px; }
        .decision-panel { text-align: center; }
        .decision-panel h4 { color: #1f2937; margin-bottom: 20px; }
        .decision-buttons { display: flex; gap: 12px; justify-content: center; margin: 20px 0; flex-wrap: wrap; }
        .modern-feedback { width: 100%; padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px; min-height: 80px; margin-top: 16px; resize: vertical; }
        .btn-success { background: #10b981; color: white; border: none; }
        .btn-warning { background: #f59e0b; color: white; border: none; }
        .btn-danger { background: #ef4444; color: white; border: none; }
        .btn-small { padding: 8px 16px; font-size: 14px; }
        .approval-tab-content { position: relative; z-index: 1; }
        .approval-tab-content:not(.active) { display: none !important; }
        .test-plan-section h4 { color: #1f2937; margin-bottom: 16px; }
        .test-content { background: #f0f9ff; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
        .no-tests { color: #6b7280; font-style: italic; text-align: center; padding: 40px; }
        </style>
    </body>
    </html>
    """

@app.post("/api/projects")
async def create_project(requirements: ProjectRequirements):
    try:
        # Sanitize and validate inputs
        sanitized_data = input_sanitizer.sanitize_dict(requirements.dict())
        
        # Validate project name
        if not input_sanitizer.validate_project_id(sanitized_data['project_name']):
            raise ValidationError("Invalid project name format")
        
        project_id = str(uuid.uuid4())
        workflow_id = str(uuid.uuid4())
        requirement_id = f"REQ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Start workflow tracking
        try:
            from core.performance_monitor import workflow_metrics
            workflow_metrics.start_workflow(project_id, "full_development")
        except ImportError:
            pass  # Performance monitoring optional
        
        project_data = {
            "id": project_id,
            "requirement_id": requirement_id,
            "workflow_id": workflow_id,
            "created_at": datetime.now().isoformat(),
            "status": "analyzing",
            **sanitized_data
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project creation failed: {str(e)}")
    
    # Get JIRA user stories if provided
    if requirements.user_story_keys:
        try:
            from core.mcp_integration import MCPIntegration
            mcp = MCPIntegration()
            stories_data = await mcp.get_user_stories(requirements.user_story_keys)
            project_data["user_stories"] = stories_data
        except Exception as e:
            print(f"JIRA user stories fetch failed: {e}")
            project_data["user_stories"] = {"user_stories": []}
    
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
    
    # Persist data immediately
    data_store.save_projects(projects)
    data_store.save_workflows(workflows)
    print(f"Saved project {project_id} and workflow {workflow_id}")
    
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
        
        # Run intelligent test analysis
        try:
            from agents.intelligent_test_generator import IntelligentTestGenerator
            test_generator = IntelligentTestGenerator()
            
            # Analyze test coverage
            coverage_analysis = test_generator.analyze_test_coverage(
                cycle_result["final_tests"], 
                cycle_result["final_code"]
            )
            projects[project_id]["test_coverage_analysis"] = coverage_analysis
            
            # Generate security tests
            security_tests = test_generator.generate_security_tests(
                cycle_result["final_code"], 
                tech_stack
            )
            projects[project_id]["security_tests"] = security_tests
            
        except Exception as e:
            logger.warning(f"Intelligent test analysis failed: {e}")
            projects[project_id]["test_coverage_analysis"] = {"coverage_percentage": 0}
            projects[project_id]["security_tests"] = {"security_categories": []}
        
        # Update generated code with final refined version
        projects[project_id]["generated_code"] = cycle_result["final_code"]
        
        # Save refined code and tests to project folder
        if "project_path" in project:
            from pathlib import Path
            project_path = Path(project["project_path"])
            
            # Get tech stack
            tech_stack = project.get('recommended_tech_stack', [])
            
            # Save refined code
            saved_code_files = file_manager.save_code_files(project_path, cycle_result["final_code"], tech_stack)
            projects[project_id]["saved_files"] = [str(f) for f in saved_code_files]
            
            # Save final tests
            saved_test_files = file_manager.save_tests(project_path, cycle_result["final_tests"], tech_stack)
            projects[project_id]["saved_test_files"] = [str(f) for f in saved_test_files]
            
            # Save issues log
            issues_file = project_path / "issues_log.json"
            issues_file.write_text(json.dumps(cycle_result["issues_log"], indent=2), encoding='utf-8')
            
            # NEW: Run deployment validation
            await validate_deployment(project_id)
        
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

async def validate_deployment(project_id: str):
    """NEW: Validate that project can actually be deployed and run"""
    if project_id not in projects:
        return
    
    project = projects[project_id]
    
    try:
        from agents.deployment_validation_crew import DeploymentValidationCrew
        from pathlib import Path
        
        validator = DeploymentValidationCrew()
        project_path = Path(project["project_path"])
        tech_stack = project.get('recommended_tech_stack', [])
        
        validation_result = validator.validate_project_deployment(project_path, tech_stack)
        
        # Store validation results
        projects[project_id]["deployment_validation"] = validation_result
        projects[project_id]["deployment_ready"] = validation_result.get("deployment_ready", False)
        projects[project_id]["git_ready"] = validation_result.get("git_ready", False)
        
        data_store.save_projects(projects)
        
    except Exception as e:
        projects[project_id]["deployment_validation"] = {
            "status": "ERROR",
            "error": str(e),
            "deployment_ready": False,
            "git_ready": False
        }
        data_store.save_projects(projects)

async def generate_documentation(project_id: str):
    """Generate comprehensive documentation"""
    if project_id not in projects:
        return
    
    project = projects[project_id]
    workflow_id = project["workflow_id"]
    
    try:
        from agents.documentation_crew import DocumentationCrew
        from agents.documentation_validator_crew import DocumentationValidatorCrew
        
        crew = DocumentationCrew()
        analysis = project.get('analysis', '')
        code_content = project.get('generated_code', '')
        tests = project.get('generated_tests', '')
        
        doc_result = crew.generate_documentation(project, analysis, code_content, tests)
        
        # Validate documentation against requirements
        validator = DocumentationValidatorCrew()
        validation_result = validator.validate_documentation(
            project, 
            doc_result["documentation"], 
            analysis
        )
        
        # Store generated documentation and validation
        projects[project_id]["generated_docs"] = doc_result["documentation"]
        projects[project_id]["doc_files"] = doc_result["doc_files"]
        projects[project_id]["doc_validation"] = validation_result
        
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
        projects[project_id]["doc_validation"] = {"validation_status": "ERROR", "error": str(e)}
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
@timed_operation("analysis.total_duration_ms")
async def trigger_analysis(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Start performance monitoring
    op_id = None
    try:
        from core.performance_monitor import performance_monitor, workflow_metrics
        op_id = performance_monitor.start_operation(
            f"analysis_{project_id}", 
            "requirements_analysis",
            agent_type="analysis",
            project_id=project_id
        )
    except ImportError:
        pass  # Performance monitoring optional
    
    project = projects[project_id]
    
    # Check cache first
    cached_analysis = await cache_manager.get_cached_analysis(project)
    if cached_analysis:
        local_metrics.record_counter("cache.hits")
        logger.info(f"Using cached analysis for project {project_id}")
        
        analysis_data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "title": f"Cached Analysis for {project['project_name']}",
            "content": cached_analysis,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "recommended_tech_stack": extract_tech_stack_from_analysis(cached_analysis),
            "estimated_timeline": extract_timeline_from_analysis(cached_analysis),
            "cached": True
        }
        
        analyses[analysis_data["id"]] = analysis_data
        data_store.save_analyses(analyses)
        
        # Update workflow status
        workflow_id = project["workflow_id"]
        if workflow_id in workflows:
            workflows[workflow_id]["status"] = "analysis_complete"
            workflows[workflow_id]["current_phase"] = "Human Approval"
            workflows[workflow_id]["progress"] = 50
            workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
            data_store.save_workflows(workflows)
        
        projects[project_id]["status"] = "analysis_complete"
        projects[project_id]["analysis"] = cached_analysis
        data_store.save_projects(projects)
        
        return {"analysis_id": analysis_data["id"], "status": "analysis_complete", "analysis": cached_analysis, "cached": True}
    
    local_metrics.record_counter("cache.misses")
    
    # Process JIRA user stories as structured requirements
    if project.get("user_stories") and project["user_stories"].get("user_stories"):
        stories = project["user_stories"]["user_stories"]
        
        # Convert JIRA stories to structured features
        jira_features = []
        user_stories_text = "\n\n## JIRA User Stories Analysis:\n"
        
        for story in stories:
            story_key = story.get('key', 'N/A')
            story_summary = story.get('summary', 'N/A')
            story_desc = story.get('description', '')
            
            # Add story as a feature
            feature_text = f"{story_key}: {story_summary}"
            jira_features.append(feature_text)
            
            # Build detailed analysis text
            user_stories_text += f"\n### {story_key}: {story_summary}\n"
            if story_desc:
                user_stories_text += f"**Description:** {story_desc}\n"
            user_stories_text += f"**Status:** {story.get('status', 'Unknown')}\n"
        
        # Update project with JIRA-derived features and enhanced description
        project["features"] = jira_features
        project["jira_story_count"] = len(stories)
        project["enhanced_description"] = project["description"] + user_stories_text
        
        # Set appropriate target users and scale based on story count
        if not project.get("target_users") or project["target_users"] == "":
            project["target_users"] = "business-users"  # Default for JIRA projects
        if not project.get("scale") or project["scale"] == "":
            if len(stories) <= 3:
                project["scale"] = "small"
            elif len(stories) <= 10:
                project["scale"] = "medium"
            else:
                project["scale"] = "large"
    
    analysis_content = ""
    test_plan = ""
    
    try:
        # Use CrewAI for real analysis with parallel test planning
        from agents.analysis_crew import AnalysisCrew
        from agents.test_validator_crew import AutomatedTestValidator
        
        crew = AnalysisCrew()
        analysis_content = crew.analyze_requirements(project)
        
        # Extract test plan from analysis (it's now included)
        test_plan = extract_test_plan_from_analysis(analysis_content)
        
        # Validate test-story alignment
        if project.get('user_stories') and project['user_stories'].get('user_stories'):
            primary_story = project['user_stories']['user_stories'][0]
            test_validator = AutomatedTestValidator()
            test_validation = test_validator.validate_test_story_alignment(test_plan, primary_story)
            
            if not test_validation['approved']:
                # Add test validation feedback to analysis
                analysis_content += f"\n\n## Test Validation Issues:\n{test_validation['justification']}\n"
                analysis_content += f"Coverage Gaps: {test_validation['coverage_gaps']}\n"
        
        # Cache the analysis result
        await cache_manager.cache_analysis(project, analysis_content)
        local_metrics.record_counter("analyses.completed")
        
        # Extract tech stack and diagrams from analysis
        tech_stack = extract_tech_stack_from_analysis(analysis_content)
        timeline = extract_timeline_from_analysis(analysis_content)
        diagrams = extract_diagrams_from_analysis(analysis_content)
        
        analysis_data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "title": f"AI Story-Focused Analysis for {project['project_name']}",
            "content": analysis_content,
            "test_plan": test_plan,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "recommended_tech_stack": tech_stack,
            "estimated_timeline": timeline,
            "diagrams": diagrams,
            "rework_history": [{
                "action": "submitted",
                "feedback": "AI analysis with story-first approach and test planning",
                "timestamp": datetime.now().isoformat(),
                "actor": "AI System (CrewAI)"
            }]
        }
        
        # End performance monitoring
        metrics = performance_monitor.end_operation(op_id, tokens_processed=len(analysis_content.split()))
        workflow_metrics.record_phase(project_id, "analysis", metrics.duration_ms if metrics else 0, True)
        
    except Exception as e:
        # Fallback to basic analysis if CrewAI fails
        analysis_content = f"Analysis failed with CrewAI: {str(e)}\n\nFallback analysis for {project['project_name']}"
        test_plan = "Basic test plan: Verify application starts and responds"
        analysis_data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "title": f"Basic Analysis for {project['project_name']}",
            "content": analysis_content,
            "test_plan": test_plan,
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
        
        # End performance monitoring with error
        performance_monitor.end_operation(op_id)
        workflow_metrics.record_phase(project_id, "analysis", 0, False, str(e))
    
    analyses[analysis_data["id"]] = analysis_data
    data_store.save_analyses(analyses)
    
    # Update workflow status
    workflow_id = project["workflow_id"]
    if workflow_id in workflows:
        workflows[workflow_id]["status"] = "analysis_complete"
        workflows[workflow_id]["current_phase"] = "Human Approval"
        workflows[workflow_id]["progress"] = 50
        workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
        data_store.save_workflows(workflows)
    
    # Update project status and store analysis
    projects[project_id]["status"] = "analysis_complete"
    data_store.save_projects(projects)
    projects[project_id]["analysis"] = analysis_content
    projects[project_id]["recommended_tech_stack"] = analysis_data.get("recommended_tech_stack", [])
    
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
    data_store.save_analyses(analyses)
    
    # Update workflow status
    workflow_id = project["workflow_id"]
    if workflow_id in workflows:
        workflows[workflow_id]["status"] = "analysis_complete"
        workflows[workflow_id]["current_phase"] = "Human Approval"
        workflows[workflow_id]["progress"] = 50
        workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
        data_store.save_workflows(workflows)
    
    projects[project_id]["status"] = "analysis_complete"
    data_store.save_projects(projects)
    projects[project_id]["analysis"] = analysis_data["content"]
    projects[project_id]["recommended_tech_stack"] = analysis_data.get("recommended_tech_stack", [])
    
    return {"analysis_id": analysis_data["id"], "status": "rework_complete", "analysis": rework_content}

@app.post("/api/complete-code-generation/{project_id}")
async def complete_code_generation(project_id: str):
    from core.performance_monitor import performance_monitor, workflow_metrics
    
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    workflow_id = project["workflow_id"]
    
    # Start performance monitoring
    op_id = performance_monitor.start_operation(
        f"coding_{project_id}", 
        "code_generation",
        agent_type="coding",
        project_id=project_id
    )
    
    try:
        # Use Enhanced DevelopmentCrew for real code generation
        from agents.enhanced_development_crew import EnhancedDevelopmentCrew
        from agents.story_validation_crew import StoryValidationCrew
        
        crew = EnhancedDevelopmentCrew()
        analysis = project.get('analysis', '')
        code_result = crew.generate_code(project, analysis)
        
        # Store generated code
        projects[project_id]["generated_code"] = code_result["code"]
        projects[project_id]["files_generated"] = code_result["files_generated"]
        
        # Run AI code quality analysis
        try:
            from agents.code_quality_ai import CodeQualityAI
            code_quality_ai = CodeQualityAI()
            quality_analysis = code_quality_ai.review_code(code_result["code"], tech_stack)
            projects[project_id]["code_quality_analysis"] = quality_analysis
            
            # Run architecture analysis
            from agents.architecture_advisor import ArchitectureAdvisor
            arch_advisor = ArchitectureAdvisor()
            arch_analysis = arch_advisor.analyze_architecture(code_result["code"], project, tech_stack)
            projects[project_id]["architecture_analysis"] = arch_analysis
            
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            projects[project_id]["code_quality_analysis"] = {"quality_score": 0, "issues_found": []}
            projects[project_id]["architecture_analysis"] = {"architecture_score": 0, "recommendations": []}
        
        # Get and store tech stack
        tech_stack = project.get('recommended_tech_stack', [])
        if not tech_stack:
            # Try to extract from analysis content
            analysis_content = project.get('analysis', '')
            tech_stack = extract_tech_stack_from_analysis(analysis_content)
            projects[project_id]['recommended_tech_stack'] = tech_stack
        
        # Save code files to project folder
        if "project_path" in project:
            from pathlib import Path
            project_path = Path(project["project_path"])
            saved_files = file_manager.save_code_files(project_path, code_result["code"], tech_stack)
            projects[project_id]["saved_files"] = [str(f) for f in saved_files]
            
            # Get folder summary for validation
            folder_summary = file_manager.get_project_summary(project_path)
            
            # Validate story completion
            story_validator = StoryValidationCrew()
            validation_result = story_validator.validate_story_completion(project, {
                "code_files": [str(f) for f in saved_files],
                "folder_summary": folder_summary
            })
            
            projects[project_id]["story_validation"] = validation_result
            
            # If story validation fails, add to issues
            if validation_result.get("validation") != "PASS":
                projects[project_id]["story_compliance_issues"] = validation_result.get("gaps", [])
        
        # End performance monitoring
        metrics = performance_monitor.end_operation(op_id, tokens_processed=len(code_result["code"].split()))
        workflow_metrics.record_phase(project_id, "development", metrics.duration_ms if metrics else 0, True)
        
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
            "files_generated": code_result["files_generated"],
            "story_validation": projects[project_id].get("story_validation", {})
        }
        
    except Exception as e:
        # End performance monitoring with error
        performance_monitor.end_operation(op_id)
        workflow_metrics.record_phase(project_id, "development", 0, False, str(e))
        
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
    from core.performance_monitor import workflow_metrics
    
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
    
    # End workflow tracking
    workflow_metrics.end_workflow(project_id, True, "completed")
    
    return {"status": "deployment_complete", "project_id": project_id}

@app.get("/api/metrics")
async def get_system_metrics():
    """Get comprehensive system metrics."""
    current_metrics = local_metrics.get_current_metrics()
    performance_summary = local_metrics.get_performance_summary()
    cache_stats = cache_manager.get_stats()
    async_stats = async_processor.get_stats()
    
    return {
        "system": current_metrics["system"],
        "process": current_metrics["process"],
        "application": current_metrics["application"],
        "performance": performance_summary,
        "cache": cache_stats,
        "async_processing": async_stats,
        "projects": {
            "total": len(projects),
            "completed": len([p for p in projects.values() if p.get('status') == 'completed']),
            "active": len([p for p in projects.values() if p.get('status') not in ['completed', 'failed']])
        }
    }

@app.get("/api/performance/tasks")
async def get_async_tasks():
    """Get all async tasks status."""
    tasks = await async_processor.get_all_tasks()
    return {
        "tasks": [asdict(task) for task in tasks.values()],
        "stats": async_processor.get_stats()
    }

@app.get("/api/performance/cache")
async def get_cache_status():
    """Get cache performance status."""
    return cache_manager.get_stats()

@app.get("/api/projects/{project_id}/ai-insights")
async def get_ai_insights(project_id: str):
    """Get AI-powered insights for a project."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    
    return {
        "project_id": project_id,
        "code_quality": project.get("code_quality_analysis", {}),
        "architecture": project.get("architecture_analysis", {}),
        "test_coverage": project.get("test_coverage_analysis", {}),
        "security_tests": project.get("security_tests", {}),
        "ai_insights": project.get("ai_insights", {})
    }

@app.post("/api/projects/{project_id}/analyze-code-quality")
async def analyze_code_quality(project_id: str):
    """Run AI code quality analysis on demand."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    code_content = project.get("generated_code", "")
    tech_stack = project.get("recommended_tech_stack", [])
    
    if not code_content:
        raise HTTPException(status_code=400, detail="No code available for analysis")
    
    try:
        from agents.code_quality_ai import CodeQualityAI
        code_quality_ai = CodeQualityAI()
        analysis = code_quality_ai.review_code(code_content, tech_stack)
        
        projects[project_id]["code_quality_analysis"] = analysis
        data_store.save_projects(projects)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code quality analysis failed: {str(e)}")

@app.post("/api/projects/{project_id}/generate-intelligent-tests")
async def generate_intelligent_tests(project_id: str):
    """Generate intelligent tests on demand."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    code_content = project.get("generated_code", "")
    tech_stack = project.get("recommended_tech_stack", [])
    
    if not code_content:
        raise HTTPException(status_code=400, detail="No code available for test generation")
    
    try:
        from agents.intelligent_test_generator import IntelligentTestGenerator
        test_generator = IntelligentTestGenerator()
        
        # Generate comprehensive tests
        test_results = test_generator.generate_comprehensive_tests(code_content, project, tech_stack)
        
        # Generate security tests
        security_tests = test_generator.generate_security_tests(code_content, tech_stack)
        
        projects[project_id]["intelligent_tests"] = test_results
        projects[project_id]["security_tests"] = security_tests
        data_store.save_projects(projects)
        
        return {
            "comprehensive_tests": test_results,
            "security_tests": security_tests
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligent test generation failed: {str(e)}")

@app.post("/api/projects/{project_id}/architecture-review")
async def architecture_review(project_id: str):
    """Run architecture review on demand."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    code_content = project.get("generated_code", "")
    tech_stack = project.get("recommended_tech_stack", [])
    
    if not code_content:
        raise HTTPException(status_code=400, detail="No code available for architecture review")
    
    try:
        from agents.architecture_advisor import ArchitectureAdvisor
        arch_advisor = ArchitectureAdvisor()
        
        # Analyze current architecture
        analysis = arch_advisor.analyze_architecture(code_content, project, tech_stack)
        
        # Get refactoring suggestions if there are issues
        quality_analysis = project.get("code_quality_analysis", {})
        issues = [issue["description"] for issue in quality_analysis.get("issues_found", [])]
        
        if issues:
            refactoring = arch_advisor.suggest_refactoring(code_content, issues)
            analysis["refactoring_suggestions"] = refactoring
        
        projects[project_id]["architecture_analysis"] = analysis
        data_store.save_projects(projects)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Architecture review failed: {str(e)}")

@app.get("/metrics")
async def metrics_dashboard():
    """Serve metrics dashboard page"""
    from fastapi.responses import FileResponse
    return FileResponse("web/static/metrics.html")

@app.get("/security-dashboard")
async def security_dashboard():
    """Serve security dashboard page"""
    from fastapi.responses import FileResponse
    return FileResponse("web/templates/security_dashboard.html")

@app.get("/ai-insights/{project_id}")
async def ai_insights_dashboard(project_id: str):
    """Serve AI insights dashboard page"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Insights - {project_id}</title>
        <link rel="stylesheet" href="/static/style.css">
        <link rel="stylesheet" href="/static/ai_insights.css">
        <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    </head>
    <body>
        <div class="ai-insights-dashboard">
            <header class="page-header">
                <h1>AI Insights Dashboard</h1>
                <div class="ai-actions">
                    <button class="btn-ai" onclick="runCodeQualityAnalysis()">
                        <i data-lucide="search"></i>
                        Analyze Code Quality
                    </button>
                    <button class="btn-ai" onclick="generateIntelligentTests()">
                        <i data-lucide="shield-check"></i>
                        Generate Smart Tests
                    </button>
                    <button class="btn-ai" onclick="reviewArchitecture()">
                        <i data-lucide="layers"></i>
                        Review Architecture
                    </button>
                </div>
            </header>
            
            <div class="insights-summary" id="insights-summary">
                <div class="insight-card quality">
                    <div class="insight-title">Code Quality</div>
                    <div class="insight-score" id="quality-score">-</div>
                    <div class="insight-description">Overall code quality assessment</div>
                </div>
                <div class="insight-card architecture">
                    <div class="insight-title">Architecture</div>
                    <div class="insight-score" id="architecture-score">-</div>
                    <div class="insight-description">System design quality</div>
                </div>
                <div class="insight-card testing">
                    <div class="insight-title">Test Coverage</div>
                    <div class="insight-score" id="coverage-score">-</div>
                    <div class="insight-description">Test completeness percentage</div>
                </div>
                <div class="insight-card security">
                    <div class="insight-title">Security Tests</div>
                    <div class="insight-score" id="security-score">-</div>
                    <div class="insight-description">Security test categories</div>
                </div>
            </div>
            
            <div class="recommendations-section">
                <h2>AI Recommendations</h2>
                <div id="recommendations-container">
                    <p>Run AI analysis to get personalized recommendations</p>
                </div>
            </div>
            
            <div class="issues-grid" id="issues-grid">
                <!-- Issues will be populated by JavaScript -->
            </div>
        </div>
        
        <script>
            const projectId = '{project_id}';
            
            async function loadInsights() {{
                try {{
                    const response = await fetch(`/api/projects/${{projectId}}/ai-insights`);
                    const data = await response.json();
                    
                    // Update scores
                    document.getElementById('quality-score').textContent = data.ai_insights.code_quality_score || 0;
                    document.getElementById('architecture-score').textContent = data.ai_insights.architecture_score || 0;
                    document.getElementById('coverage-score').textContent = data.ai_insights.test_coverage || 0;
                    document.getElementById('security-score').textContent = data.ai_insights.security_tests_count || 0;
                    
                    // Update recommendations
                    displayRecommendations(data.code_quality?.recommendations || []);
                    displayIssues(data.code_quality?.issues_found || []);
                    
                }} catch (error) {{
                    console.error('Failed to load insights:', error);
                }}
            }}
            
            async function runCodeQualityAnalysis() {{
                showLoading('Analyzing code quality...');
                try {{
                    await fetch(`/api/projects/${{projectId}}/analyze-code-quality`, {{ method: 'POST' }});
                    await loadInsights();
                }} catch (error) {{
                    alert('Code quality analysis failed');
                }}
                hideLoading();
            }}
            
            async function generateIntelligentTests() {{
                showLoading('Generating intelligent tests...');
                try {{
                    await fetch(`/api/projects/${{projectId}}/generate-intelligent-tests`, {{ method: 'POST' }});
                    await loadInsights();
                }} catch (error) {{
                    alert('Test generation failed');
                }}
                hideLoading();
            }}
            
            async function reviewArchitecture() {{
                showLoading('Reviewing architecture...');
                try {{
                    await fetch(`/api/projects/${{projectId}}/architecture-review`, {{ method: 'POST' }});
                    await loadInsights();
                }} catch (error) {{
                    alert('Architecture review failed');
                }}
                hideLoading();
            }}
            
            function displayRecommendations(recommendations) {{
                const container = document.getElementById('recommendations-container');
                if (recommendations.length === 0) {{
                    container.innerHTML = '<p>No recommendations available. Run AI analysis first.</p>';
                    return;
                }}
                
                container.innerHTML = recommendations.map(rec => `
                    <div class="recommendation-item ${{rec.priority?.toLowerCase() || 'medium'}}">
                        <div class="recommendation-title">
                            ${{rec.title || rec.description?.substring(0, 100) || 'Recommendation'}}
                            <span class="priority-badge priority-${{rec.priority?.toLowerCase() || 'medium'}}">
                                ${{rec.priority || 'Medium'}}
                            </span>
                        </div>
                        <div class="recommendation-description">
                            ${{rec.description || rec.title || 'No description available'}}
                        </div>
                    </div>
                `).join('');
            }}
            
            function displayIssues(issues) {{
                const container = document.getElementById('issues-grid');
                if (issues.length === 0) return;
                
                container.innerHTML = `
                    <div class="issue-category">
                        <h3>Code Quality Issues</h3>
                        <ul class="issue-list">
                            ${{issues.map(issue => `
                                <li class="issue-item">
                                    <span class="issue-text">${{issue.description}}</span>
                                    <span class="severity-badge severity-${{issue.severity?.toLowerCase() || 'medium'}}">
                                        ${{issue.severity || 'Medium'}}
                                    </span>
                                </li>
                            `).join('')}}
                        </ul>
                    </div>
                `;
            }}
            
            function showLoading(message) {{
                // Simple loading implementation
                document.body.style.cursor = 'wait';
            }}
            
            function hideLoading() {{
                document.body.style.cursor = 'default';
            }}
            
            // Load insights on page load
            document.addEventListener('DOMContentLoaded', loadInsights);
            lucide.createIcons();
        </script>
    </body>
    </html>
    """

@app.get("/api/projects/{project_id}/code")
async def get_generated_code(project_id: str):
    # Validate project_id format to prevent path traversal
    if not project_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    
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
        "code_quality_analysis": project.get("code_quality_analysis", {}),
        "architecture_analysis": project.get("architecture_analysis", {}),
        "test_coverage_analysis": project.get("test_coverage_analysis", {}),
        "security_tests": project.get("security_tests", {}),
        "deployment_validation": project.get("deployment_validation", {}),
        "deployment_ready": project.get("deployment_ready", False),
        "git_ready": project.get("git_ready", False),
        "status": project.get("status", "unknown"),
        "ai_insights": {
            "code_quality_score": project.get("code_quality_analysis", {}).get("quality_score", 0),
            "architecture_score": project.get("architecture_analysis", {}).get("architecture_score", 0),
            "test_coverage": project.get("test_coverage_analysis", {}).get("coverage_percentage", 0),
            "security_tests_count": len(project.get("security_tests", {}).get("security_categories", []))
        }
    }

@app.get("/api/jira-stories")
async def get_jira_stories():
    try:
        # Use direct Python execution in container (method we know works)
        import asyncio
        import json
        
        # Use direct JIRA integration
        try:
            from core.jira_integration import get_jira_integration
            jira_integration = await get_jira_integration()
            stories = await jira_integration.get_user_stories(project="KW", limit=100)
            
            if stories:
                return {"stories": stories, "source": "direct-jira", "total": len(stories)}
            else:
                return {"stories": [], "error": "No stories found", "source": "empty-jira"}
                
        except Exception as jira_error:
            return {"stories": [], "error": f"JIRA integration error: {str(jira_error)}", "source": "jira-error"}
        
    except Exception as e:
        # Fallback to demo data
        demo_stories = [
            {"key": "DEMO-001", "summary": "User Authentication System", "status": "To Do", "description": "Implement secure user login and registration"},
            {"key": "DEMO-002", "summary": "Dashboard Analytics", "status": "In Progress", "description": "Create real-time analytics dashboard"},
            {"key": "DEMO-003", "summary": "API Integration", "status": "To Do", "description": "Integrate with third-party APIs"}
        ]
        return {"stories": demo_stories, "error": f"JIRA integration failed: {str(e)}", "source": "demo"}

@app.get("/api/mcp-status")
async def get_mcp_status():
    try:
        from core.mcp_integration import MCPIntegration
        mcp = MCPIntegration()
        return mcp.get_status()
    except Exception as e:
        return {"mcp_enabled": False, "error": str(e)}

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
    # Validate project_id format to prevent path traversal
    if not project_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    
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

@app.post("/api/analysis-chat")
async def analysis_chat(request: dict):
    """Chat with AI architect about specific analysis."""
    message = request.get('message', '')
    analysis_id = request.get('analysisId', '')
    
    if analysis_id not in analyses:
        return {"response": "I don't have access to that analysis. Please check the analysis ID."}
    
    analysis = analyses[analysis_id]
    project_id = analysis.get('project_id')
    project = projects.get(project_id, {}) if project_id else {}
    
    # Use direct architect responses grounded in analysis data
    tech_stack = analysis.get('recommended_tech_stack', [])
    timeline = analysis.get('estimated_timeline', '2-4 weeks')
    project_name = project.get('project_name', 'this project')
    message_lower = message.lower()
    
    # Check for React and Angular questions
    has_react = 'react' in message_lower
    has_angular = 'angular' in message_lower
    
    if has_react and has_angular:
        return {"response": f"For {project_name}, I've included both React and Angular in my architecture. React will handle the dynamic UI components with its excellent virtual DOM performance, while Angular provides the enterprise framework structure for complex business logic. The coding agents will implement both - React for the interactive frontend components and Angular for the structured application framework. This gives us both flexibility and enterprise-grade robustness."}
    elif has_react:
        return {"response": f"I chose React as part of the tech stack because it's perfect for building the component-based UI {project_name} needs. The coding agents will implement React components following my architectural specifications - clean, reusable, and performant. React's virtual DOM aligns with the scalable patterns I've designed."}
    elif has_angular:
        return {"response": f"Angular is in my recommended stack because {project_name} needs enterprise-grade structure and TypeScript support. The coding agents will use Angular's dependency injection and framework features to implement the business logic layer I've architected. It provides the robust foundation for complex workflows."}
    elif any(word in message_lower for word in ['tech', 'stack', 'technology']):
        return {"response": f"I analyzed the requirements and selected {', '.join(tech_stack)} as the optimal stack. Each serves a specific architectural purpose: Express for the API layer, React/Angular for different UI needs, PostgreSQL for data persistence, Docker for deployment, Jest for testing, and AWS for cloud infrastructure. The coding agents will implement using exactly this stack."}
    elif any(word in message_lower for word in ['timeline', 'time']):
        return {"response": f"My {timeline} estimate accounts for the coding agents implementing the full stack I've designed - {', '.join(tech_stack[:3])} and supporting technologies. This includes development sprints, testing cycles with Jest, and AWS deployment validation."}
    else:
        return {"response": f"I'm the AI architect who designed this system using {', '.join(tech_stack)}. I can explain why I chose React vs Angular, the Express API architecture, PostgreSQL data design, or how our coding agents will implement any part of my technical specifications. What interests you?"}

@app.post("/api/chat")
async def chat_with_ai(request: dict):
    """AI chat endpoint for user questions."""
    message = request.get('message', '')
    context = request.get('context', {})
    
    try:
        from agents.chat_assistant import ChatAssistant
        assistant = ChatAssistant()
        response = assistant.respond(message, context, projects, analyses)
        return {"response": response}
    except Exception:
        # Fallback response
        if 'project' in message.lower():
            return {"response": f"You have {len(projects)} projects. Would you like me to help with requirements, technology choices, or project planning?"}
        elif 'tech' in message.lower() or 'stack' in message.lower():
            return {"response": "I can recommend technology stacks based on your requirements. What type of application are you building?"}
        else:
            return {"response": "I can help with project requirements, technology recommendations, and development questions. What would you like to know?"}

@app.get("/api/diagram-png/{analysis_id}/{diagram_index}")
async def get_diagram_png(analysis_id: str, diagram_index: int):
    """Convert Draw.io XML to PNG image."""
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analyses[analysis_id]
    if not analysis.get('diagrams') or diagram_index >= len(analysis['diagrams']):
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    diagram = analysis['diagrams'][diagram_index]
    xml_content = diagram['content'] if isinstance(diagram, dict) else diagram
    
    try:
        import subprocess
        import tempfile
        import base64
        from pathlib import Path
        
        # Create temp files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as xml_file:
            xml_file.write(xml_content)
            xml_path = xml_file.name
        
        png_path = xml_path.replace('.xml', '.png')
        
        # Use Draw.io desktop CLI to convert (if available)
        try:
            subprocess.run([
                'drawio', '--export', '--format', 'png', 
                '--output', png_path, xml_path
            ], check=True, capture_output=True)
            
            # Read and return PNG as base64
            png_data = Path(png_path).read_bytes()
            png_base64 = base64.b64encode(png_data).decode()
            
            # Cleanup
            Path(xml_path).unlink(missing_ok=True)
            Path(png_path).unlink(missing_ok=True)
            
            return Response(
                content=png_data,
                media_type="image/png",
                headers={"Content-Disposition": f"inline; filename=diagram_{diagram_index}.png"}
            )
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: generate enhanced SVG with connections
            from xml.dom import minidom
            
            dom = minidom.parseString(xml_content)
            cells = dom.getElementsByTagName('mxCell')
            
            components = []
            edges = []
            
            for cell in cells:
                cell_id = cell.getAttribute('id')
                if cell.hasAttribute('value') and cell.getAttribute('value').strip():
                    value = cell.getAttribute('value')
                    geometry = cell.getElementsByTagName('mxGeometry')
                    if geometry:
                        geom = geometry[0]
                        x = int(geom.getAttribute('x') or '0')
                        y = int(geom.getAttribute('y') or '0')
                        width = int(geom.getAttribute('width') or '120')
                        height = int(geom.getAttribute('height') or '60')
                        components.append({'id': cell_id, 'value': value, 'x': x, 'y': y, 'width': width, 'height': height})
                elif cell.hasAttribute('edge'):
                    source = cell.getAttribute('source')
                    target = cell.getAttribute('target')
                    if source and target:
                        edges.append({'source': source, 'target': target})
            
            if components:
                max_x = max(c['x'] + c['width'] for c in components)
                max_y = max(c['y'] + c['height'] for c in components)
                
                svg = f'<svg width="{max_x + 100}" height="{max_y + 100}" xmlns="http://www.w3.org/2000/svg">'
                svg += '<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#666"/></marker></defs>'
                
                # Draw connections first
                comp_map = {c['id']: c for c in components}
                for edge in edges:
                    if edge['source'] in comp_map and edge['target'] in comp_map:
                        src = comp_map[edge['source']]
                        tgt = comp_map[edge['target']]
                        x1 = src['x'] + src['width'] // 2
                        y1 = src['y'] + src['height']
                        x2 = tgt['x'] + tgt['width'] // 2
                        y2 = tgt['y']
                        svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>'
                
                # Draw components
                for comp in components:
                    # Add shadow
                    svg += f'<rect x="{comp["x"]+3}" y="{comp["y"]+3}" width="{comp["width"]}" height="{comp["height"]}" fill="rgba(0,0,0,0.1)" rx="8"/>'
                    # Main rectangle
                    svg += f'<rect x="{comp["x"]}" y="{comp["y"]}" width="{comp["width"]}" height="{comp["height"]}" fill="#dae8fc" stroke="#6c8ebf" stroke-width="2" rx="8"/>'
                    # Text
                    svg += f'<text x="{comp["x"] + comp["width"]//2}" y="{comp["y"] + comp["height"]//2}" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="12" font-weight="600" fill="#1f2937">{comp["value"]}</text>'
                
                svg += '</svg>'
                
                return Response(content=svg, media_type="image/svg+xml")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate diagram: {str(e)}")
    
    raise HTTPException(status_code=500, detail="Could not generate diagram")

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    # Validate project_id format to prevent path traversal
    if not project_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    
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

# Phase 3B Advanced AI Features Endpoints

@app.post("/api/projects/{project_id}/debug-analysis")
async def debug_analysis(project_id: str, request: dict):
    """Run AI debugging analysis on project errors."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    error_log = request.get("error_log", "")
    if not error_log:
        raise HTTPException(status_code=400, detail="Error log required")
    
    try:
        project = projects[project_id]
        project_path = project.get("project_path", "")
        
        analysis = debugging_assistant.debug_workflow(project_path, error_log)
        
        projects[project_id]["debugging_analysis"] = analysis
        data_store.save_projects(projects)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug analysis failed: {str(e)}")

@app.post("/api/projects/{project_id}/refactor-analysis")
async def refactor_analysis(project_id: str):
    """Run smart refactoring analysis on project code."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        project = projects[project_id]
        project_path = project.get("project_path", "")
        
        if not project_path:
            raise HTTPException(status_code=400, detail="No project path available")
        
        analysis = smart_refactoring.refactoring_workflow(project_path)
        
        projects[project_id]["refactoring_suggestions"] = analysis
        data_store.save_projects(projects)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refactoring analysis failed: {str(e)}")

@app.post("/api/projects/{project_id}/generate-documentation")
async def generate_project_documentation(project_id: str):
    """Generate intelligent documentation for project."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        project = projects[project_id]
        project_path = project.get("project_path", "")
        
        if not project_path:
            raise HTTPException(status_code=400, detail="No project path available")
        
        project_info = {
            "name": project.get("project_name", "Unknown"),
            "description": project.get("description", ""),
            "tech_stack": project.get("recommended_tech_stack", []),
            "features": project.get("features", [])
        }
        
        docs = intelligent_docs.documentation_workflow(project_path, project_info)
        
        projects[project_id]["documentation_quality"] = {
            "readme_generated": bool(docs["readme"]),
            "api_docs_count": len(docs["api_docs"]),
            "commented_files_count": len(docs["commented_files"]),
            "adrs_count": len(docs["adrs"])
        }
        
        data_store.save_projects(projects)
        
        return docs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Documentation generation failed: {str(e)}")

# Phase 4 Enterprise Features Endpoints

@app.get("/api/enterprise/projects")
async def get_enterprise_projects():
    """Get all projects with enterprise management features."""
    try:
        enterprise_projects = project_manager.list_projects()
        return {"projects": enterprise_projects, "workspace_stats": project_manager.get_workspace_stats()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enterprise projects: {str(e)}")

@app.post("/api/security/sast-scan")
async def run_sast_scan(request: dict):
    """Run Static Application Security Testing scan."""
    project_path = request.get("project_path", "")
    
    if not project_path:
        raise HTTPException(status_code=400, detail="Project path required")
    
    try:
        results = security_framework.sast_scan(project_path)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAST scan failed: {str(e)}")

@app.post("/api/collaboration/code-review")
async def create_code_review(request: dict):
    """Create new code review request."""
    try:
        result = collaboration_manager.create_code_review(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create code review: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)