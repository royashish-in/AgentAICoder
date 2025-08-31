"""Testing crew for generating comprehensive test suites."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama

class TestingCrew:
    """CrewAI-based testing crew for generating comprehensive test suites."""
    
    def __init__(self):
        from config import get_ollama_config
        ollama_config = get_ollama_config()
        self.llm = Ollama(model=ollama_config["model"], base_url=ollama_config["base_url"])
    
    def generate_tests(self, project_data: dict, code_content: str) -> dict:
        """Generate comprehensive test suite for the project."""
        
        # Test Generation Agent
        test_agent = Agent(
            role="Senior Test Engineer",
            goal="Generate comprehensive test suites with high coverage",
            backstory="Expert in test-driven development, unit testing, integration testing, and test automation",
            llm=self.llm,
            verbose=True
        )
        
        # Test Review Agent
        review_agent = Agent(
            role="QA Lead",
            goal="Review and improve test quality and coverage",
            backstory="Quality assurance expert focused on test completeness, edge cases, and maintainability",
            llm=self.llm,
            verbose=True
        )
        
        # Test Generation Task
        test_task = Task(
            description=f"""
            Generate comprehensive test suite for the project: {project_data.get('project_name', 'Unknown')}
            
            Project Description: {project_data.get('description', '')}
            Generated Code: {code_content[:2000]}...
            
            Create:
            1. Unit tests for all functions and classes
            2. Integration tests for component interactions
            3. Edge case and error handling tests
            4. Performance tests where applicable
            5. Test fixtures and mock data
            
            Use pytest framework and include:
            - Test file structure
            - Setup and teardown methods
            - Parameterized tests
            - Assertions and validations
            - Test documentation
            """,
            agent=test_agent,
            expected_output="Complete test suite with multiple test files, fixtures, and comprehensive coverage"
        )
        
        # Test Review Task
        review_task = Task(
            description="""
            Review the generated test suite and provide improvements:
            
            1. Verify test coverage completeness
            2. Check for missing edge cases
            3. Validate test structure and organization
            4. Suggest performance test improvements
            5. Ensure test maintainability
            
            Provide final optimized test suite.
            """,
            agent=review_agent,
            expected_output="Reviewed and improved test suite with coverage analysis and recommendations"
        )
        
        # Create and run crew
        crew = Crew(
            agents=[test_agent, review_agent],
            tasks=[test_task, review_task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        return {
            "tests": str(result),
            "test_files": self._extract_test_files(str(result))
        }
    
    def _extract_test_files(self, content: str) -> list:
        """Extract test file names from generated content."""
        import re
        
        patterns = [
            r'test_[a-zA-Z_]+\.py',
            r'[a-zA-Z_]+_test\.py',
            r'conftest\.py'
        ]
        
        files = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            files.extend(matches)
        
        return list(set(files))