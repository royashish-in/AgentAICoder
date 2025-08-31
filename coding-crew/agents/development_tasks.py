"""Development phase tasks for code generation and review."""

from crewai import Task

def create_coding_task(analysis_result: str):
    """Create coding task based on approved analysis."""
    return Task(
        description=f"""
        Generate complete, production-ready code based on the approved system analysis:
        
        {analysis_result}
        
        Requirements:
        1. Implement all components identified in the analysis
        2. Follow the recommended technology stack
        3. Include proper error handling and validation
        4. Add comprehensive docstrings and comments
        5. Implement security best practices
        6. Ensure code is modular and maintainable
        7. Include configuration management
        8. Add logging and monitoring hooks
        
        Deliverables:
        - Complete source code files
        - Configuration files
        - Database schemas (if applicable)
        - API documentation
        - Installation/setup instructions
        """,
        expected_output="""Complete codebase with:
        - All source files with proper structure
        - Configuration and environment files
        - Database migration scripts
        - API endpoint implementations
        - Documentation and setup guides
        - Security implementations
        - Error handling and logging"""
    )

def create_code_review_task():
    """Create code review task for quality assurance."""
    return Task(
        description="""
        Perform comprehensive code review of the generated codebase:
        
        Review Areas:
        1. **Code Quality**: Structure, readability, maintainability
        2. **Security**: Vulnerabilities, input validation, authentication
        3. **Performance**: Efficiency, scalability, resource usage
        4. **Best Practices**: Design patterns, conventions, standards
        5. **Testing**: Test coverage, test quality, edge cases
        6. **Documentation**: Code comments, API docs, setup guides
        7. **Error Handling**: Exception management, graceful failures
        8. **Configuration**: Environment management, secrets handling
        
        Provide specific feedback with:
        - Issues found with severity levels
        - Recommended improvements
        - Code examples for fixes
        - Performance optimization suggestions
        """,
        expected_output="""Detailed code review report with:
        - Executive summary of code quality
        - Categorized issues (Critical/High/Medium/Low)
        - Specific recommendations for each issue
        - Code improvement examples
        - Security assessment
        - Performance analysis
        - Overall quality score and approval status"""
    )