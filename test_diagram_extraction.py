#!/usr/bin/env python3
"""Test diagram extraction functionality."""

import sys
from pathlib import Path
sys.path.append('coding-crew')

from utils.file_manager import ProjectFileManager

# Test on existing project
project_path = Path("generated_projects/REQ-20250831-853E995B_pyread")
analysis_file = project_path / "analysis" / "requirements_analysis.md"

if analysis_file.exists():
    print(f"Testing diagram extraction on: {project_path}")
    
    # Read analysis content
    content = analysis_file.read_text(encoding='utf-8')
    
    # Create file manager and extract diagrams
    file_manager = ProjectFileManager()
    saved_diagrams = file_manager.extract_and_save_diagrams(content, project_path / "analysis")
    
    print(f"Extracted {len(saved_diagrams)} diagrams:")
    for diagram_file in saved_diagrams:
        print(f"  - {diagram_file.name}")
        print(f"    Size: {diagram_file.stat().st_size} bytes")
    
    # Check project summary
    summary = file_manager.get_project_summary(project_path)
    print(f"\nProject summary:")
    for key, value in summary.items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} files")
        else:
            print(f"  {key}: {value}")
else:
    print(f"Analysis file not found: {analysis_file}")