"""Development crew using CrewAI and Ollama for code generation."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
import logging
from config import get_ollama_config

logger = logging.getLogger(__name__)

class DevelopmentCrew:
    """CrewAI-based development crew for code generation."""
    
    def __init__(self):
        ollama_config = get_ollama_config()
        self.llm = Ollama(model=ollama_config["model"], base_url=ollama_config["base_url"])
        self.crew = self._create_crew()
    
    def _create_crew(self) -> Crew:
        """Create the development crew with agents and tasks."""
        
        # Coding Agent
        coding_agent = Agent(
            role="Senior Software Developer",
            goal="Generate high-quality, production-ready code based on approved architecture",
            backstory="You are an expert developer with 10+ years of experience in multiple programming languages and frameworks.",
            llm=self.llm,
            verbose=True
        )
        
        # Code Review Agent
        review_agent = Agent(
            role="Code Reviewer",
            goal="Review generated code for quality, security, and best practices",
            backstory="You are a senior code reviewer who ensures code quality, security, and maintainability standards.",
            llm=self.llm,
            verbose=True
        )
        
        return Crew(
            agents=[coding_agent, review_agent],
            tasks=[],
            verbose=True
        )
    
    def generate_code(self, project: dict, analysis: str) -> dict:
        """Generate code based on approved analysis."""
        try:
            # Create coding task
            coding_task = Task(
                description=f"""
                Generate complete, production-ready code based on this approved analysis:
                
                PROJECT: {project.get('project_name', 'Unknown')}
                ANALYSIS: {analysis}
                
                Requirements:
                - {project.get('description', 'No description')}
                - Target Users: {project.get('target_users', 'Not specified')}
                - Scale: {project.get('scale', 'Not specified')}
                - Features: {', '.join(project.get('features', []))}
                - Constraints: {project.get('constraints', 'None specified')}
                
                Generate:
                1. Main application code
                2. Configuration files
                3. Requirements/dependencies
                4. README with setup instructions
                5. Basic error handling
                
                Follow the technology stack and architecture from the analysis.
                """,
                agent=self.crew.agents[0],
                expected_output="Complete codebase with all necessary files"
            )
            
            # Create review task
            review_task = Task(
                description="""
                Review the generated code and provide:
                1. Code quality assessment
                2. Security vulnerability check
                3. Best practices validation
                4. Performance considerations
                5. Improvement suggestions
                
                Ensure the code is production-ready and follows industry standards.
                """,
                agent=self.crew.agents[1],
                expected_output="Code review report with quality assessment"
            )
            
            # Update crew with tasks
            self.crew.tasks = [coding_task, review_task]
            
            # Execute the crew
            result = self.crew.kickoff()
            
            logger.info("Development crew completed successfully")
            return {
                "code": str(result),
                "status": "completed",
                "files_generated": self._extract_files(str(result))
            }
            
        except Exception as e:
            logger.error(f"Development crew failed: {str(e)}")
            return {
                "code": f"Code generation failed: {str(e)}",
                "status": "failed",
                "files_generated": []
            }
    
    def _extract_files(self, code_output: str) -> list:
        """Extract file names from generated code output."""
        import re
        
        # Look for file patterns in the output
        file_patterns = [
            r'```(\w+)\s*#\s*(\S+\.[\w]+)',  # ```python # main.py
            r'File:\s*(\S+\.[\w]+)',         # File: main.py
            r'(\S+\.[\w]+):',                # main.py:
        ]
        
        files = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, code_output)
            for match in matches:
                if isinstance(match, tuple):
                    files.add(match[-1])  # Get the filename part
                else:
                    files.add(match)
        
        return list(files)