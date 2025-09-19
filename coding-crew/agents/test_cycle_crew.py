"""Test cycle crew for iterative testing and issue resolution."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
from typing import Dict, List
import json
from datetime import datetime

class TestCycleCrew:
    """CrewAI-based test cycle crew for iterative testing and issue resolution."""
    
    def __init__(self):
        from core.llm_config import get_testing_llm
        self.llm = get_testing_llm()
        self.max_iterations = 5
    
    def run_test_cycle(self, project_data: dict, code_content: str) -> dict:
        """Run iterative test cycle with issue detection and fixing."""
        
        # Test Agent
        test_agent = Agent(
            role="Story-Focused Test Engineer",
            goal="Identify issues that prevent JIRA story completion and generate story validation tests",
            backstory="Expert in validating software against user story requirements and acceptance criteria",
            llm=self.llm,
            verbose=True
        )
        
        # Code Fix Agent
        fix_agent = Agent(
            role="Story-Focused Developer",
            goal="Fix issues to enable JIRA story completion",
            backstory="Expert developer focused on delivering working solutions that fulfill user stories",
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
                
                PRIMARY OBJECTIVE: Identify issues that prevent this JIRA story from being fulfilled:
                {self._extract_story_context(project_data)}
                
                Current Code: {current_code[:2000]}...
                
                STORY-FOCUSED ISSUE IDENTIFICATION:
                - Does the code fulfill the story requirement?
                - Are there missing features needed for the story?
                - Can the story be demonstrated with this code?
                - Are there technical issues blocking story completion?
                
                Secondary technical issues:
                - Syntax errors
                - Logic errors
                - Missing error handling
                - Security vulnerabilities
                
                Output format:
                ISSUES FOUND:
                - Issue 1: [description] Story Impact: [BLOCKS_STORY/MINOR] Severity: [HIGH/MEDIUM/LOW]
                - Issue 2: [description] Story Impact: [BLOCKS_STORY/MINOR] Severity: [HIGH/MEDIUM/LOW]
                
                Prioritize issues that block story completion.
                """,
                agent=test_agent,
                expected_output="Detailed issue analysis with severity ratings"
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
                ITERATION {iteration}/{self.max_iterations} - STORY-FOCUSED CODE FIXING
                
                PRIMARY GOAL: Fix issues to enable JIRA story completion:
                {self._extract_story_context(project_data)}
                
                Current Code: {current_code[:2000]}...
                
                Issues to Fix:
                {json.dumps(issues, indent=2)}
                
                FIXING PRIORITIES:
                1. Fix issues that block story completion (HIGHEST PRIORITY)
                2. Fix critical technical issues
                3. Maintain story-required functionality
                4. Add error handling for story scenarios
                5. Improve code quality where it supports the story
                
                VALIDATION: Ensure the fixed code can demonstrate story fulfillment.
                
                Provide the COMPLETE FIXED CODE with story-focused improvements.
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
            Generate final test suite that validates JIRA story completion:
            
            Story Requirements:
            {self._extract_story_context(project_data)}
            
            Final Code: {current_code[:2000]}...
            
            Create test suite that PROVES story fulfillment:
            1. Story acceptance tests (PRIMARY)
            2. Story scenario validation
            3. Story constraint verification
            4. Basic functionality tests
            5. Error handling for story use cases
            
            CRITICAL: Tests must demonstrate that the story requirement is met.
            
            IMPORTANT: Generate ONLY TEST CODE, not the application code.
            Use appropriate testing framework for the technology stack.
            Include test file names and structure.
            
            Format:
            ```[language]
            // test_main.[ext] or similar
            [actual test code here]
            ```
            """,
            agent=test_agent,
            expected_output="Final comprehensive test suite with proper test file structure"
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
    
    def _extract_story_context(self, project_data: dict) -> str:
        """Extract story context for test cycle focus."""
        stories = project_data.get('user_stories', {}).get('user_stories', [])
        if not stories:
            return f"Project Goal: {project_data.get('description', 'No specific story requirements')}"
        
        primary_story = stories[0]
        return f"""
        Story: {primary_story.get('key', 'N/A')}
        Requirement: {primary_story.get('summary', 'N/A')}
        Details: {primary_story.get('description', 'N/A')}
        
        SUCCESS CRITERIA: Code must enable this story to be completed.
        """
    
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