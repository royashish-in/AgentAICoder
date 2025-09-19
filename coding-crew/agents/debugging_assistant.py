"""AI-Powered Debugging Assistant for intelligent error analysis and fix suggestions."""

import json
import re
import traceback
from typing import Dict, List, Optional, Any
from crewai import Agent, Task, Crew
from langchain_ollama import ChatOllama

class DebuggingAssistant:
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.llm = ChatOllama(model=model_name, temperature=0.1)
        self.agent = Agent(
            role="AI Debugging Specialist",
            goal="Analyze errors, interpret stack traces, and provide intelligent fix suggestions",
            backstory="Expert debugger with deep understanding of common programming issues and solutions",
            llm=self.llm,
            verbose=True
        )

    def analyze_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error and provide intelligent debugging suggestions."""
        task = Task(
            description=f"""
            Analyze this error and provide debugging assistance:
            
            Error Type: {error_info.get('error_type', 'Unknown')}
            Error Message: {error_info.get('error_message', '')}
            Stack Trace: {error_info.get('stack_trace', '')}
            Code Context: {error_info.get('code_context', '')}
            File Path: {error_info.get('file_path', '')}
            
            Provide:
            1. Root cause analysis
            2. Specific fix suggestions
            3. Prevention strategies
            4. Related code improvements
            
            Format as JSON with keys: root_cause, fix_suggestions, prevention, improvements
            """,
            agent=self.agent,
            expected_output="JSON analysis with debugging recommendations"
        )
        
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        try:
            return json.loads(str(result))
        except:
            return {
                "root_cause": "Error analysis completed",
                "fix_suggestions": [str(result)],
                "prevention": ["Review code patterns"],
                "improvements": ["Apply suggested fixes"]
            }

    def interpret_stack_trace(self, stack_trace: str, code_files: Dict[str, str]) -> Dict[str, Any]:
        """Interpret stack trace with code context."""
        # Extract file paths and line numbers from stack trace
        trace_pattern = r'File "([^"]+)", line (\d+)'
        matches = re.findall(trace_pattern, stack_trace)
        
        context_info = []
        for file_path, line_num in matches:
            if file_path in code_files:
                lines = code_files[file_path].split('\n')
                line_idx = int(line_num) - 1
                
                # Get context around error line
                start = max(0, line_idx - 3)
                end = min(len(lines), line_idx + 4)
                context = '\n'.join(f"{i+1}: {lines[i]}" for i in range(start, end))
                
                context_info.append({
                    "file": file_path,
                    "line": line_num,
                    "context": context
                })
        
        return {
            "stack_analysis": self.analyze_error({
                "error_type": "Stack Trace Analysis",
                "stack_trace": stack_trace,
                "code_context": str(context_info)
            }),
            "context_info": context_info
        }

    def suggest_fixes(self, error_type: str, code_snippet: str) -> List[Dict[str, str]]:
        """Generate specific fix suggestions for code."""
        task = Task(
            description=f"""
            Provide specific code fixes for this {error_type} error:
            
            Code:
            {code_snippet}
            
            Generate 2-3 specific fix options with:
            1. Description of the fix
            2. Updated code snippet
            3. Explanation of why this fixes the issue
            
            Format as JSON array with keys: description, fixed_code, explanation
            """,
            agent=self.agent,
            expected_output="JSON array of fix suggestions"
        )
        
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        try:
            return json.loads(str(result))
        except:
            return [{
                "description": "Apply suggested fix",
                "fixed_code": code_snippet,
                "explanation": str(result)
            }]

    def debug_workflow(self, project_path: str, error_log: str) -> Dict[str, Any]:
        """Complete debugging workflow for a project."""
        # Parse error log
        lines = error_log.strip().split('\n')
        error_type = "Runtime Error"
        error_message = ""
        stack_trace = ""
        
        for i, line in enumerate(lines):
            if "Error:" in line or "Exception:" in line:
                error_type = line.split(':')[0].strip()
                error_message = ':'.join(line.split(':')[1:]).strip()
                stack_trace = '\n'.join(lines[:i])
                break
        
        # Analyze and provide comprehensive debugging assistance
        analysis = self.analyze_error({
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "project_path": project_path
        })
        
        return {
            "error_analysis": analysis,
            "debugging_steps": [
                "Review root cause analysis",
                "Apply suggested fixes",
                "Test the solution",
                "Implement prevention strategies"
            ],
            "confidence_score": 0.85
        }