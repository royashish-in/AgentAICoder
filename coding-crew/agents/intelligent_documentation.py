"""Intelligent Documentation Generator for context-aware API docs and code comments."""

import json
import ast
import os
import re
from typing import Dict, List, Optional, Any
from crewai import Agent, Task, Crew
from langchain_ollama import ChatOllama

class IntelligentDocumentation:
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.llm = ChatOllama(model=model_name, temperature=0.2)
        self.agent = Agent(
            role="Documentation Specialist",
            goal="Generate comprehensive, context-aware documentation and code comments",
            backstory="Expert technical writer with deep understanding of code structure and API design",
            llm=self.llm,
            verbose=True
        )

    def generate_api_docs(self, code: str, file_path: str) -> Dict[str, Any]:
        """Generate comprehensive API documentation."""
        # Extract API endpoints and functions
        api_elements = self._extract_api_elements(code)
        
        task = Task(
            description=f"""
            Generate comprehensive API documentation for this code:
            
            File: {file_path}
            Code:
            {code}
            
            API Elements Found:
            {json.dumps(api_elements, indent=2)}
            
            Generate:
            1. API overview and purpose
            2. Endpoint documentation with parameters, responses
            3. Usage examples
            4. Error handling documentation
            
            Format as JSON with keys: overview, endpoints, examples, error_handling
            """,
            agent=self.agent,
            expected_output="JSON API documentation"
        )
        
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        try:
            return json.loads(str(result))
        except:
            return {
                "overview": "API documentation generated",
                "endpoints": api_elements,
                "examples": ["See code for usage examples"],
                "error_handling": ["Standard HTTP error codes apply"]
            }

    def _extract_api_elements(self, code: str) -> List[Dict[str, Any]]:
        """Extract API endpoints and functions from code."""
        elements = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for FastAPI decorators
                    decorators = [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]
                    
                    if any('app.' in str(d) or 'router.' in str(d) for d in decorators):
                        elements.append({
                            "name": node.name,
                            "type": "endpoint",
                            "line": node.lineno,
                            "parameters": [arg.arg for arg in node.args.args],
                            "decorators": decorators
                        })
                    else:
                        elements.append({
                            "name": node.name,
                            "type": "function",
                            "line": node.lineno,
                            "parameters": [arg.arg for arg in node.args.args]
                        })
                
                elif isinstance(node, ast.ClassDef):
                    elements.append({
                        "name": node.name,
                        "type": "class",
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
        except:
            pass
        
        return elements

    def generate_code_comments(self, code: str, file_path: str) -> str:
        """Generate intelligent code comments."""
        task = Task(
            description=f"""
            Add intelligent comments to this code:
            
            File: {file_path}
            Code:
            {code}
            
            Add:
            1. Function/class docstrings
            2. Inline comments for complex logic
            3. Parameter and return type documentation
            4. Usage examples where helpful
            
            Return the complete code with added comments.
            """,
            agent=self.agent,
            expected_output="Code with intelligent comments added"
        )
        
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        return str(result)

    def generate_adr(self, decision_context: Dict[str, Any]) -> str:
        """Generate Architecture Decision Record (ADR)."""
        task = Task(
            description=f"""
            Create an Architecture Decision Record (ADR) for this decision:
            
            Context: {decision_context.get('context', '')}
            Decision: {decision_context.get('decision', '')}
            Alternatives: {decision_context.get('alternatives', [])}
            Consequences: {decision_context.get('consequences', '')}
            
            Format as standard ADR with:
            1. Title
            2. Status
            3. Context
            4. Decision
            5. Consequences
            
            Use markdown format.
            """,
            agent=self.agent,
            expected_output="Markdown formatted ADR"
        )
        
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        return str(result)

    def generate_readme(self, project_path: str, project_info: Dict[str, Any]) -> str:
        """Generate comprehensive README.md."""
        # Analyze project structure
        structure = self._analyze_project_structure(project_path)
        
        task = Task(
            description=f"""
            Generate a comprehensive README.md for this project:
            
            Project Info:
            {json.dumps(project_info, indent=2)}
            
            Project Structure:
            {json.dumps(structure, indent=2)}
            
            Include:
            1. Project description and features
            2. Installation instructions
            3. Usage examples
            4. API documentation
            5. Contributing guidelines
            6. License information
            
            Use proper markdown formatting.
            """,
            agent=self.agent,
            expected_output="Comprehensive README.md content"
        )
        
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        return str(result)

    def _analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze project structure for documentation."""
        structure = {
            "directories": [],
            "python_files": [],
            "config_files": [],
            "dependencies": []
        }
        
        for root, dirs, files in os.walk(project_path):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            rel_root = os.path.relpath(root, project_path)
            if rel_root != '.':
                structure["directories"].append(rel_root)
            
            for file in files:
                if file.endswith('.py'):
                    structure["python_files"].append(os.path.join(rel_root, file))
                elif file in ['requirements.txt', 'pyproject.toml', 'setup.py', 'Dockerfile']:
                    structure["config_files"].append(file)
        
        return structure

    def documentation_workflow(self, project_path: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Complete documentation generation workflow."""
        results = {
            "readme": "",
            "api_docs": {},
            "commented_files": [],
            "adrs": []
        }
        
        # Generate README
        results["readme"] = self.generate_readme(project_path, project_info)
        
        # Process Python files
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r') as f:
                            code = f.read()
                        
                        # Generate API docs for API files
                        if 'app.py' in file or 'api' in file_path.lower():
                            api_docs = self.generate_api_docs(code, file_path)
                            results["api_docs"][file_path] = api_docs
                        
                        # Generate comments for all files
                        commented_code = self.generate_code_comments(code, file_path)
                        results["commented_files"].append({
                            "file": file_path,
                            "commented_code": commented_code
                        })
                        
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
        
        return results