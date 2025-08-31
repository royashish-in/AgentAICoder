"""Test cycle crew for iterative testing and issue resolution."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from typing import Dict, List
import json
from datetime import datetime

class TestCycleCrew:
    """CrewAI-based test cycle crew for iterative testing and issue resolution."""
    
    def __init__(self):
        from config import get_ollama_config
        ollama_config = get_ollama_config()
        self.llm = Ollama(model=ollama_config["model"], base_url=ollama_config["base_url"])
        self.max_iterations = 5
    
    def run_test_cycle(self, project_data: dict, code_content: str) -> dict:
        """Run iterative test cycle with issue detection and fixing."""
        
        # Test Agent
        test_agent = Agent(
            role="Senior Test Engineer",
            goal="Generate comprehensive tests and identify code issues",
            backstory="Expert in test-driven development, bug detection, and quality assurance",
            llm=self.llm,
            verbose=True
        )
        
        # Code Fix Agent
        fix_agent = Agent(
            role="Senior Developer",
            goal="Fix identified issues and improve code quality",
            backstory="Expert developer focused on bug fixes, code optimization, and maintainability",
            llm=self.llm,
            verbose=True
        )
        
        issues_log = []
        current_code = code_content
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Test Generation and Issue Detection Task
            test_task = Task(
                description=f"""
                ITERATION {iteration}/{self.max_iterations}
                
                Analyze the current code and generate comprehensive tests:
                
                Project: {project_data.get('project_name', 'Unknown')}
                Current Code: {current_code[:2000]}...
                
                Tasks:
                1. Generate unit tests for all functions/classes
                2. Create integration tests
                3. Test edge cases and error conditions
                4. IDENTIFY SPECIFIC ISSUES in the code:
                   - Syntax errors
                   - Logic errors
                   - Missing error handling
                   - Performance issues
                   - Security vulnerabilities
                   - Missing functionality
                
                Output format:
                TESTS:
                [test code here]
                
                ISSUES FOUND:
                - Issue 1: [description]
                - Issue 2: [description]
                
                SEVERITY: [HIGH/MEDIUM/LOW for each issue]
                """,
                agent=test_agent,
                expected_output="Test suite with detailed issue analysis and severity ratings"
            )
            
            test_result = Crew(
                agents=[test_agent],
                tasks=[test_task],
                verbose=True
            ).kickoff()
            
            # Extract issues from test result
            issues = self._extract_issues(str(test_result))
            
            if not issues:
                # No issues found, cycle complete
                break
            
            # Log issues for this iteration
            iteration_log = {
                "iteration": iteration,
                "timestamp": datetime.now().isoformat(),
                "issues_found": issues,
                "code_version": current_code[:500] + "..."
            }
            issues_log.append(iteration_log)
            
            # Code Fix Task
            fix_task = Task(
                description=f"""
                ITERATION {iteration}/{self.max_iterations} - CODE FIXING
                
                Fix the following issues in the code:
                
                Current Code: {current_code[:2000]}...
                
                Issues to Fix:
                {json.dumps(issues, indent=2)}
                
                Requirements:
                1. Fix ALL identified issues
                2. Maintain existing functionality
                3. Improve code quality and robustness
                4. Add proper error handling
                5. Ensure code follows best practices
                
                Provide the COMPLETE FIXED CODE with all improvements.
                """,
                agent=fix_agent,
                expected_output="Complete fixed code with all issues resolved"
            )
            
            fix_result = Crew(
                agents=[fix_agent],
                tasks=[fix_task],
                verbose=True
            ).kickoff()
            
            # Update current code with fixes
            current_code = str(fix_result)
            
            # Log the fix
            issues_log[-1]["fixes_applied"] = current_code[:500] + "..."
        
        # Final test generation
        final_test_task = Task(
            description=f"""
            Generate final comprehensive test suite for the refined code:
            
            Final Code: {current_code[:2000]}...
            
            Create complete test suite with:
            1. Unit tests for all components
            2. Integration tests
            3. Edge case tests
            4. Performance tests
            5. Error handling tests
            """,
            agent=test_agent,
            expected_output="Final comprehensive test suite"
        )
        
        final_tests = Crew(
            agents=[test_agent],
            tasks=[final_test_task],
            verbose=True
        ).kickoff()
        
        return {
            "final_code": current_code,
            "final_tests": str(final_tests),
            "iterations_completed": iteration,
            "issues_log": issues_log,
            "total_issues_fixed": sum(len(log["issues_found"]) for log in issues_log)
        }
    
    def _extract_issues(self, test_result: str) -> List[Dict]:
        """Extract issues from test result."""
        issues = []
        lines = test_result.split('\n')
        
        in_issues_section = False
        current_issue = None
        
        for line in lines:
            line = line.strip()
            
            if "ISSUES FOUND:" in line.upper():
                in_issues_section = True
                continue
            
            if in_issues_section:
                if line.startswith('- ') or line.startswith('* '):
                    issue_text = line[2:].strip()
                    if issue_text:
                        issues.append({
                            "description": issue_text,
                            "severity": self._extract_severity(issue_text),
                            "timestamp": datetime.now().isoformat()
                        })
                elif line.startswith('SEVERITY:') or line.startswith('TESTS:'):
                    break
        
        return issues
    
    def _extract_severity(self, issue_text: str) -> str:
        """Extract severity from issue text."""
        issue_lower = issue_text.lower()
        
        if any(word in issue_lower for word in ['critical', 'security', 'crash', 'fatal']):
            return "HIGH"
        elif any(word in issue_lower for word in ['performance', 'optimization', 'missing']):
            return "MEDIUM"
        else:
            return "LOW"