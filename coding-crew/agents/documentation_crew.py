"""Documentation crew for generating comprehensive project documentation."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama

class DocumentationCrew:
    """CrewAI-based documentation crew for generating comprehensive project docs."""
    
    def __init__(self):
        from config import get_ollama_config
        ollama_config = get_ollama_config()
        self.llm = Ollama(model=ollama_config["model"], base_url=ollama_config["base_url"])
    
    def generate_documentation(self, project_data: dict, analysis: str, code_content: str, tests: str) -> dict:
        """Generate comprehensive documentation for the project."""
        
        # Documentation Agent
        doc_agent = Agent(
            role="Technical Writer",
            goal="Create comprehensive, user-friendly documentation",
            backstory="Expert technical writer specializing in software documentation, API docs, and user guides",
            llm=self.llm,
            verbose=True
        )
        
        # Documentation Review Agent
        review_agent = Agent(
            role="Documentation Reviewer",
            goal="Ensure documentation quality and completeness",
            backstory="Senior developer and documentation expert focused on clarity, accuracy, and usability",
            llm=self.llm,
            verbose=True
        )
        
        # Documentation Generation Task
        doc_task = Task(
            description=f"""
            Generate comprehensive documentation for the project: {project_data.get('project_name', 'Unknown')}
            
            Project Details:
            - Description: {project_data.get('description', '')}
            - Features: {project_data.get('features', [])}
            - Target Users: {project_data.get('target_users', '')}
            - Scale: {project_data.get('scale', '')}
            
            Analysis: {analysis[:1000]}...
            Code: {code_content[:1000]}...
            Tests: {tests[:500]}...
            
            Create:
            1. README.md with project overview, installation, usage
            2. API documentation (if applicable)
            3. User guide with examples
            4. Developer guide for contributors
            5. Architecture documentation
            6. Deployment guide
            7. Troubleshooting guide
            
            Use clear markdown formatting with code examples.
            """,
            agent=doc_agent,
            expected_output="Complete documentation suite with README, guides, and technical documentation"
        )
        
        # Documentation Review Task
        review_task = Task(
            description="""
            Review and improve the generated documentation:
            
            1. Check for clarity and completeness
            2. Verify code examples work correctly
            3. Ensure proper markdown formatting
            4. Add missing sections or details
            5. Improve organization and flow
            
            Provide final polished documentation.
            """,
            agent=review_agent,
            expected_output="Reviewed and improved documentation with enhanced clarity and completeness"
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