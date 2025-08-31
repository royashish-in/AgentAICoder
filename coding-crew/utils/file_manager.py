"""File management utilities for organizing project artifacts."""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class ProjectFileManager:
    """Manages file organization for generated project artifacts."""
    
    def __init__(self, base_output_dir: str = "generated_projects"):
        # Place generated_projects parallel to coding-crew folder
        current_dir = Path(__file__).parent.parent  # Go up from utils/file_manager.py to coding-crew/
        self.base_output_dir = current_dir.parent / base_output_dir  # Go up one more to AgentAI/
        self.base_output_dir.mkdir(exist_ok=True)
    
    def create_project_folder(self, project_name: str, requirement_id: str) -> Path:
        """Create a new project folder with sanitized name."""
        folder_name = f"{requirement_id}_{self._sanitize_name(project_name)}"
        project_path = self.base_output_dir / folder_name
        project_path.mkdir(exist_ok=True)
        
        # Create standard subdirectories
        (project_path / "analysis").mkdir(exist_ok=True)
        (project_path / "code").mkdir(exist_ok=True)
        (project_path / "tests").mkdir(exist_ok=True)
        (project_path / "docs").mkdir(exist_ok=True)
        
        return project_path
    
    def save_analysis(self, project_path: Path, analysis_content: str) -> Path:
        """Save analysis content to project folder."""
        analysis_file = project_path / "analysis" / "requirements_analysis.md"
        analysis_file.write_text(analysis_content, encoding='utf-8')
        
        # Extract and save diagrams as separate files
        self.extract_and_save_diagrams(analysis_content, project_path / "analysis")
        
        return analysis_file
    
    def extract_and_save_diagrams(self, content: str, output_dir: Path) -> List[Path]:
        """Extract draw.io XML diagrams and save as .drawio files."""
        diagrams_dir = output_dir / "diagrams"
        diagrams_dir.mkdir(exist_ok=True)
        
        xml_patterns = [
            r'```xml\s*(<mxfile[^>]*>.*?</mxfile>)\s*```',
            r'```drawio\s*(<mxfile[^>]*>.*?</mxfile>)\s*```',
            r'(<mxfile[^>]*>.*?</mxfile>)',
        ]
        
        diagrams = []
        for pattern in xml_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            diagrams.extend(matches)
        
        saved_files = []
        for i, diagram in enumerate(diagrams, 1):
            if '<mxfile' in diagram and '</mxfile>' in diagram:
                cleaned = diagram.strip()
                if not cleaned.startswith('<?xml'):
                    cleaned = '<?xml version="1.0" encoding="UTF-8"?>\n' + cleaned
                
                diagram_name = self._extract_diagram_name(cleaned) or f"diagram_{i}"
                diagram_file = diagrams_dir / f"{diagram_name}.drawio"
                diagram_file.write_text(cleaned, encoding='utf-8')
                saved_files.append(diagram_file)
        
        return saved_files
    
    def _extract_diagram_name(self, xml_content: str) -> str:
        """Extract diagram name from XML content."""
        name_match = re.search(r'<diagram[^>]*name=["\']([^"\'>]+)["\']', xml_content)
        if name_match:
            name = name_match.group(1)
            return re.sub(r'[^\w\-_]', '_', name).lower()
        return None
    
    def save_code_files(self, project_path: Path, code_content: str) -> List[Path]:
        """Extract and save individual code files from generated content."""
        code_dir = project_path / "code"
        saved_files = []
        
        # Extract code blocks with filenames
        file_blocks = self._extract_code_blocks(code_content)
        
        if file_blocks:
            for filename, content in file_blocks:
                file_path = code_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
                saved_files.append(file_path)
        else:
            # Save as single file if no individual files detected
            main_file = code_dir / "main.py"
            main_file.write_text(code_content, encoding='utf-8')
            saved_files.append(main_file)
        
        return saved_files
    
    def save_tests(self, project_path: Path, test_content: str) -> List[Path]:
        """Extract and save test files from generated content."""
        tests_dir = project_path / "tests"
        saved_files = []
        
        # Extract test files
        test_blocks = self._extract_test_blocks(test_content)
        
        if test_blocks:
            for filename, content in test_blocks:
                file_path = tests_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
                saved_files.append(file_path)
        else:
            # Save as single test file
            test_file = tests_dir / "test_main.py"
            test_file.write_text(test_content, encoding='utf-8')
            saved_files.append(test_file)
        
        return saved_files
    
    def save_documentation(self, project_path: Path, doc_content: str) -> List[Path]:
        """Extract and save documentation files from generated content."""
        docs_dir = project_path / "docs"
        saved_files = []
        
        # Extract documentation files
        doc_blocks = self._extract_doc_blocks(doc_content)
        
        if doc_blocks:
            for filename, content in doc_blocks:
                if filename.lower() == "readme.md":
                    file_path = project_path / filename
                else:
                    file_path = docs_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
                saved_files.append(file_path)
        else:
            # Save as README and docs file
            readme_file = project_path / "README.md"
            readme_file.write_text(doc_content, encoding='utf-8')
            saved_files.append(readme_file)
            
            docs_file = docs_dir / "documentation.md"
            docs_file.write_text(doc_content, encoding='utf-8')
            saved_files.append(docs_file)
        
        return saved_files
    
    def get_project_summary(self, project_path: Path) -> Dict:
        """Get summary of all files in project folder."""
        summary = {
            "analysis_files": [],
            "code_files": [],
            "test_files": [],
            "doc_files": [],
            "total_files": 0
        }
        
        for category, subdir in [
            ("analysis_files", "analysis"),
            ("code_files", "code"), 
            ("test_files", "tests"),
            ("doc_files", "docs")
        ]:
            subdir_path = project_path / subdir
            if subdir_path.exists():
                files = list(subdir_path.rglob("*"))
                summary[category] = [str(f.relative_to(project_path)) for f in files if f.is_file()]
        
        # Check for diagram files
        diagrams_dir = project_path / "analysis" / "diagrams"
        if diagrams_dir.exists():
            diagram_files = list(diagrams_dir.glob("*.drawio"))
            summary["diagram_files"] = [str(f.relative_to(project_path)) for f in diagram_files]
        else:
            summary["diagram_files"] = []
        
        summary["total_files"] = sum(len(files) for files in summary.values() if isinstance(files, list))
        return summary
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize project name for use as folder name."""
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized.lower()[:50]
    
    def _extract_code_blocks(self, content: str) -> List[Tuple[str, str]]:
        """Extract code blocks with filenames from generated content."""
        file_blocks = []
        
        patterns = [
            r'```\w*\s*#?\s*([^\n]+\.\w+)\s*\n(.*?)```',
            r'File:\s*([^\n]+\.\w+)\s*\n```\w*\n(.*?)```',
            r'([^\n]+\.\w+):\s*\n```\w*\n(.*?)```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for filename, code in matches:
                filename = filename.strip().split('/')[-1]
                file_blocks.append((filename, code.strip()))
        
        return file_blocks
    
    def _extract_test_blocks(self, content: str) -> List[Tuple[str, str]]:
        """Extract test files from generated content."""
        test_blocks = []
        
        patterns = [
            r'```\w*\s*#?\s*(test_[^\n]+\.py)\s*\n(.*?)```',
            r'```\w*\s*#?\s*([^\n]+_test\.py)\s*\n(.*?)```',
            r'```\w*\s*#?\s*(conftest\.py)\s*\n(.*?)```',
            r'File:\s*(test_[^\n]+\.py)\s*\n```\w*\n(.*?)```',
            r'(test_[^\n]+\.py):\s*\n```\w*\n(.*?)```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for filename, code in matches:
                filename = filename.strip().split('/')[-1]
                test_blocks.append((filename, code.strip()))
        
        return test_blocks
    
    def _extract_doc_blocks(self, content: str) -> List[Tuple[str, str]]:
        """Extract documentation files from generated content."""
        doc_blocks = []
        
        patterns = [
            r'```\w*\s*#?\s*([^\n]+\.md)\s*\n(.*?)```',
            r'File:\s*([^\n]+\.md)\s*\n```\w*\n(.*?)```',
            r'([^\n]+\.md):\s*\n```\w*\n(.*?)```',
            r'## ([^\n]+\.md)\s*\n(.*?)(?=##|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for filename, doc_content in matches:
                filename = filename.strip().split('/')[-1]
                doc_blocks.append((filename, doc_content.strip()))
        
        return doc_blocks