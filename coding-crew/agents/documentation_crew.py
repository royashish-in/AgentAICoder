"""Documentation crew for generating comprehensive project documentation."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama

class DocumentationCrew:
    """CrewAI-based documentation crew for generating comprehensive project docs."""
    
    def __init__(self):
        from core.llm_config import get_documentation_llm
        self.llm = get_documentation_llm()
    
    def generate_documentation(self, project_data: dict, analysis: str, code_content: str, tests: str) -> dict:
        """Generate comprehensive documentation for the project."""
        
        # Documentation Agent
        doc_agent = Agent(
            role="Story-Focused Technical Writer",
            goal="Create documentation that helps users achieve the JIRA story objective",
            backstory="Expert technical writer specializing in user-focused documentation that enables story completion",
            llm=self.llm,
            verbose=True
        )
        
        # Documentation Review Agent
        review_agent = Agent(
            role="Story Documentation Reviewer",
            goal="Ensure documentation enables users to fulfill the JIRA story",
            backstory="Senior developer focused on documentation that directly supports user story completion",
            llm=self.llm,
            verbose=True
        )
        
        # Documentation Generation Task
        doc_task = Task(
            description=f"""
            Create COMPREHENSIVE END-USER DOCUMENTATION for:
            {self._extract_story_context(project_data)}
            
            Project Context:
            - Project: {project_data.get('project_name', 'Unknown')}
            - Description: {project_data.get('description', '')}
            - Target Users: {project_data.get('target_users', '')}
            - Tech Stack: {project_data.get('recommended_tech_stack', [])}
            
            Generated Solution:
            - Code: {code_content[:1000]}...
            - Tests: {tests[:500]}...
            
            Create COMPLETE documentation covering:
            
            ```markdown
            # README.md
            # {project_data.get('project_name', 'Project')}
            
            ## Overview
            [What this solution does and why it exists]
            
            ## Features
            [Key capabilities and functionality]
            
            ## Installation
            [Step-by-step setup instructions]
            
            ## Usage
            [How to use the solution with examples]
            
            ## API/Interface Documentation
            [Endpoints, functions, or UI elements]
            
            ## Configuration
            [Settings and customization options]
            
            ## Troubleshooting
            [Common issues and solutions]
            ```
            
            REQUIREMENTS:
            1. Explain WHAT the solution does
            2. Show HOW to install and run it
            3. Demonstrate HOW to use all features
            4. Include practical examples
            5. Cover configuration options
            6. Address common issues
            """,
            agent=doc_agent,
            expected_output="Complete end-user documentation with installation, usage, and troubleshooting"
        )
        
        # Documentation Review Task
        review_task = Task(
            description=f"""
            Review documentation for COMPLETENESS and END-USER USABILITY:
            
            Story Requirements:
            {self._extract_story_context(project_data)}
            
            Review Criteria:
            1. SOLUTION CLARITY: Is it clear what the solution does?
            2. INSTALLATION: Can users install/setup from these instructions?
            3. USAGE EXAMPLES: Are there practical examples for all features?
            4. CONFIGURATION: Are customization options documented?
            5. TROUBLESHOOTING: Are common issues addressed?
            6. COMPLETENESS: Can users fully utilize the solution?
            
            Ensure documentation serves as complete user manual for the delivered solution.
            """,
            agent=review_agent,
            expected_output="Complete, user-friendly documentation covering all aspects of the solution"
        )
        
        # Create and run crew
        crew = Crew(
            agents=[doc_agent, review_agent],
            tasks=[doc_task, review_task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        return {
            "documentation": str(result),
            "doc_files": self._extract_doc_files(str(result))
        }
    
    def _extract_story_context(self, project_data: dict) -> str:
        """Extract story context for documentation focus."""
        stories = project_data.get('user_stories', {}).get('user_stories', [])
        if not stories:
            return f"Project Goal: {project_data.get('description', 'No specific story requirements')}"
        
        primary_story = stories[0]
        return f"""
        Story: {primary_story.get('key', 'N/A')}
        Requirement: {primary_story.get('summary', 'N/A')}
        Details: {primary_story.get('description', 'N/A')}
        
        DOCUMENTATION GOAL: Enable users to fulfill this story requirement.
        """
    
    def _extract_doc_files(self, content: str) -> list:
        """Extract documentation file names from generated content."""
        import re
        
        patterns = [
            r'README\.md',
            r'[A-Z_]+\.md',
            r'[a-z_]+\.md',
            r'docs/[a-zA-Z_/]+\.md'
        ]
        
        files = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            files.extend(matches)
        
        return list(set(files))