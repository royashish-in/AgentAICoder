"""Smart Code Refactoring with automated code smell detection and safe refactoring execution."""

import json
import ast
import os
from typing import Dict, List, Optional, Any
from crewai import Agent, Task, Crew
from langchain_ollama import ChatOllama

class SmartRefactoring:
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.llm = ChatOllama(model=model_name, temperature=0.1)
        self.agent = Agent(
            role="Code Refactoring Specialist",
            goal="Detect code smells, suggest refactoring improvements, and ensure safe code transformations",
            backstory="Expert in clean code principles, design patterns, and safe refactoring techniques",
            llm=self.llm,
            verbose=True
        )

    def detect_code_smells(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Detect code smells and quality issues."""
        smells = []
        
        try:
            tree = ast.parse(code)
            
            # Analyze AST for common issues
            for node in ast.walk(tree):
                # Long methods
                if isinstance(node, ast.FunctionDef):
                    lines = len(code.split('\n'))
                    if lines > 50:
                        smells.append({
                            "type": "Long Method",
                            "severity": "medium",
                            "line": node.lineno,
                            "description": f"Method '{node.name}' is too long ({lines} lines)",
                            "suggestion": "Break into smaller methods"
                        })
                
                # Too many parameters
                if isinstance(node, ast.FunctionDef) and len(node.args.args) > 5:
                    smells.append({
                        "type": "Long Parameter List",
                        "severity": "medium",
                        "line": node.lineno,
                        "description": f"Method '{node.name}' has {len(node.args.args)} parameters",
                        "suggestion": "Use parameter object or builder pattern"
                    })
        except:
            pass
        
        # AI-powered smell detection
        ai_smells = self._ai_smell_detection(code, file_path)
        smells.extend(ai_smells)
        
        return smells

    def _ai_smell_detection(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Use AI to detect complex code smells."""
        task = Task(
            description=f"""
            Analyze this code for quality issues and code smells:
            
            File: {file_path}
            Code:
            {code}
            
            Identify:
            1. Code smells (duplicated code, large classes, etc.)
            2. Design pattern violations
            3. Performance issues
            4. Maintainability concerns
            
            Format as JSON array with keys: type, severity, line, description, suggestion
            """,
            agent=self.agent,
            expected_output="JSON array of code smell detections"
        )
        
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        try:
            return json.loads(str(result))
        except:
            return []

    def suggest_refactoring(self, code: str, smells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate refactoring suggestions with impact analysis."""
        task = Task(
            description=f"""
            Provide refactoring suggestions for this code with detected issues:
            
            Code:
            {code}
            
            Issues:
            {json.dumps(smells, indent=2)}
            
            Provide:
            1. Refactoring strategy
            2. Step-by-step refactoring plan
            3. Impact analysis (risk level, effort, benefits)
            4. Refactored code example
            
            Format as JSON with keys: strategy, plan, impact, refactored_code
            """,
            agent=self.agent,
            expected_output="JSON refactoring recommendations"
        )
        
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        try:
            return json.loads(str(result))
        except:
            return {
                "strategy": "Incremental refactoring",
                "plan": ["Address high-priority issues first"],
                "impact": {"risk": "low", "effort": "medium", "benefits": "improved maintainability"},
                "refactored_code": code
            }

    def safe_refactor(self, file_path: str, refactoring_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute safe refactoring with rollback capability."""
        # Create backup
        backup_path = f"{file_path}.backup"
        
        try:
            with open(file_path, 'r') as f:
                original_code = f.read()
            
            with open(backup_path, 'w') as f:
                f.write(original_code)
            
            # Apply refactoring
            refactored_code = refactoring_plan.get('refactored_code', original_code)
            
            with open(file_path, 'w') as f:
                f.write(refactored_code)
            
            return {
                "status": "success",
                "backup_path": backup_path,
                "changes_applied": True,
                "rollback_available": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "changes_applied": False,
                "rollback_available": os.path.exists(backup_path)
            }

    def rollback_refactoring(self, file_path: str, backup_path: str) -> Dict[str, Any]:
        """Rollback refactoring changes."""
        try:
            if os.path.exists(backup_path):
                with open(backup_path, 'r') as f:
                    original_code = f.read()
                
                with open(file_path, 'w') as f:
                    f.write(original_code)
                
                os.remove(backup_path)
                
                return {"status": "success", "message": "Refactoring rolled back successfully"}
            else:
                return {"status": "error", "message": "Backup file not found"}
                
        except Exception as e:
            return {"status": "error", "message": f"Rollback failed: {str(e)}"}

    def refactoring_workflow(self, project_path: str, target_files: List[str] = None) -> Dict[str, Any]:
        """Complete refactoring workflow for project files."""
        results = {}
        
        if not target_files:
            target_files = []
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.py'):
                        target_files.append(os.path.join(root, file))
        
        for file_path in target_files:
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                
                # Detect issues
                smells = self.detect_code_smells(code, file_path)
                
                if smells:
                    # Generate refactoring suggestions
                    suggestions = self.suggest_refactoring(code, smells)
                    
                    results[file_path] = {
                        "smells_detected": len(smells),
                        "smells": smells,
                        "refactoring_suggestions": suggestions,
                        "refactoring_ready": True
                    }
                else:
                    results[file_path] = {
                        "smells_detected": 0,
                        "status": "clean",
                        "refactoring_ready": False
                    }
                    
            except Exception as e:
                results[file_path] = {
                    "error": str(e),
                    "refactoring_ready": False
                }
        
        return {
            "files_analyzed": len(target_files),
            "files_with_issues": len([r for r in results.values() if r.get('smells_detected', 0) > 0]),
            "results": results
        }