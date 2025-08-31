"""Documentation phase tasks."""

from crewai import Task

def create_documentation_task(code_result: str, test_result: str):
    """Create documentation generation task."""
    return Task(
        description=f"""
        Generate comprehensive project documentation based on:
        
        Code: {code_result[:500]}...
        Tests: {test_result[:500]}...
        
        Create:
        1. **README.md**: Project overview, setup, usage
        2. **API Documentation**: Endpoint specs and examples  
        3. **User Guide**: Installation and usage instructions
        4. **Developer Guide**: Architecture and contribution guidelines
        5. **Deployment Guide**: Production deployment instructions
        """,
        expected_output="""Complete documentation package:
        - README.md with project overview
        - API documentation with examples
        - User installation and usage guide
        - Developer setup and architecture guide
        - Deployment and production guide"""
    )