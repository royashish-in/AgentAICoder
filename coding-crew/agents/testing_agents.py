"""Testing phase agents for test generation and execution."""

from crewai import Agent
from core.llm_config import get_llm_config

def create_unit_test_agent():
    """Create unit test agent for test generation."""
    llm_config = get_llm_config()
    
    return Agent(
        role="Senior Test Engineer & QA Specialist",
        goal="Generate comprehensive unit tests with high coverage and quality validation",
        backstory="""You are an expert test engineer with deep knowledge of testing 
        frameworks, test-driven development, and quality assurance. You excel at 
        creating thorough test suites that catch edge cases and ensure code reliability.""",
        verbose=True,
        allow_delegation=False,
        llm=llm_config["testing"]
    )

def create_test_execution_agent():
    """Create test execution agent for running and validating tests."""
    llm_config = get_llm_config()
    
    return Agent(
        role="Test Automation Engineer",
        goal="Execute tests, analyze results, and generate comprehensive test reports",
        backstory="""You are a test automation specialist who ensures all tests run 
        correctly, analyzes test coverage, and provides detailed reports on test 
        results and code quality metrics.""",
        verbose=True,
        allow_delegation=False,
        llm=llm_config["testing"]
    )