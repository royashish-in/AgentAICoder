"""Multi-Project Management with templates, dependencies, and workspace organization."""

import json
import os
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class ProjectManager:
    def __init__(self, workspace_path: str = "generated_projects"):
        self.workspace_path = workspace_path
        self.projects_db = os.path.join(workspace_path, "projects.json")
        self.templates_path = os.path.join(workspace_path, "templates")
        self._ensure_workspace()

    def _ensure_workspace(self):
        """Ensure workspace directories exist."""
        os.makedirs(self.workspace_path, exist_ok=True)
        os.makedirs(self.templates_path, exist_ok=True)
        
        if not os.path.exists(self.projects_db):
            with open(self.projects_db, 'w') as f:
                json.dump({"projects": {}, "templates": {}}, f, indent=2)

    def create_project(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create new project with template and configuration."""
        project_id = str(uuid.uuid4())
        project_name = project_config.get('name', f'project_{project_id[:8]}')
        
        # Create project directory
        project_path = os.path.join(self.workspace_path, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Apply template if specified
        template_name = project_config.get('template')
        if template_name:
            self._apply_template(project_path, template_name)
        
        # Create project metadata
        project_data = {
            "id": project_id,
            "name": project_name,
            "path": project_path,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "config": project_config,
            "dependencies": [],
            "tags": project_config.get('tags', []),
            "description": project_config.get('description', ''),
            "technology_stack": project_config.get('technology_stack', [])
        }
        
        # Save to database
        self._save_project(project_id, project_data)
        
        return {
            "project_id": project_id,
            "project_path": project_path,
            "status": "created",
            "project_data": project_data
        }

    def _apply_template(self, project_path: str, template_name: str):
        """Apply project template to new project."""
        template_path = os.path.join(self.templates_path, template_name)
        
        if os.path.exists(template_path):
            # Copy template files
            for item in os.listdir(template_path):
                src = os.path.join(template_path, item)
                dst = os.path.join(project_path, item)
                
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)

    def create_template(self, template_name: str, source_project_path: str, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create project template from existing project."""
        template_path = os.path.join(self.templates_path, template_name)
        
        # Copy project structure
        if os.path.exists(source_project_path):
            shutil.copytree(source_project_path, template_path, dirs_exist_ok=True)
            
            # Create template metadata
            template_data = {
                "name": template_name,
                "description": template_config.get('description', ''),
                "technology_stack": template_config.get('technology_stack', []),
                "created_at": datetime.now().isoformat(),
                "source_project": source_project_path,
                "variables": template_config.get('variables', {}),
                "files": self._get_template_files(template_path)
            }
            
            # Save template metadata
            with open(os.path.join(template_path, 'template.json'), 'w') as f:
                json.dump(template_data, f, indent=2)
            
            # Update templates database
            self._save_template(template_name, template_data)
            
            return {"status": "success", "template_path": template_path}
        
        return {"status": "error", "message": "Source project not found"}

    def _get_template_files(self, template_path: str) -> List[str]:
        """Get list of files in template."""
        files = []
        for root, dirs, filenames in os.walk(template_path):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), template_path)
                files.append(rel_path)
        return files

    def list_projects(self, status: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List projects with optional filtering."""
        projects_data = self._load_projects_db()
        projects = list(projects_data["projects"].values())
        
        # Filter by status
        if status:
            projects = [p for p in projects if p.get('status') == status]
        
        # Filter by tags
        if tags:
            projects = [p for p in projects if any(tag in p.get('tags', []) for tag in tags)]
        
        return projects

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID."""
        projects_data = self._load_projects_db()
        return projects_data["projects"].get(project_id)

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update project configuration."""
        project_data = self.get_project(project_id)
        
        if project_data:
            project_data.update(updates)
            project_data["updated_at"] = datetime.now().isoformat()
            self._save_project(project_id, project_data)
            return {"status": "success", "project_data": project_data}
        
        return {"status": "error", "message": "Project not found"}

    def delete_project(self, project_id: str, delete_files: bool = False) -> Dict[str, Any]:
        """Delete project and optionally its files."""
        project_data = self.get_project(project_id)
        
        if project_data:
            # Delete files if requested
            if delete_files and os.path.exists(project_data["path"]):
                shutil.rmtree(project_data["path"])
            
            # Remove from database
            projects_data = self._load_projects_db()
            del projects_data["projects"][project_id]
            self._save_projects_db(projects_data)
            
            return {"status": "success", "message": "Project deleted"}
        
        return {"status": "error", "message": "Project not found"}

    def manage_dependencies(self, project_id: str, action: str, dependency: str) -> Dict[str, Any]:
        """Manage project dependencies."""
        project_data = self.get_project(project_id)
        
        if not project_data:
            return {"status": "error", "message": "Project not found"}
        
        dependencies = project_data.get("dependencies", [])
        
        if action == "add" and dependency not in dependencies:
            dependencies.append(dependency)
        elif action == "remove" and dependency in dependencies:
            dependencies.remove(dependency)
        
        project_data["dependencies"] = dependencies
        self._save_project(project_id, project_data)
        
        return {"status": "success", "dependencies": dependencies}

    def get_workspace_stats(self) -> Dict[str, Any]:
        """Get workspace statistics."""
        projects = self.list_projects()
        
        stats = {
            "total_projects": len(projects),
            "active_projects": len([p for p in projects if p.get('status') == 'active']),
            "completed_projects": len([p for p in projects if p.get('status') == 'completed']),
            "technology_stacks": {},
            "tags": {}
        }
        
        # Count technology stacks and tags
        for project in projects:
            for tech in project.get('technology_stack', []):
                stats["technology_stacks"][tech] = stats["technology_stacks"].get(tech, 0) + 1
            
            for tag in project.get('tags', []):
                stats["tags"][tag] = stats["tags"].get(tag, 0) + 1
        
        return stats

    def _save_project(self, project_id: str, project_data: Dict[str, Any]):
        """Save project to database."""
        projects_data = self._load_projects_db()
        projects_data["projects"][project_id] = project_data
        self._save_projects_db(projects_data)

    def _save_template(self, template_name: str, template_data: Dict[str, Any]):
        """Save template to database."""
        projects_data = self._load_projects_db()
        projects_data["templates"][template_name] = template_data
        self._save_projects_db(projects_data)

    def _load_projects_db(self) -> Dict[str, Any]:
        """Load projects database."""
        with open(self.projects_db, 'r') as f:
            return json.load(f)

    def _save_projects_db(self, data: Dict[str, Any]):
        """Save projects database."""
        with open(self.projects_db, 'w') as f:
            json.dump(data, f, indent=2)