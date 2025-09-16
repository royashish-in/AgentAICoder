class AgentAIInterface {
    constructor() {
        this.features = [];
        this.currentPage = 'dashboard';
        this.feedbackCache = {};
        this.init();
    }

    renderMarkdown(text) {
        if (typeof marked !== 'undefined') {
            return marked.parse(this.escapeHtml(text));
        }
        // Fallback if marked.js is not loaded
        return this.escapeHtml(text).replace(/\n/g, '<br>');
    }

    init() {
        this.loadDashboardStats();
        this.setupEventListeners();
        this.startDashboardRefresh();
        this.selectedStories = [];
        this.requirementSource = null;
        this.allStories = [];
        this.currentPage = 1;
        this.pageSize = 10;
        this.searchTerm = '';
        // Initialize Lucide icons after DOM updates
        setTimeout(() => lucide.createIcons(), 100);
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
        
        // Requirement source switching
        document.querySelectorAll('input[name="requirement-source"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.switchRequirementSource(e.target.value));
        });
        
        // Load stories button
        const loadBtn = document.getElementById('load-stories-btn');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadJiraStories());
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
        } else if (pageId === 'metrics') {
            this.loadMetrics();
        } else if (pageId === 'chat') {
            this.initChat();
        } else if (pageId === 'new-project') {
            this.showRequirementModal();
            return;
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
                <div class="kanban-card add-card" onclick="showPage('new-project')">
                    <i data-lucide="plus" class="add-icon"></i>
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
        
        container.innerHTML = this.sanitizeHtml(content);
        
        // Re-initialize Lucide icons for new content
        setTimeout(() => lucide.createIcons(), 50);
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
                        <button class="btn btn-primary" onclick="showPage('new-project')">
                            <i data-lucide="plus"></i>
                            Create Project
                        </button>
                    </div>
                `;
                return;
            }

            const workflowsHtml = workflows.map(workflow => `
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
            
            container.innerHTML = this.sanitizeHtml(workflowsHtml);
            
            // Re-initialize Lucide icons
            setTimeout(() => lucide.createIcons(), 50);
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
            this.analysisCache = analyses.reduce((acc, a) => { acc[a.id] = a; return acc; }, {});
            
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

            const analysesHtml = analyses.map(analysis => `
                <div class="modern-analysis-card" data-analysis="${analysis.id}">
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
                    
                    <div class="modern-approval-container">
                        <div class="approval-tabs">
                            <button class="tab-btn active" onclick="app.switchApprovalTab(event, 'review-${analysis.id}')">📋 Review</button>
                            <button class="tab-btn" onclick="app.switchApprovalTab(event, 'tests-${analysis.id}')">🧪 Tests</button>
                            ${analysis.diagrams && analysis.diagrams.length > 0 ? `<button class="tab-btn" onclick="app.switchApprovalTab(event, 'diagrams-${analysis.id}')">📊 Diagrams</button>` : ''}
                            <button class="tab-btn" onclick="app.switchApprovalTab(event, 'chat-${analysis.id}')">💬 Ask AI</button>
                            <button class="tab-btn" onclick="app.switchApprovalTab(event, 'decision-${analysis.id}')">✅ Decision</button>
                        </div>
                        
                        <div id="review-${analysis.id}" class="approval-tab-content active">
                            <div class="clean-analysis-view">
                                <div class="analysis-summary">
                                    <div class="markdown-content">${this.renderMarkdown(analysis.content.substring(0, 500) + '...')}</div>
                                    <button class="btn btn-link" onclick="app.expandAnalysis('${analysis.id}')">Read Full Analysis</button>
                                </div>
                            </div>
                        </div>
                        
                        <div id="tests-${analysis.id}" class="approval-tab-content">
                            <div class="test-plan-section">
                                <h4>🧪 Test Strategy</h4>
                                ${analysis.test_plan ? `
                                    <div class="test-content">
                                        <div class="markdown-content">${this.renderMarkdown(analysis.test_plan)}</div>
                                    </div>
                                ` : '<p class="no-tests">No test plan available for this analysis.</p>'}
                            </div>
                        </div>
                        
                        <div id="chat-${analysis.id}" class="approval-tab-content">
                            <div class="architect-chat">
                                <div class="chat-header">
                                    <h4>🤖 Ask the AI Architect</h4>
                                    <p>Get clarifications about this analysis</p>
                                </div>
                                <div id="chat-messages-${analysis.id}" class="mini-chat-messages"></div>
                                <div class="mini-chat-input">
                                    <input type="text" id="chat-input-${analysis.id}" placeholder="Ask about the architecture, tech choices, timeline..." onkeypress="if(event.key==='Enter') app.sendAnalysisChat('${analysis.id}')">
                                    <button onclick="app.sendAnalysisChat('${analysis.id}')" class="btn btn-primary btn-small">Send</button>
                                </div>
                            </div>
                        </div>
                        
                        <div id="decision-${analysis.id}" class="approval-tab-content">
                            <div class="decision-panel">
                                <h4>Make Your Decision</h4>
                                <div class="decision-buttons">
                                    <button class="btn btn-success" onclick="app.approve('${analysis.id}', true)">
                                        ✅ Approve & Proceed
                                    </button>
                                    <button class="btn btn-warning" onclick="app.approve('${analysis.id}', 'rework')">
                                        🔄 Request Changes
                                    </button>
                                    <button class="btn btn-danger" onclick="app.approve('${analysis.id}', false)">
                                        ❌ Reject
                                    </button>
                                </div>
                                <textarea 
                                    id="feedback-${analysis.id}" 
                                    class="modern-feedback" 
                                    placeholder="Optional feedback or specific changes needed..."
                                ></textarea>
                            </div>
                        </div>
                    </div>
                    
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
                            <div id="diagrams-${analysis.id}" class="approval-tab-content">
                                <div class="diagrams-section">
                                    <h4>📊 System Diagrams</h4>
                                    ${analysis.diagrams.map((diagram, index) => {
                                        const diagramContent = typeof diagram === 'string' ? diagram : diagram.content;
                                        const diagramName = typeof diagram === 'object' ? diagram.name : `Diagram ${index + 1}`;
                                        return `
                                        <div class="diagram-item">
                                            <div class="diagram-header">
                                                <strong>${diagramName}</strong>
                                            </div>
                                            <img src="/api/diagram-png/${analysis.id}/${index}" alt="${diagramName}" style="max-width: 100%; height: auto; border: 1px solid #e5e7eb; border-radius: 4px; margin-top: 8px;" onerror="this.style.display='none'"/>
                                            </div>
                                            <div id="diagram-render-${analysis.id}-${index}" class="diagram-visual"></div>
                                        </div>
                                    `}).join('')}
                                </div>
                            </div>
                        ` : ''}
                </div>
            `).join('');
            
            container.innerHTML = this.sanitizeHtml(analysesHtml);

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
                <span>${this.escapeHtml(feature)}</span>
                <button onclick="app.removeFeature(${index})">Remove</button>
            </div>
        `).join('');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    sanitizeHtml(html) {
        const div = document.createElement('div');
        div.innerHTML = html;
        
        // Remove script tags and event handlers
        const scripts = div.querySelectorAll('script');
        scripts.forEach(script => script.remove());
        
        const elements = div.querySelectorAll('*');
        elements.forEach(el => {
            // Remove event handler attributes
            Array.from(el.attributes).forEach(attr => {
                if (attr.name.startsWith('on')) {
                    el.removeAttribute(attr.name);
                }
            });
        });
        
        return div.innerHTML;
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 10000;
            padding: 12px 20px; border-radius: 6px; color: white;
            font-weight: 500; max-width: 400px; word-wrap: break-word;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    showConfirm(message) {
        return confirm(message); // Temporary - should be replaced with custom modal
    }

    async handleProjectSubmit(e) {
        e.preventDefault();
        
        const projectData = {
            project_name: document.getElementById('project-name').value,
            description: document.getElementById('description')?.value || '',
            target_users: document.getElementById('target-users')?.value || '',
            scale: document.getElementById('scale')?.value || '',
            features: this.features,
            constraints: document.getElementById('constraints')?.value || '',
            user_story_keys: this.selectedStories || []
        };

        const source = this.requirementSource;
        
        if (!projectData.project_name) {
            this.showNotification('Please enter a project name', 'warning');
            return;
        }
        
        if (source === 'jira') {
            if (this.selectedStories.length === 0) {
                this.showNotification('Please select at least one JIRA user story', 'warning');
                return;
            }
            // Override with JIRA-specific data - ignore manual fields completely
            projectData.user_story_keys = this.selectedStories;
            projectData.description = `Project based on ${this.selectedStories.length} JIRA user stories`;
            projectData.target_users = 'business-users';
            projectData.scale = this.selectedStories.length <= 3 ? 'small' : this.selectedStories.length <= 10 ? 'medium' : 'large';
            projectData.features = []; // Will be populated from JIRA stories on backend
            projectData.constraints = '';
        } else {
            // Manual mode validation
            if (!projectData.target_users || !projectData.scale) {
                this.showNotification('Please fill in all required fields', 'warning');
                return;
            }
            if (!projectData.description || this.features.length === 0) {
                this.showNotification('Please add description and at least one feature for manual mode', 'warning');
                return;
            }
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
                    this.showNotification('Requirements submitted! AI analysis will begin shortly.', 'success');
                }, 500);
            } else {
                this.showNotification('Failed to submit requirements', 'error');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Analyze Requirements';
            }
        } catch (error) {
            console.error('Failed to submit requirements:', error);
            this.showNotification('Failed to submit requirements', 'error');
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
                        this.showNotification('Architecture approved! Development phase will begin shortly.', 'success');
                    } else if (rework) {
                        this.showNotification('Analysis sent for rework.', 'info');
                    } else {
                        this.showNotification('Analysis rejected.', 'warning');
                    }
                }, 100);
            } else {
                this.showNotification('Failed to submit response', 'error');
            }
        } catch (error) {
            console.error('Failed to submit response:', error);
            this.showNotification('Failed to submit response', 'error');
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
                        <button class="btn btn-primary" onclick="showPage('new-project')">
                            <i data-lucide="plus"></i>
                            Create Project
                        </button>
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
                this.showNotification('Failed to load project details', 'error');
            }
        } catch (error) {
            this.showNotification(`Error loading project: ${error.message}`, 'error');
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
            // Handle both string and object formats
            const processedDiagrams = project.diagrams.map(diagram => {
                if (typeof diagram === 'string') {
                    return { content: diagram, name: 'System Diagram' };
                } else {
                    return diagram;
                }
            });
            diagrams = diagrams.concat(processedDiagrams.map(d => d.content));
        }
        
        if (diagrams.length === 0) {
            return '<div class="empty-artifact">No diagrams generated yet</div>';
        }
        
        return `
            <div class="diagrams-container">
                ${diagrams.map((diagram, index) => {
                    const diagramContent = typeof diagram === 'string' ? diagram : diagram.content || diagram;
                    const diagramName = typeof diagram === 'object' ? diagram.name : `System Diagram ${index + 1}`;
                    return `
                    <div class="diagram-item">
                        <div class="diagram-header">
                            <h4>${diagramName}</h4>
                            <button class="btn btn-small" onclick="app.viewDiagram('${encodeURIComponent(diagramContent)}')">View Full Size</button>
                        </div>
                        <div class="diagram-preview">
                            <div id="diagram-render-${index}" class="diagram-visual"></div>
                            <div class="diagram-xml-display" style="margin-top: 10px;">
                                <details>
                                    <summary>View XML Source</summary>
                                    <pre class="xml-content">${diagramContent}</pre>
                                </details>
                                <div class="diagram-actions">
                                    <button class="btn btn-small" onclick="app.copyDiagram('${encodeURIComponent(diagramContent)}')">Copy XML</button>
                                    <button class="btn btn-small" onclick="app.openInDrawio('${encodeURIComponent(diagramContent)}')">Open in Draw.io</button>
                                </div>
                            </div>
                        </div>
                        <div data-diagram="${encodeURIComponent(diagramContent)}" data-container="diagram-render-${index}" class="diagram-script"></div>
                    </div>
                `}).join('')}
            </div>
        `;
    }
    
    copyDiagram(encodedDiagram) {
        const diagram = decodeURIComponent(encodedDiagram);
        navigator.clipboard.writeText(diagram).then(() => {
            this.showNotification('Diagram XML copied to clipboard!', 'success');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = diagram;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showNotification('Diagram XML copied to clipboard!', 'success');
        });
    }
    

    
    renderDiagramVisual(encodedDiagram, containerId) {
        const diagram = decodeURIComponent(encodedDiagram);
        const container = document.getElementById(containerId);
        
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }
        
        try {
            // Parse the actual diagram XML to extract components
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(diagram, 'text/xml');
            
            // Check for parsing errors
            const parseError = xmlDoc.querySelector('parsererror');
            if (parseError) {
                throw new Error('XML parsing failed');
            }
            
            const cells = xmlDoc.querySelectorAll('mxCell[value]');
            
            if (cells.length > 0) {
                // Render actual diagram components
                const components = [];
                
                cells.forEach(cell => {
                    const value = cell.getAttribute('value');
                    const style = cell.getAttribute('style') || '';
                    const geometry = cell.querySelector('mxGeometry');
                    
                    if (value && value.trim() && geometry) {
                        const x = parseInt(geometry.getAttribute('x') || '0');
                        const y = parseInt(geometry.getAttribute('y') || '0');
                        const width = parseInt(geometry.getAttribute('width') || '120');
                        const height = parseInt(geometry.getAttribute('height') || '60');
                        
                        // Extract colors from style
                        const fillColor = this.extractStyleValue(style, 'fillColor') || '#dae8fc';
                        const strokeColor = this.extractStyleValue(style, 'strokeColor') || '#6c8ebf';
                        
                        components.push({ value, x, y, width, height, fillColor, strokeColor });
                    }
                });
                
                if (components.length > 0) {
                    // Calculate container dimensions
                    const maxX = Math.max(...components.map(c => c.x + c.width));
                    const maxY = Math.max(...components.map(c => c.y + c.height));
                    const containerWidth = Math.max(400, maxX + 50);
                    const containerHeight = Math.max(200, maxY + 50);
                    
                    // Create SVG representation
                    let svgContent = `<svg width="${containerWidth}" height="${containerHeight}" viewBox="0 0 ${containerWidth} ${containerHeight}" style="background: #fafbfc; border-radius: 8px;">`;
                    
                    components.forEach(comp => {
                        svgContent += `
                            <rect x="${comp.x}" y="${comp.y}" width="${comp.width}" height="${comp.height}" 
                                  fill="${comp.fillColor}" stroke="${comp.strokeColor}" stroke-width="2" 
                                  rx="8" ry="8" style="filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));"/>
                            <text x="${comp.x + comp.width/2}" y="${comp.y + comp.height/2}" 
                                  text-anchor="middle" dominant-baseline="middle" 
                                  font-family="Arial, sans-serif" font-size="12" font-weight="600" 
                                  fill="#1f2937">${this.escapeHtml(comp.value)}</text>`;
                    });
                    
                    svgContent += '</svg>';
                    
                    container.innerHTML = `
                        <div style="display: flex; flex-direction: column; align-items: center; padding: 16px; background: #fafbfc; border-radius: 8px;">
                            ${svgContent}

                        </div>
                    `;
                    return;
                }
            }
        } catch (error) {
            console.error('Failed to parse diagram XML:', error);
        }
        
        // Fallback to placeholder if parsing fails
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 180px; background: #f8fafc; border-radius: 8px; padding: 24px; text-align: center;">
                <div style="width: 48px; height: 48px; background: #e2e8f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
                    📊
                </div>
                <p style="color: #6b7280; margin: 0 0 16px 0; font-size: 14px;">Diagram Available</p>

            </div>
        `;
    }
    
    extractStyleValue(style, property) {
        const regex = new RegExp(`${property}=([^;]+)`);
        const match = style.match(regex);
        return match ? match[1] : null;
    }
    
    viewDiagram(encodedDiagram) {
        const diagram = decodeURIComponent(encodedDiagram);
        const modal = document.createElement('div');
        modal.className = 'diagram-modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.5); z-index: 1000; display: flex; 
            align-items: center; justify-content: center; padding: 20px;
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

    switchRequirementSource(source) {
        const jiraMode = document.getElementById('jira-mode');
        const manualMode = document.getElementById('manual-mode');
        const jiraModeNote = document.getElementById('jira-mode-note');
        const manualFields = document.querySelectorAll('.manual-only');
        const featuresSection = document.getElementById('features-section');
        const descriptionField = document.getElementById('description');
        const targetUsersField = document.getElementById('target-users');
        const scaleField = document.getElementById('scale');
        
        if (source === 'jira') {
            jiraMode.style.display = 'block';
            manualMode.style.display = 'none';
            jiraModeNote.style.display = 'block';
            manualFields.forEach(field => field.style.display = 'none');
            if (featuresSection) featuresSection.style.display = 'none';
            
            // Remove required attributes for hidden fields
            if (descriptionField) descriptionField.removeAttribute('required');
            if (targetUsersField) targetUsersField.removeAttribute('required');
            if (scaleField) scaleField.removeAttribute('required');
            
            this.loadJiraStories();
        } else {
            jiraMode.style.display = 'none';
            manualMode.style.display = 'block';
            jiraModeNote.style.display = 'none';
            manualFields.forEach(field => field.style.display = 'block');
            if (featuresSection) featuresSection.style.display = 'block';
            
            // Restore required attributes for visible fields
            if (descriptionField) descriptionField.setAttribute('required', '');
            if (targetUsersField) targetUsersField.setAttribute('required', '');
            if (scaleField) scaleField.setAttribute('required', '');
        }
    }
    
    async loadJiraStories() {
        const loadBtn = document.getElementById('load-stories-btn');
        const container = document.getElementById('user-stories-list');
        
        loadBtn.disabled = true;
        loadBtn.textContent = 'Loading...';
        container.innerHTML = '<p>🔄 Loading JIRA stories...</p>';
        
        try {
            // Validate URL is from same origin
            const url = new URL('/api/jira-stories', window.location.origin);
            const response = await fetch(url.toString());
            const data = await response.json();
            
            if (data.stories && data.stories.length > 0) {
                this.allStories = data.stories;
                this.currentPage = 1;
                this.renderStoriesGrid(data.source, data.total);
            } else {
                container.innerHTML = `<div class="error-state"><p>❌ ${data.error || 'No stories found'}</p></div>`;
            }
        } catch (error) {
            container.innerHTML = `<div class="error-state"><p>❌ Error: ${error.message}</p></div>`;
        } finally {
            loadBtn.disabled = false;
            loadBtn.textContent = 'Refresh Stories';
        }
    }
    
    toggleStory(storyKey) {
        const index = this.selectedStories.indexOf(storyKey);
        if (index > -1) {
            this.selectedStories.splice(index, 1);
        } else {
            this.selectedStories.push(storyKey);
        }
        this.updateSelectionCount();
    }
    
    selectAllStories() {
        this.selectedStories = [...this.allStories.map(story => story.key)];
        this.renderStoriesGrid('jira-mcp', this.allStories.length);
    }
    
    clearStorySelection() {
        const checkboxes = document.querySelectorAll('#user-stories-list input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);
        this.selectedStories = [];
        this.updateSelectionCount();
    }
    
    renderStoriesGrid(source, total) {
        const container = document.getElementById('user-stories-list');
        const filteredStories = this.getFilteredStories();
        const totalPages = Math.ceil(filteredStories.length / this.pageSize);
        const startIndex = (this.currentPage - 1) * this.pageSize;
        const pageStories = filteredStories.slice(startIndex, startIndex + this.pageSize);
        
        container.innerHTML = `
            <div class="stories-grid-header">
                <h4>Select User Stories (${total} from ${source === 'jira-mcp' ? 'JIRA KW' : 'Demo'})</h4>
                <div class="grid-controls">
                    <input type="text" id="story-search" placeholder="Search stories..." value="${this.searchTerm}">
                    <button onclick="app.selectAllStories()" class="btn btn-small">Select All</button>
                    <button onclick="app.selectAllVisible()" class="btn btn-small">Select Page</button>
                    <button onclick="app.clearStorySelection()" class="btn btn-small">Clear All</button>
                </div>
            </div>
            <div class="stories-table">
                <div class="table-header">
                    <div class="col-select">Select</div>
                    <div class="col-key">Key</div>
                    <div class="col-summary">Summary</div>
                    <div class="col-status">Status</div>
                </div>
                ${pageStories.map(story => `
                    <div class="table-row">
                        <div class="col-select">
                            <input type="checkbox" value="${story.key}" ${this.selectedStories.includes(story.key) ? 'checked' : ''} onchange="app.toggleStory('${story.key}')">
                        </div>
                        <div class="col-key">${story.key}</div>
                        <div class="col-summary" title="${story.summary}">${story.summary}</div>
                        <div class="col-status">
                            <span class="status-badge status-${story.status?.toLowerCase().replace(/\s+/g, '-') || 'unknown'}">${story.status || 'Unknown'}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="pagination">
                <div class="pagination-info">${this.selectedStories.length} selected | Page ${this.currentPage} of ${totalPages} (${filteredStories.length} stories)</div>
                <div class="pagination-controls">
                    <button onclick="app.goToPage(1)" ${this.currentPage === 1 ? 'disabled' : ''}>First</button>
                    <button onclick="app.goToPage(${this.currentPage - 1})" ${this.currentPage === 1 ? 'disabled' : ''}>Prev</button>
                    <button onclick="app.goToPage(${this.currentPage + 1})" ${this.currentPage === totalPages ? 'disabled' : ''}>Next</button>
                    <button onclick="app.goToPage(${totalPages})" ${this.currentPage === totalPages ? 'disabled' : ''}>Last</button>
                </div>
            </div>
        `;
        
        document.getElementById('story-search').addEventListener('input', (e) => {
            this.searchTerm = e.target.value;
            this.currentPage = 1;
            this.renderStoriesGrid(source, total);
        });
    }
    
    getFilteredStories() {
        if (!this.searchTerm) return this.allStories;
        return this.allStories.filter(story => 
            story.key.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
            story.summary.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
            (story.description && story.description.toLowerCase().includes(this.searchTerm.toLowerCase()))
        );
    }
    
    goToPage(page) {
        const filteredStories = this.getFilteredStories();
        const totalPages = Math.ceil(filteredStories.length / this.pageSize);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.renderStoriesGrid('jira-mcp', this.allStories.length);
        }
    }
    
    selectAllVisible() {
        const checkboxes = document.querySelectorAll('.stories-table input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.checked = true;
            if (!this.selectedStories.includes(cb.value)) {
                this.selectedStories.push(cb.value);
            }
        });
        this.renderStoriesGrid('jira-mcp', this.allStories.length);
    }
    
    updateSelectionCount() {
        // This method is now handled in renderStoriesGrid
    }
    
    showRequirementModal() {
        const modal = document.getElementById('requirement-modal');
        modal.style.display = 'flex';
    }
    
    selectRequirementSource(source) {
        this.requirementSource = source;
        
        // Update visual selection
        document.querySelectorAll('.option-card').forEach(card => card.classList.remove('selected'));
        
        // Find the clicked card and select it
        const clickedCard = event ? event.target.closest('.option-card') : 
            document.querySelector(`[onclick*="'${source}'"]`);
        if (clickedCard) {
            clickedCard.classList.add('selected');
        }
        
        // Enable continue button
        const continueBtn = document.getElementById('continue-btn');
        if (continueBtn) {
            continueBtn.disabled = false;
        }
    }
    
    continueWithSelection() {
        if (!this.requirementSource) {
            return;
        }
        
        // Close modal
        document.getElementById('requirement-modal').style.display = 'none';
        
        // Show new project page
        document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
        document.getElementById('new-project-page').classList.add('active');
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        document.querySelector('[data-page="new-project"]').classList.add('active');
        
        // Set current page
        this.currentPage = 'new-project';
        
        // Configure form based on selection
        this.switchRequirementSource(this.requirementSource);
        this.setFormDefaults();
    }
    
    closeRequirementModal() {
        const modal = document.getElementById('requirement-modal');
        modal.style.display = 'none';
    }
    
    closeModal() {
        const modal = document.getElementById('requirement-modal');
        modal.style.display = 'none';
    }

    async deleteProject(projectId) {
        if (!this.showConfirm('Are you sure you want to delete this project? This will remove all files and cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showNotification('Project deleted successfully', 'success');
                this.loadProjects(); // Refresh the list
            } else {
                const error = await response.json();
                this.showNotification(`Failed to delete project: ${error.detail}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Error deleting project: ${error.message}`, 'error');
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
                this.showNotification('Failed to load generated code', 'error');
            }
        } catch (error) {
            this.showNotification(`Error loading code: ${error.message}`, 'error');
        }
    }

    async loadMetrics() {
        console.log('Loading metrics...');
        try {
            const response = await fetch('/api/metrics');
            console.log('Metrics response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const metrics = await response.json();
            console.log('Metrics data:', JSON.stringify(metrics, null, 2));
            
            document.getElementById('performance-metrics').innerHTML = this.formatPerformanceMetrics(metrics.performance);
            document.getElementById('llm-metrics').innerHTML = this.formatLLMMetrics(metrics.llm);
            document.getElementById('workflow-metrics').innerHTML = this.formatWorkflowMetrics(metrics.workflow);
        } catch (error) {
            console.error('Failed to load metrics:', error);
            document.getElementById('performance-metrics').innerHTML = `<p>Error: ${error.message}</p>`;
            document.getElementById('llm-metrics').innerHTML = `<p>Error: ${error.message}</p>`;
            document.getElementById('workflow-metrics').innerHTML = `<p>Error: ${error.message}</p>`;
        }
    }
    
    formatPerformanceMetrics(metrics) {
        if (!metrics || Object.keys(metrics).length === 0) {
            return '<p>No performance data available</p>';
        }
        
        let html = '';
        for (const [operation, data] of Object.entries(metrics)) {
            if (operation === 'total_projects') {
                html += `
                    <div class="metric-item">
                        <strong>Projects</strong><br>
                        Count: ${data.count}<br>
                        Files: ${data.files_generated}<br>
                        Size: ${data.total_size_mb}MB
                    </div>
                `;
            } else if (operation === 'analyses_completed') {
                html += `
                    <div class="metric-item">
                        <strong>Analyses</strong><br>
                        Count: ${data.count}<br>
                        Success: ${(data.success_rate * 100).toFixed(1)}%
                    </div>
                `;
            } else if (operation === 'code_generation') {
                html += `
                    <div class="metric-item">
                        <strong>Code Generation</strong><br>
                        Count: ${data.count}<br>
                        Success: ${(data.success_rate * 100).toFixed(1)}%
                    </div>
                `;
            }
        }
        return html;
    }
    
    formatLLMMetrics(metrics) {
        if (!metrics || Object.keys(metrics).length === 0) {
            return '<p>No LLM data available</p>';
        }
        
        return `
            <div class="metric-item">
                <strong>LLM Usage</strong><br>
                Total Requests: ${metrics.total_requests || 0}<br>
                Analysis Tasks: ${metrics.analysis_tasks || 0}<br>
                Coding Tasks: ${metrics.coding_tasks || 0}
            </div>
        `;
    }
    
    formatWorkflowMetrics(metrics) {
        if (!metrics || Object.keys(metrics).length === 0) {
            return '<p>No workflow data available</p>';
        }
        
        return `
            <div class="metric-item">
                <strong>Projects</strong><br>
                Total: ${metrics.total_projects || 0}<br>
                Completed: ${metrics.completed_projects || 0}<br>
                Avg Time: ${metrics.avg_completion_time || 'N/A'}
            </div>
        `;
    }
    
    initChat() {
        if (!this.chatInitialized) {
            this.chatInitialized = true;
            this.addChatMessage('assistant', 'Hello! I\'m your AI assistant. I can help you with:\n\n• Project requirements and clarifications\n• Technology stack recommendations\n• Architecture questions\n• Code review insights\n\nWhat would you like to know?');
        }
    }
    
    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;
        
        input.value = '';
        this.addChatMessage('user', message);
        this.addChatMessage('assistant', 'Thinking...');
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, context: this.getChatContext() })
            });
            
            const data = await response.json();
            this.updateLastMessage(data.response);
        } catch (error) {
            this.updateLastMessage('Sorry, I\'m having trouble connecting. Please try again.');
        }
    }
    
    addChatMessage(role, content) {
        const container = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`;
        messageDiv.innerHTML = `
            <div class="message-content">${this.renderMarkdown(content)}</div>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }
    
    updateLastMessage(content) {
        const messages = document.querySelectorAll('.chat-message.assistant');
        const lastMessage = messages[messages.length - 1];
        if (lastMessage) {
            lastMessage.querySelector('.message-content').innerHTML = this.renderMarkdown(content);
        }
    }
    
    getChatContext() {
        return {
            total_projects: Object.keys(projects || {}).length,
            current_page: this.currentPage,
            recent_projects: Object.values(projects || {}).slice(-3).map(p => ({ name: p.project_name, status: p.status }))
        };
    }
    
    clearChat() {
        document.getElementById('chat-messages').innerHTML = '';
        this.chatInitialized = false;
        this.initChat();
    }
    
    switchApprovalTab(event, tabId) {
        const analysisId = tabId.split('-').slice(1).join('-');
        const container = event.target.closest('.modern-approval-container');
        
        container.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        container.querySelectorAll('.approval-tab-content').forEach(content => content.classList.remove('active'));
        
        event.target.classList.add('active');
        document.getElementById(tabId).classList.add('active');
        
        if (tabId.startsWith('chat-')) {
            this.initAnalysisChat(analysisId);
        }
    }
    
    initAnalysisChat(analysisId) {
        const chatContainer = document.getElementById(`chat-messages-${analysisId}`);
        if (!chatContainer.innerHTML) {
            chatContainer.innerHTML = `
                <div class="chat-message assistant">
                    <div class="message-content">Hi! I'm the AI architect who created this analysis. Ask me anything about the technology choices, architecture decisions, or timeline estimates.</div>
                </div>
            `;
        }
    }
    
    async sendAnalysisChat(analysisId) {
        const input = document.getElementById(`chat-input-${analysisId}`);
        const message = input.value.trim();
        if (!message) return;
        
        input.value = '';
        const chatContainer = document.getElementById(`chat-messages-${analysisId}`);
        
        const chatHtml = `
            <div class="chat-message user">
                <div class="message-content">${this.escapeHtml(message)}</div>
            </div>
            <div class="chat-message assistant">
                <div class="message-content">Let me think about that...</div>
            </div>
        `;
        chatContainer.innerHTML += this.sanitizeHtml(chatHtml);
        
        try {
            const response = await fetch('/api/analysis-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, analysisId })
            });
            
            const data = await response.json();
            const messages = chatContainer.querySelectorAll('.chat-message.assistant');
            const lastMessage = messages[messages.length - 1];
            lastMessage.querySelector('.message-content').innerHTML = data.response;
        } catch (error) {
            const messages = chatContainer.querySelectorAll('.chat-message.assistant');
            const lastMessage = messages[messages.length - 1];
            lastMessage.querySelector('.message-content').innerHTML = 'I can help explain the technical decisions in this analysis. What specific aspect would you like me to clarify?';
        }
        
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    async expandAnalysis(analysisId) {
        const container = document.querySelector(`[data-analysis="${analysisId}"] .analysis-summary`);
        const contentDiv = container.querySelector('.markdown-content');
        const button = container.querySelector('.btn');
        
        if (container.classList.contains('expanded')) {
            container.classList.remove('expanded');
            // Get analysis from cache or fetch
            const analysis = this.analysisCache?.[analysisId];
            if (analysis) {
                contentDiv.innerHTML = this.renderMarkdown(analysis.content.substring(0, 500) + '...');
            }
            button.textContent = 'Read Full Analysis';
        } else {
            container.classList.add('expanded');
            // Get full analysis
            const analysis = this.analysisCache?.[analysisId];
            if (analysis) {
                contentDiv.innerHTML = this.renderMarkdown(analysis.content);
            }
            button.textContent = 'Show Summary';
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

// Make app globally available
window.app = app;