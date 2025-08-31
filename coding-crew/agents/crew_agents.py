"""CrewAI agent definitions for the coding crew system."""

import os
from crewai import Agent
from core.llm_config import get_analysis_llm, get_coding_llm, get_review_llm, get_testing_llm, get_documentation_llm

# Configure environment for CrewAI + Ollama
os.environ["OPENAI_API_KEY"] = "sk-fake-key-for-ollama"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"


def create_analysis_agent() -> Agent:
    """Create analysis agent for requirements parsing and architecture design."""
    return Agent(
        role='Requirements Analyst & System Architect',
        goal='Parse markdown requirements and create comprehensive system architecture with aesthetic diagrams',
        backstory="""You are an expert system architect with 15+ years of experience in software design.
        You excel at understanding complex requirements and translating them into clear, actionable system designs.
        You create beautiful, professional diagrams that stakeholders love to review.""",
        verbose=True,
        allow_delegation=False,
        llm=get_analysis_llm(),
        max_iter=5
    )


def create_architecture_review_agent() -> Agent:
    """Create architecture review agent for reviewing and refining designs."""
    return Agent(
        role='Senior Architecture Reviewer',
        goal='Review system architecture and provide constructive feedback for improvements',
        backstory="""You are a senior technical architect who specializes in reviewing system designs.
        You have a keen eye for potential issues, scalability concerns, and design improvements.
        You provide clear, actionable feedback that helps create robust, maintainable systems.""",
        verbose=True,
        allow_delegation=False,
        llm=get_review_llm(),
        max_iter=5
    )


def create_coding_agent() -> Agent:
    """Create coding agent for generating code from architecture."""
    return Agent(
        role='Senior Software Developer',
        goal='Generate high-quality, well-structured code based on approved architecture designs',
        backstory="""You are a senior software developer with expertise in multiple programming languages.
        You write clean, maintainable code following best practices and design patterns.
        You pay attention to performance, security, and code quality standards.""",
        verbose=True,
        allow_delegation=False,
        llm=get_coding_llm(),
        max_iter=5
    )


def create_code_review_agent() -> Agent:
    """Create code review agent for reviewing and improving code quality."""
    return Agent(
        role='Code Quality Specialist',
        goal='Review code for quality, security, performance, and maintainability issues',
        backstory="""You are a code quality specialist who ensures all code meets high standards.
        You identify potential bugs, security vulnerabilities, performance issues, and maintainability concerns.
        You provide specific, actionable feedback to improve code quality.""",
        verbose=True,
        allow_delegation=False,
        llm=get_review_llm(),
        max_iter=5
    )


def create_unit_test_agent() -> Agent:
    """Create unit test agent for generating comprehensive test cases."""
    return Agent(
        role='Test Automation Specialist',
        goal='Generate comprehensive unit tests and identify code issues through testing',
        backstory="""You are a test automation specialist who creates thorough test suites.
        You understand testing best practices, edge cases, and how to achieve high code coverage.
        You write clear, maintainable tests that catch bugs and ensure code reliability.""",
        verbose=True,
        allow_delegation=False,
        llm=get_testing_llm(),
        max_iter=5
    )


def create_documentation_agent() -> Agent:
    """Create documentation agent for generating comprehensive documentation."""
    return Agent(
        role='Technical Documentation Specialist',
        goal='Create comprehensive, clear documentation for the entire system',
        backstory="""You are a technical writer who creates excellent documentation.
        You understand how to explain complex technical concepts clearly and create documentation
        that helps developers, users, and stakeholders understand and use the system effectively.""",
        verbose=True,
        allow_delegation=False,
        llm=get_documentation_llm(),
        max_iter=1
    )