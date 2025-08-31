"""Simple JSON-based persistence for requests and audit logs."""

import json
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class DataStore:
    """Simple JSON file-based data persistence."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Data files
        self.projects_file = self.data_dir / "projects.json"
        self.workflows_file = self.data_dir / "workflows.json"
        self.analyses_file = self.data_dir / "analyses.json"
        self.approvals_file = self.data_dir / "approvals.json"
    
    def load_data(self) -> Dict[str, Dict]:
        """Load all data from JSON files."""
        return {
            "projects": self._load_json(self.projects_file),
            "workflows": self._load_json(self.workflows_file),
            "analyses": self._load_json(self.analyses_file),
            "approvals": self._load_json(self.approvals_file)
        }
    
    def save_projects(self, projects: Dict):
        """Save projects data."""
        self._save_json(self.projects_file, projects)
    
    def save_workflows(self, workflows: Dict):
        """Save workflows data."""
        self._save_json(self.workflows_file, workflows)
    
    def save_analyses(self, analyses: Dict):
        """Save analyses data."""
        self._save_json(self.analyses_file, analyses)
    
    def save_approvals(self, approvals: Dict):
        """Save approvals data."""
        self._save_json(self.approvals_file, approvals)
    
    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON data from file."""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_json(self, file_path: Path, data: Dict):
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Fail silently to avoid breaking the app