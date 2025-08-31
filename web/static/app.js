class AgentAIInterface {
    constructor() {
        this.features = [];
        this.currentPage = 'dashboard';
        this.feedbackCache = {};
        this.init();
    }

    renderMarkdown(text) {
        if (typeof marked !== 'undefined') {
            return marked.parse(text);
        }
        // Fallback if marked.js is not loaded
        return text.replace(/\n/g, '<br>');
    }

    init() {
        this.loadDashboardStats();
        this.setupEventListeners();
        this.startDashboardRefresh();
    }

    startDashboardRefresh() {
        setInterval(() => {
            if (this.currentPage === 'dashboard') {
                this.loadDashboardStats();
            } else if (this.currentPage === 'workflows') {
                this.loadWorkflows();
            }
        }, 3000);
    }

    setupEventListeners() {
        const form = document.getElementById('project-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleProjectSubmit(e));
        }
        
        const featureInput = document.getElementById('feature-input');
        if (featureInput) {
            featureInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.addFeature();
                }
            });
        }
    }

    showPage(pageId) {
        // Update page visibility
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById(`${pageId}-page`).classList.add('active');
        
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
        
        this.currentPage = pageId;


        // Load page-specific data
        if (pageId === 'dashboard') {
            this.loadDashboardStats();
        } else if (pageId === 'workflows') {
            this.loadWorkflows();
        } else if (pageId === 'approvals') {
            this.loadAnalyses();
        } else if (pageId === 'projects') {
            this.loadProjects();
        } else if (pageId === 'new-project') {
            this.setFormDefaults();
        }
    }

    async loadDashboardStats() {
        try {
            const [projectsRes, workflowsRes, analysesRes] = await Promise.all([
                fetch('/api/projects'),
                fetch('/api/workflows'),
                fetch('/api/analyses')
            ]);
            
            const projects = await projectsRes.json();
            const workflows = await workflowsRes.json();
            const analyses = await analysesRes.json();
            
            this.populateKanbanBoard(projects, workflows, analyses);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }

    populateKanbanBoard(projects, workflows, analyses) {
        const columns = {
            requirements: [],
            analysis: [],
            development: [],
            testing: [],
            deployment: []
        };
        
        // Categorize projects by status
        projects.forEach(project => {
            const workflow = workflows.find(w => w.project_id === project.id);
            const analysis = analyses.find(a => a.project_id === project.id);
            
            // Determine status based on workflow and analysis
            let status = workflow?.status || 'analyzing';
            if (analysis) {
                if (analysis.status === 'pending' || analysis.status === 'rework') {
                    status = 'analysis_complete'; // Show in analysis column for approval
                } else if (analysis.status === 'approved') {
                    status = workflow?.status || 'development'; // Use workflow status after approval
                }
            }
            
            const currentPhase = workflow?.current_phase || 'Requirements Analysis';
            
            if (currentPhase === 'Requirements Analysis') {
                columns.requirements.push({...project, workflow, analysis});
            } else if (currentPhase === 'Human Approval') {
                columns.analysis.push({...project, workflow, analysis});
            } else if (currentPhase === 'Development') {
                columns.development.push({...project, workflow, analysis});
            } else if (currentPhase === 'Testing') {
                columns.testing.push({...project, workflow, analysis});
            } else if (currentPhase === 'Deployment' || workflow?.status === 'completed') {
                columns.deployment.push({...project, workflow, analysis});
            }
        });
        
        // Update column counts
        document.getElementById('requirements-count').textContent = columns.requirements.length;
        document.getElementById('analysis-count').textContent = columns.analysis.length;
        document.getElementById('development-count').textContent = columns.development.length;
        document.getElementById('testing-count').textContent = columns.testing.length;
        document.getElementById('deployment-count').textContent = columns.deployment.length;
        
        // Populate columns
        this.renderKanbanColumn('requirements-column', columns.requirements);
        this.renderKanbanColumn('analysis-column', columns.analysis);
        this.renderKanbanColumn('development-column', columns.development);
        this.renderKanbanColumn('testing-column', columns.testing);
        this.renderKanbanColumn('deployment-column', columns.deployment);
    }
    
    renderKanbanColumn(columnId, items) {
        const container = document.getElementById(columnId);
        
        let content = '';
        
        // Add + card for requirements column
        if (columnId === 'requirements-column') {
            content += `
                <div class="kanban-card add-card" onclick="app.showPage('new-project')">
                    <div class="add-icon">+</div>
                    <div class="add-text">Add New Project</div>
                </div>
            `;
        }
        
        if (items.length === 0 && columnId !== 'requirements-column') {
            container.innerHTML = '<div class="empty-state"><p>No items</p></div>';
            return;
        }
        
        content += items.map(item => `
            <div class="kanban-card" onclick="app.showProjectDetails('${item.id}')">
                <div class="card-id">${item.requirement_id || 'REQ-' + item.id.substring(0, 8).toUpperCase()}</div>
                <div class="card-title">${item.project_name}</div>
                <div class="card-description">${item.description.substring(0, 80)}...</div>
                <div class="card-meta">
                    <span class="card-status status-${item.analysis?.status || item.workflow?.status || 'analyzing'}">
                        ${item.analysis?.status || item.workflow?.status || 'analyzing'}
                    </span>
                    <span>${new Date(item.created_at).toLocaleDateString()}</span>
                </div>
                ${item.workflow?.status === 'completed' || item.status === 'completed' ? `
                    <div class="card-actions" onclick="event.stopPropagation();">
                        <button class="btn btn-small" onclick="app.viewCode('${item.id}')">View Code</button>
                    </div>
                ` : ''}
            </div>
        `).join('');
        
        container.innerHTML = content;
    }

    async loadWorkflows() {
        try {
            const response = await fetch('/api/workflows');
            const workflows = await response.json();
            
            const container = document.getElementById('workflows-list');
            if (workflows.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <h3>No active workflows</h3>
                        <p>Start a new project to create your first workflow</p>
                        <button class="btn btn-primary" onclick="app.showPage('new-project')">Create Project</button>
                    </div>
                `;
                return;
            }

            container.innerHTML = workflows.map(workflow => `
                <div class="workflow-card">
                    <div class="workflow-header">
                        <div class="workflow-title">${workflow.project_name}</div>
                        <div class="status-badge status-${(workflow.current_phase || 'Requirements Analysis').toLowerCase().replace(/ /g, '-')}">${workflow.current_phase || 'Requirements Analysis'}</div>
                    </div>
                    <div class="workflow-phases">
                        ${this.renderWorkflowPhases(workflow.current_phase || 'Requirements Analysis')}
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${workflow.progress || 10}%"></div>
                    </div>
                    <div class="timestamp">
                        Started: ${new Date(workflow.created_at).toLocaleDateString()} | 
                        Updated: ${new Date(workflow.updated_at || workflow.created_at).toLocaleDateString()}
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load workflows:', error);
        }
    }



    renderWorkflowPhases(currentPhase) {
        const phases = ['Requirements Analysis', 'Human Approval', 'Development', 'Testing', 'Deployment'];
        const currentIndex = phases.indexOf(currentPhase) >= 0 ? phases.indexOf(currentPhase) : 0;
        
        return phases.map((phase, index) => {
            let className = 'phase';
            if (index < currentIndex) className += ' completed';
            if (index === currentIndex) className += ' active';
            
            return `
                <div class="${className}">
                    <div class="phase-dot"></div>
                    <div>${phase}</div>
                </div>
            `;
        }).join('');
    }

    getRequirementId(projectId) {
        // Find project by ID and return its requirement_id
        const project = Object.values(this.projectsCache || {}).find(p => p.id === projectId);
        return project?.requirement_id || `REQ-${projectId?.substring(0, 8).toUpperCase()}`;
    }

    async loadAnalyses() {
        try {
            const response = await fetch('/api/analyses');
            const analyses = await response.json();
            
            // Cache projects for requirement ID lookup
            const projectsResponse = await fetch('/api/projects');
            const projects = await projectsResponse.json();
            this.projectsCache = projects.reduce((acc, p) => { acc[p.id] = p; return acc; }, {});
            
            const container = document.getElementById('analyses-list');
            if (analyses.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <h3>No pending approvals</h3>
                        <p>All analyses have been reviewed</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = analyses.map(analysis => `
                <div class="analysis-card" data-analysis="${analysis.id}">
                    <div class="analysis-id">ID: ${this.getRequirementId(analysis.project_id)}</div>
                    <div class="analysis-header">
                        <div class="analysis-title">${analysis.title || 'Analysis Report'}</div>
                        <div class="status-info">
                            <div class="status-badge status-${analysis.status}">${analysis.status === 'rework' ? 'rework' : analysis.status}</div>
                            ${analysis.status === 'rework' ? `
                                <div class="rework-progress">Awaiting rework completion</div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="timestamp">Submitted: ${new Date(analysis.timestamp).toLocaleString()}</div>
                    
                    ${analysis.recommended_tech_stack ? `
                        <div class="analysis-recommendation">
                            <h4>🤖 AI Recommended Technology Stack</h4>
                            <div class="tech-stack-list">
                                ${analysis.recommended_tech_stack.map(tech => `<span class="tech-tag">${tech}</span>`).join('')}
                            </div>
                            ${analysis.estimated_timeline ? `<p><strong>Estimated Timeline:</strong> ${analysis.estimated_timeline}</p>` : ''}
                        </div>
                    ` : ''}
                    
                    <div class="analysis-content markdown-content">${this.renderMarkdown(analysis.content)}</div>
                    
                    ${analysis.rework_history && analysis.rework_history.length > 0 ? `
                        <div class="rework-history">
                            <h4>📝 Rework History</h4>
                            ${analysis.rework_history.map(entry => `
                                <div class="rework-entry">
                                    <div class="rework-meta">
                                        <span class="rework-action">${entry.action}</span>
                                        <span class="rework-actor">by ${entry.actor || 'Unknown'}</span>
                                        <span class="rework-date">${new Date(entry.timestamp).toLocaleString()}</span>
                                    </div>
                                    ${entry.feedback ? `<div class="rework-feedback">${entry.feedback}</div>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${analysis.diagrams && analysis.diagrams.length > 0 ? `
                        <div class="diagram-container">
                            <h4>System Diagrams</h4>
                            ${analysis.diagrams.map((diagram, index) => `
                                <div class="diagram-viewer">
                                    <div class="diagram-header">
                                        <strong>Diagram ${index + 1}</strong>
                                        <button class="btn btn-small" onclick="app.viewDiagram('${encodeURIComponent(diagram)}')">View</button>
                                    </div>
                                    <div class="diagram-preview-text">
                                        <div id="diagram-render-${analysis.id}-${index}" class="diagram-visual"></div>
                                        <details style="margin-top: 10px;">
                                            <summary>View XML Source</summary>
                                            <pre style="background: #f8f9fa; padding: 12px; border-radius: 4px; font-size: 11px; max-height: 200px; overflow-y: auto;">${diagram}</pre>
                                        </details>
                                        <div style="margin-top: 8px; font-size: 12px; color: #6b7280;">Draw.io XML diagram (${diagram.length} characters)</div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${analysis.status === 'pending' || analysis.status === 'rework' ? `
                        <div class="approval-section">
                            <div class="approval-buttons">
                                <button class="btn btn-approve" onclick="app.approve('${analysis.id}', true)">
                                    ✅ Approve
                                </button>
                                <button class="btn btn-reject" onclick="app.approve('${analysis.id}', false)">
                                    ❌ Reject
                                </button>
                                <button class="btn btn-secondary" onclick="app.approve('${analysis.id}', 'rework')">
                                    🔄 Rework
                                </button>
                            </div>
                            <textarea 
                                id="feedback-${analysis.id}" 
                                class="feedback-input" 
                                placeholder="Optional feedback or requested changes..."
                                name="feedback-${analysis.id}"
                            ></textarea>
                        </div>
                    ` : ''}
                </div>
            `).join('');
            
            // Render diagrams after DOM is updated
            setTimeout(() => {
                analyses.forEach(analysis => {
                    if (analysis.diagrams && analysis.diagrams.length > 0) {
                        analysis.diagrams.forEach((diagram, index) => {
                            this.renderDiagramVisual(encodeURIComponent(diagram), `diagram-render-${analysis.id}-${index}`);
                        });
                    }
                });
            }, 100);
        } catch (error) {
            console.error('Failed to load analyses:', error);
        }
    }

    addFeature() {
        const input = document.getElementById('feature-input');
        const value = input.value.trim();
        
        if (value && !this.features.includes(value)) {
            this.features.push(value);
            input.value = '';
            this.renderFeatures();
        }
    }

    removeFeature(index) {
        this.features.splice(index, 1);
        this.renderFeatures();
    }

    renderFeatures() {
        const container = document.getElementById('features-list');
        container.innerHTML = this.features.map((feature, index) => `
            <div class="feature-item">
                <span>${feature}</span>
                <button onclick="app.removeFeature(${index})">Remove</button>
            </div>
        `).join('');
    }

    async handleProjectSubmit(e) {
        e.preventDefault();
        
        const projectData = {
            project_name: document.getElementById('project-name').value,
            description: document.getElementById('description').value,
            target_users: document.getElementById('target-users').value,
            scale: document.getElementById('scale').value,
            features: this.features,
            constraints: document.getElementById('constraints').value
        };

        if (!projectData.project_name || !projectData.description || !projectData.target_users || !projectData.scale) {
            alert('Please fill in all required fields marked with *');
            return;
        }

        if (this.features.length === 0) {
            alert('Please add at least one key feature');
            return;
        }

        try {
            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Analyzing Requirements...';
            
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projectData)
            });

            if (response.ok) {
                const result = await response.json();
                this.resetForm();
                this.showPage('dashboard');
                
                // Show success message
                setTimeout(() => {
                    alert('Requirements submitted! AI analysis will begin shortly.');
                }, 500);
            } else {
                alert('Failed to submit requirements');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Analyze Requirements';
            }
        } catch (error) {
            console.error('Failed to submit requirements:', error);
            alert('Failed to submit requirements');
            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Analyze Requirements';
        }
    }

    setFormDefaults() {
        document.getElementById('target-users').value = 'developers';
        document.getElementById('scale').value = 'small';
    }

    resetForm() {
        document.getElementById('project-form').reset();
        this.features = [];
        this.renderFeatures();
        this.setFormDefaults();
        const submitBtn = document.querySelector('#project-form button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Analyze Requirements';
        }
    }

    showProjectDetails(projectId) {
        // Find project and route to appropriate page
        Promise.all([
            fetch('/api/projects').then(res => res.json()),
            fetch('/api/workflows').then(res => res.json())
        ])
        .then(([projects, workflows]) => {
            const project = projects.find(p => p.id === projectId);
            const workflow = workflows.find(w => w.project_id === projectId);
            const status = workflow?.status || 'analyzing';
            
            if (status === 'analysis_complete') {
                this.showPage('approvals');
            } else if (status === 'running' || status === 'development') {
                this.showPage('workflows');
            } else {
                this.showPage('workflows');
            }
        })
        .catch(err => console.error('Failed to load project details:', err));
    }

    async approve(analysisId, action) {
        const feedbackElement = document.getElementById(`feedback-${analysisId}`);
        const feedback = feedbackElement ? feedbackElement.value : '';
        
        const approved = action === true;
        const rework = action === 'rework';

        try {
            const response = await fetch(`/api/approve/${analysisId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis_id: analysisId,
                    approved: approved,
                    rework: rework,
                    feedback: feedback
                })
            });

            if (response.ok) {
                this.showPage('dashboard');
                setTimeout(() => {
                    if (approved) {
                        alert('Architecture approved! Development phase will begin shortly.');
                    } else if (rework) {
                        alert('Analysis sent for rework.');
                    } else {
                        alert('Analysis rejected.');
                    }
                }, 100);
            } else {
                alert('Failed to submit response');
            }
        } catch (error) {
            console.error('Failed to submit response:', error);
            alert('Failed to submit response');
        }
    }

    async loadProjects() {
        try {
            const response = await fetch('/api/projects');
            const projects = await response.json();
            
            const container = document.getElementById('projects-list');
            if (projects.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <h3>No projects yet</h3>
                        <p>Create your first project to get started</p>
                        <button class="btn btn-primary" onclick="app.showPage('new-project')">Create Project</button>
                    </div>
                `;
                return;
            }

            container.innerHTML = projects.map(project => `
                <div class="project-card">
                    <div class="project-header">
                        <div class="project-id">${project.requirement_id || 'REQ-' + project.id.substring(0, 8).toUpperCase()}</div>
                        <div class="project-actions">
                            <button class="btn btn-small" onclick="app.viewProjectDetails('${project.id}')">View Details</button>
                            <button class="btn btn-small btn-danger" onclick="app.deleteProject('${project.id}')">Delete</button>
                        </div>
                    </div>
                    <div class="project-title">${project.project_name}</div>
                    <div class="project-description">${project.description}</div>
                    <div class="project-meta">
                        <div class="status-badge status-${project.status}">${project.status}</div>
                        <div class="project-date">Created: ${new Date(project.created_at).toLocaleDateString()}</div>
                    </div>
                    ${project.project_path ? `
                        <div class="project-path">📁 ${project.project_path}</div>
                    ` : ''}
                    ${project.test_iterations ? `
                        <div class="project-stats">
                            <span>🔄 ${project.test_iterations} test iterations</span>
                            <span>🐛 ${project.total_issues_fixed || 0} issues fixed</span>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    }

    async viewProjectDetails(projectId) {
        try {
            const response = await fetch(`/api/projects/${projectId}`);
            const project = await response.json();
            
            if (response.ok) {
                const modal = document.createElement('div');
                modal.className = 'project-modal';
                modal.style.cssText = `
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                    background: rgba(0,0,0,0.8); z-index: 1000; display: flex; 
                    align-items: center; justify-content: center;
                `;
                modal.innerHTML = `
                    <div class="modal-container">
                        <div class="modal-header">
                            <div class="modal-title">
                                <h2>${project.project_name}</h2>
                                <span class="project-id-badge">${project.requirement_id}</span>
                                <span class="status-badge status-${project.status}">${project.status}</span>
                            </div>
                            <button onclick="this.closest('.project-modal').remove()" class="modal-close">&times;</button>
                        </div>
                        
                        <div class="modal-tabs">
                            <button class="tab-btn active" onclick="app.switchTab(event, 'overview')">📋 Overview</button>
                            <button class="tab-btn" onclick="app.switchTab(event, 'analysis')">🔍 Analysis</button>
                            <button class="tab-btn" onclick="app.switchTab(event, 'code')">💻 Code</button>
                            <button class="tab-btn" onclick="app.switchTab(event, 'tests')">🧪 Tests</button>
                            <button class="tab-btn" onclick="app.switchTab(event, 'docs')">📚 Docs</button>
                            <button class="tab-btn" onclick="app.switchTab(event, 'diagrams')">📏 Diagrams</button>
                            <button class="tab-btn" onclick="app.switchTab(event, 'issues')">🐛 Issues</button>
                        </div>
                        
                        <div class="modal-content">
                            <div id="overview" class="tab-content active">
                                <div class="info-grid">
                                    <div class="info-card">
                                        <h3>📋 Project Details</h3>
                                        <div class="info-item"><strong>Created:</strong> ${new Date(project.created_at).toLocaleDateString()}</div>
                                        <div class="info-item"><strong>Target Users:</strong> ${project.target_users}</div>
                                        <div class="info-item"><strong>Scale:</strong> ${project.scale}</div>
                                        <div class="info-item"><strong>Description:</strong> ${project.description}</div>
                                        ${project.constraints ? `<div class="info-item"><strong>Constraints:</strong> ${project.constraints}</div>` : ''}
                                    </div>
                                    
                                    <div class="info-card">
                                        <h3>📊 Statistics</h3>
                                        ${project.test_iterations ? `<div class="stat-item"><span class="stat-number">${project.test_iterations}</span><span class="stat-label">Test Iterations</span></div>` : ''}
                                        ${project.total_issues_fixed ? `<div class="stat-item"><span class="stat-number">${project.total_issues_fixed}</span><span class="stat-label">Issues Fixed</span></div>` : ''}
                                        ${project.folder_summary ? `<div class="stat-item"><span class="stat-number">${project.folder_summary.total_files}</span><span class="stat-label">Total Files</span></div>` : ''}
                                    </div>
                                </div>
                                
                                ${project.features && project.features.length > 0 ? `
                                    <div class="info-card">
                                        <h3>✨ Features</h3>
                                        <div class="features-list">${project.features.map(f => `<span class="feature-tag">${f}</span>`).join('')}</div>
                                    </div>
                                ` : ''}
                                
                                ${project.project_path ? `
                                    <div class="info-card">
                                        <h3>📁 Project Location</h3>
                                        <div class="project-path-display">${project.project_path}</div>
                                    </div>
                                ` : ''}
                            </div>
                            
                            <div id="analysis" class="tab-content">
                                <div class="artifact-content">
                                    ${project.analysis ? `<div class="markdown-content">${this.renderMarkdown(project.analysis)}</div>` : '<div class="empty-artifact">No analysis available</div>'}
                                </div>
                            </div>
                            
                            <div id="code" class="tab-content">
                                <div class="artifact-content">
                                    ${project.generated_code || project.final_code ? `<pre class="code-block"><code>${project.final_code || project.generated_code}</code></pre>` : '<div class="empty-artifact">No code generated yet</div>'}
                                </div>
                            </div>
                            
                            <div id="tests" class="tab-content">
                                <div class="artifact-content">
                                    ${project.generated_tests ? `<pre class="code-block"><code>${project.generated_tests}</code></pre>` : '<div class="empty-artifact">No tests generated yet</div>'}
                                </div>
                            </div>
                            
                            <div id="docs" class="tab-content">
                                <div class="artifact-content">
                                    ${project.generated_docs ? `<div class="markdown-content">${this.renderMarkdown(project.generated_docs)}</div>` : '<div class="empty-artifact">No documentation generated yet</div>'}
                                </div>
                            </div>
                            
                            <div id="diagrams" class="tab-content">
                                <div class="artifact-content">
                                    ${this.renderDiagrams(project)}
                                </div>
                            </div>
                            
                            <div id="issues" class="tab-content">
                                <div class="artifact-content">
                                    ${project.issues_log && project.issues_log.length > 0 ? `
                                        <div class="issues-timeline">
                                            ${project.issues_log.map(log => `
                                                <div class="issue-iteration">
                                                    <div class="iteration-header">
                                                        <h4>Iteration ${log.iteration}</h4>
                                                        <span class="iteration-date">${new Date(log.timestamp).toLocaleString()}</span>
                                                    </div>
                                                    <div class="issues-list">
                                                        ${log.issues_found.map(issue => `
                                                            <div class="issue-item">
                                                                <span class="severity-badge severity-${issue.severity.toLowerCase()}">${issue.severity}</span>
                                                                <span class="issue-description">${issue.description}</span>
                                                            </div>
                                                        `).join('')}
                                                    </div>
                                                </div>
                                            `).join('')}
                                        </div>
                                    ` : '<div class="empty-artifact">No issues logged</div>'}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
            } else {
                alert('Failed to load project details');
            }
        } catch (error) {
            alert(`Error loading project: ${error.message}`);
        }
    }

    renderDiagrams(project) {
        // Check for diagrams in analysis or separate diagrams field
        let diagrams = [];
        
        // Extract from analysis if available
        if (project.analysis) {
            const xmlMatches = project.analysis.match(/```xml\s*(<mxfile[^>]*>.*?<\/mxfile>)\s*```/gs);
            if (xmlMatches) {
                diagrams = xmlMatches.map(match => match.replace(/```xml\s*|\s*```/g, ''));
            }
        }
        
        // Also check diagrams field if available
        if (project.diagrams && project.diagrams.length > 0) {
            diagrams = diagrams.concat(project.diagrams);
        }
        
        if (diagrams.length === 0) {
            return '<div class="empty-artifact">No diagrams generated yet</div>';
        }
        
        return `
            <div class="diagrams-container">
                ${diagrams.map((diagram, index) => `
                    <div class="diagram-item">
                        <div class="diagram-header">
                            <h4>System Diagram ${index + 1}</h4>
                            <button class="btn btn-small" onclick="app.viewDiagram('${encodeURIComponent(diagram)}')">View Full Size</button>
                        </div>
                        <div class="diagram-preview">
                            <div id="diagram-render-${index}" class="diagram-visual"></div>
                            <div class="diagram-xml-display" style="margin-top: 10px;">
                                <details>
                                    <summary>View XML Source</summary>
                                    <pre class="xml-content">${diagram}</pre>
                                </details>
                                <div class="diagram-actions">
                                    <button class="btn btn-small" onclick="app.copyDiagram('${encodeURIComponent(diagram)}')">Copy XML</button>
                                    <button class="btn btn-small" onclick="app.openInDrawio('${encodeURIComponent(diagram)}')">Open in Draw.io</button>
                                </div>
                            </div>
                        </div>
                        <script>app.renderDiagramVisual('${encodeURIComponent(diagram)}', 'diagram-render-${index}');</script>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    copyDiagram(encodedDiagram) {
        const diagram = decodeURIComponent(encodedDiagram);
        navigator.clipboard.writeText(diagram).then(() => {
            alert('Diagram XML copied to clipboard!');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = diagram;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            alert('Diagram XML copied to clipboard!');
        });
    }
    
    openInDrawio(encodedDiagram) {
        const diagram = decodeURIComponent(encodedDiagram);
        this.copyDiagram(encodedDiagram);
        window.open('https://app.diagrams.net/', '_blank');
        alert('XML copied to clipboard! In Draw.io: File → Import from → Device, then paste the XML.');
    }
    
    renderDiagramVisual(encodedDiagram, containerId) {
        const diagram = decodeURIComponent(encodedDiagram);
        const container = document.getElementById(containerId);
        
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }
        
        try {
            // Extract component names from the XML
            const components = [];
            
            // Method 1: Look for value attributes
            const valueMatches = diagram.match(/value="([^"]+)"/g);
            if (valueMatches) {
                valueMatches.forEach(match => {
                    const component = match.replace(/value="([^"]+)"/, '$1');
                    if (component && component.trim() && !component.includes('geometry')) {
                        components.push(component.trim());
                    }
                });
            }
            
            // Method 2: Look for common component patterns
            const patterns = [
                /Python Script/g, /Web Scraping Module/g, /Data Storage/g, /Presentation Layer/g,
                /User Interface/g, /Business Logic/g, /API Gateway/g, /Database/g,
                /Frontend/g, /Backend/g, /Service/g, /Component/g
            ];
            
            patterns.forEach(pattern => {
                const matches = diagram.match(pattern);
                if (matches) {
                    matches.forEach(match => components.push(match));
                }
            });
            
            // Remove duplicates
            const uniqueComponents = [...new Set(components)].filter(c => c.length > 0);
            
            if (uniqueComponents.length === 0) {
                container.innerHTML = `
                    <div style="padding: 20px; text-align: center; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                        <p>📊 Draw.io XML detected (${diagram.length} chars)</p>
                        <p style="color: #6c757d; font-size: 14px;">No visual components found - use "Open in Draw.io" to view</p>
                    </div>
                `;
                return;
            }
            
            // Render visual components
            let diagramHtml = '<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; padding: 20px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">';
            
            uniqueComponents.forEach((component, index) => {
                const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];
                const color = colors[index % colors.length];
                
                diagramHtml += `
                    <div style="
                        padding: 12px 20px;
                        background: linear-gradient(135deg, ${color} 0%, ${color}aa 100%);
                        color: white;
                        border-radius: 8px;
                        font-weight: bold;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        text-align: center;
                        min-width: 120px;
                        font-size: 14px;
                    ">
                        ${component}
                    </div>
                `;
            });
            
            diagramHtml += '</div>';
            diagramHtml += `<div style="margin-top: 10px; text-align: center; font-size: 12px; color: #6c757d;">Found ${uniqueComponents.length} components</div>`;
            
            container.innerHTML = diagramHtml;
            
        } catch (error) {
            console.error('Error rendering diagram:', error);
            container.innerHTML = `
                <div style="padding: 20px; text-align: center; background: #fff3cd; border-radius: 8px; border: 1px solid #ffeaa7;">
                    <p>⚠️ Error parsing diagram</p>
                    <p style="font-size: 12px; color: #856404;">Use "Open in Draw.io" to view the diagram</p>
                </div>
            `;
        }
    }
    
    viewDiagram(encodedDiagram) {
        const diagram = decodeURIComponent(encodedDiagram);
        const modal = document.createElement('div');
        modal.className = 'diagram-modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.8); z-index: 1000; display: flex; 
            align-items: center; justify-content: center;
        `;
        modal.innerHTML = `
            <div style="background: white; width: 90%; height: 90%; border-radius: 8px; overflow: hidden;">
                <div style="padding: 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                    <h3>Draw.io XML Diagram</h3>
                    <button onclick="this.closest('.diagram-modal').remove()" style="background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
                </div>
                <div style="padding: 20px; height: calc(100% - 80px); overflow-y: auto;">
                    <div style="margin-bottom: 16px;">
                        <button class="btn btn-primary" onclick="app.copyDiagram('${encodeURIComponent(diagram)}')">Copy XML</button>
                        <button class="btn btn-secondary" onclick="app.openInDrawio('${encodeURIComponent(diagram)}')">Open in Draw.io</button>
                    </div>
                    <pre style="background: #f8f9fa; padding: 16px; border-radius: 4px; font-size: 12px; line-height: 1.4; white-space: pre-wrap;">${diagram}</pre>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    switchTab(event, tabName) {
        // Remove active class from all tabs and content
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding content
        event.target.classList.add('active');
        document.getElementById(tabName).classList.add('active');
    }

    async deleteProject(projectId) {
        if (!confirm('Are you sure you want to delete this project? This will remove all files and cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert('Project deleted successfully');
                this.loadProjects(); // Refresh the list
            } else {
                const error = await response.json();
                alert(`Failed to delete project: ${error.detail}`);
            }
        } catch (error) {
            alert(`Error deleting project: ${error.message}`);
        }
    }

    async viewCode(projectId) {
        try {
            const response = await fetch(`/api/projects/${projectId}/code`);
            const data = await response.json();
            
            if (response.ok) {
                const modal = document.createElement('div');
                modal.className = 'code-modal';
                modal.style.cssText = `
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                    background: rgba(0,0,0,0.8); z-index: 1000; display: flex; 
                    align-items: center; justify-content: center;
                `;
                modal.innerHTML = `
                    <div style="background: white; width: 90%; height: 90%; border-radius: 8px; overflow: hidden;">
                        <div style="padding: 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                            <h2>Generated Project - ${data.project_name}</h2>
                            <button onclick="this.closest('.code-modal').remove()" style="background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
                        </div>
                        <div style="padding: 20px; height: calc(100% - 80px); overflow-y: auto;">
                            ${data.project_path ? `
                                <div style="background: #f0f8ff; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
                                    <strong>📁 Project Folder:</strong> ${data.project_path}
                                </div>
                            ` : ''}
                            ${data.folder_summary && data.folder_summary.total_files > 0 ? `
                                <h3>📂 Project Structure:</h3>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 15px;">
                                    ${data.folder_summary.analysis_files.length > 0 ? `<div><strong>Analysis:</strong> ${data.folder_summary.analysis_files.length} files</div>` : ''}
                                    ${data.folder_summary.code_files.length > 0 ? `<div><strong>Code:</strong> ${data.folder_summary.code_files.length} files</div>` : ''}
                                    ${data.folder_summary.test_files.length > 0 ? `<div><strong>Tests:</strong> ${data.folder_summary.test_files.length} files</div>` : ''}
                                    ${data.folder_summary.doc_files.length > 0 ? `<div><strong>Docs:</strong> ${data.folder_summary.doc_files.length} files</div>` : ''}
                                </div>
                            ` : ''}
                            ${data.saved_files && data.saved_files.length > 0 ? `
                                <h3>💾 Saved Files:</h3>
                                <ul>${data.saved_files.map(file => `<li>${file}</li>`).join('')}</ul>
                            ` : ''}
                            <h3>📄 Generated Code:</h3>
                            <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto; max-height: 400px;"><code>${data.generated_code}</code></pre>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
            } else {
                alert('Failed to load generated code');
            }
        } catch (error) {
            alert(`Error loading code: ${error.message}`);
        }
    }
}

// Global functions for onclick handlers
function showPage(pageId) {
    app.showPage(pageId);
}

function addFeature() {
    app.addFeature();
}

function showProjectDetails(projectId) {
    app.showProjectDetails(projectId);
}

// Initialize the app
const app = new AgentAIInterface();