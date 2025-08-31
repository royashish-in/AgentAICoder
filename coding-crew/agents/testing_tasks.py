"""Testing phase tasks for test generation and execution."""

from crewai import Task

def create_unit_test_task(code_result: str):
    """Create unit test generation task."""
    return Task(
        description=f"""
        Generate comprehensive unit tests for the provided codebase:
        
        {code_result}
        
        Requirements:
        1. **Test Coverage**: Aim for 80%+ code coverage
        2. **Test Types**: Unit, integration, edge cases, error conditions
        3. **Test Framework**: Use appropriate framework (pytest, unittest, jest, etc.)
        4. **Test Structure**: Organize tests logically with clear naming
        5. **Mocking**: Mock external dependencies and services
        6. **Assertions**: Comprehensive assertions for all scenarios
        7. **Test Data**: Create realistic test fixtures and data
        8. **Performance Tests**: Include basic performance validation
        
        Generate tests for:
        - All public methods and functions
        - Error handling and edge cases
        - Input validation and sanitization
        - Business logic and calculations
        - API endpoints and responses
        - Database operations (if applicable)
        - Authentication and authorization
        - Configuration and environment handling
        """,
        expected_output="""Complete test suite including:
        - Test files organized by module/component
        - Unit tests with high coverage
        - Integration tests for key workflows
        - Mock configurations and test fixtures
        - Test configuration files (pytest.ini, etc.)
        - Performance and load test basics
        - Test documentation and setup instructions"""
    )

def create_test_execution_task():
    """Create test execution and reporting task."""
    return Task(
        description="""
        Execute the generated test suite and provide comprehensive analysis:
        
        Execution Requirements:
        1. **Run All Tests**: Execute unit, integration, and performance tests
        2. **Coverage Analysis**: Generate detailed coverage reports
        3. **Performance Metrics**: Measure test execution time and performance
        4. **Error Analysis**: Identify and categorize any test failures
        5. **Quality Metrics**: Calculate code quality scores
        6. **Recommendations**: Suggest improvements for test coverage gaps
        
        Report Generation:
        - Test execution summary (passed/failed/skipped)
        - Code coverage percentage by module
        - Performance benchmarks and timing
        - Failed test analysis with root causes
        - Quality assessment and recommendations
        - Test maintenance suggestions
        """,
        expected_output="""Comprehensive test report containing:
        - Executive summary of test results
        - Detailed coverage report (line, branch, function coverage)
        - Performance metrics and benchmarks
        - Failed test analysis and recommendations
        - Code quality assessment
        - Suggestions for improving test coverage
        - Test maintenance and optimization recommendations"""
    )