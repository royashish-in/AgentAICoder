"""CrewAI task definitions for the coding crew workflow."""

from crewai import Task
from typing import Dict, Any


def create_analysis_task(requirements: str) -> Task:
    """Create analysis task for requirements parsing."""
    from core.diagram_prompts import get_analysis_prompt_with_diagrams
    
    return Task(
        description=get_analysis_prompt_with_diagrams(requirements),
        expected_output="""
        A comprehensive analysis document in markdown format containing:
        - Executive summary
        - Detailed requirements breakdown
        - System architecture design
        - Component specifications
        - Technology recommendations
        - Professional draw.io XML diagrams embedded in the document
        """,
        output_file="analysis_output.md"
    )


def create_architecture_review_task() -> Task:
    """Create architecture review task."""
    from core.diagram_prompts import get_review_prompt_with_diagram_feedback
    
    return Task(
        description=get_review_prompt_with_diagram_feedback(),
        expected_output="""
        An architecture review report containing:
        - Overall assessment and rating
        - Detailed feedback on each component
        - Security and scalability analysis
        - Diagram quality assessment
        - Specific improvement recommendations
        - Refined diagrams (if applicable)
        """,
        output_file="architecture_review.md"
    )


def create_coding_task() -> Task:
    """Create coding task for implementation."""
    return Task(
        description="""
        Generate high-quality code based on the approved architecture design:
        
        1. Implement core components and modules
        2. Follow best practices and design patterns
        3. Include proper error handling and logging
        4. Ensure code is well-structured and maintainable
        5. Add appropriate comments and docstrings
        6. Follow the technology stack recommendations
        
        Focus on:
        - Clean, readable code
        - Proper separation of concerns
        - Security best practices
        - Performance optimization
        """,
        expected_output="""
        Complete code implementation including:
        - All core modules and components
        - Configuration files
        - Database schemas (if applicable)
        - API endpoints (if applicable)
        - Proper project structure
        - Installation and setup instructions
        """,
        output_file="generated_code/"
    )


def create_code_review_task() -> Task:
    """Create code review task."""
    return Task(
        description="""
        Conduct a thorough code review of the generated implementation:
        
        1. Review code quality and adherence to best practices
        2. Identify potential bugs, security vulnerabilities, and performance issues
        3. Check for proper error handling and edge cases
        4. Evaluate code structure and maintainability
        5. Verify compliance with coding standards
        6. Suggest specific improvements and optimizations
        
        Provide detailed feedback on:
        - Code organization and structure
        - Security considerations
        - Performance optimizations
        - Error handling
        - Documentation quality
        """,
        expected_output="""
        A comprehensive code review report containing:
        - Overall code quality assessment
        - Detailed findings by category (bugs, security, performance)
        - Specific line-by-line feedback
        - Improvement recommendations
        - Priority levels for each issue
        - Refactoring suggestions
        """,
        output_file="code_review_report.md"
    )


def create_unit_test_task() -> Task:
    """Create unit testing task."""
    return Task(
        description="""
        Generate comprehensive unit tests for the implemented code:
        
        1. Create test cases for all major functions and methods
        2. Include edge cases and error scenarios
        3. Aim for high code coverage (90%+)
        4. Write clear, maintainable test code
        5. Include integration tests where appropriate
        6. Generate test reports and coverage analysis
        
        Focus on:
        - Comprehensive test coverage
        - Clear test descriptions
        - Proper test data setup
        - Assertion clarity
        - Test maintainability
        """,
        expected_output="""
        Complete test suite including:
        - Unit tests for all components
        - Integration tests
        - Test configuration files
        - Test data and fixtures
        - Coverage reports
        - Test execution instructions
        """,
        output_file="tests/"
    )


def create_documentation_task() -> Task:
    """Create documentation task."""
    return Task(
        description="""
        Create comprehensive documentation for the entire system:
        
        1. Generate user documentation and guides
        2. Create technical documentation for developers
        3. Include API documentation (if applicable)
        4. Add installation and deployment guides
        5. Include troubleshooting and FAQ sections
        6. Embed the aesthetic diagrams from the analysis phase
        
        Documentation should include:
        - README with quick start guide
        - Detailed user manual
        - Developer documentation
        - API reference
        - Architecture documentation with diagrams
        - Deployment and maintenance guides
        """,
        expected_output="""
        Complete documentation suite including:
        - README.md with project overview
        - User guide and tutorials
        - Technical documentation
        - API documentation
        - Installation and deployment guides
        - Architecture documentation with embedded diagrams
        - Troubleshooting guides
        """,
        output_file="documentation/"
    )