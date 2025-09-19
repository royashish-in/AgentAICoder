"""Context-aware intelligent test generation."""

from crewai import Agent, Task, Crew
from typing import Dict, List, Any
from loguru import logger


class IntelligentTestGenerator:
    """AI agent for context-aware test case generation."""
    
    def __init__(self):
        from core.llm_config import get_analysis_llm
        self.llm = get_analysis_llm()
        self.crew = self._create_crew()
    
    def _create_crew(self) -> Crew:
        """Create intelligent test generation crew."""
        
        test_engineer = Agent(
            role="Senior Test Engineer",
            goal="Generate comprehensive, context-aware test cases that ensure code quality and functionality",
            backstory="You are an expert test engineer with deep knowledge of testing strategies, edge cases, and quality assurance best practices across multiple technologies.",
            llm=self.llm,
            verbose=True
        )
        
        return Crew(
            agents=[test_engineer],
            tasks=[],
            verbose=True
        )
    
    def generate_comprehensive_tests(self, code_content: str, requirements: Dict[str, Any], tech_stack: List[str]) -> Dict[str, Any]:
        """Generate comprehensive test suite based on code and requirements."""
        try:
            test_task = Task(
                description=f"""
                Generate a comprehensive test suite for the following code:
                
                Technology Stack: {', '.join(tech_stack)}
                
                Requirements Context:
                - Project: {requirements.get('project_name', 'Unknown')}
                - Features: {requirements.get('features', [])}
                - Target Users: {requirements.get('target_users', 'General')}
                - Scale: {requirements.get('scale', 'Medium')}
                
                Code to Test:
                {code_content}
                
                Generate tests for:
                
                1. **Unit Tests**:
                   - Test individual functions and methods
                   - Cover all code paths and branches
                   - Test edge cases and boundary conditions
                   - Mock external dependencies
                
                2. **Integration Tests**:
                   - Test component interactions
                   - Database integration tests
                   - API endpoint tests
                   - Service integration tests
                
                3. **Functional Tests**:
                   - Test business logic requirements
                   - User workflow validation
                   - Feature completeness tests
                   - Data validation tests
                
                4. **Edge Case Tests**:
                   - Invalid input handling
                   - Error condition testing
                   - Performance boundary tests
                   - Security vulnerability tests
                
                5. **Performance Tests**:
                   - Load testing scenarios
                   - Response time validation
                   - Memory usage tests
                   - Concurrent user tests
                
                For each test category, provide:
                - Test file structure and naming
                - Complete test code with assertions
                - Test data setup and teardown
                - Expected outcomes and validation
                
                Use appropriate testing frameworks for the technology stack.
                Ensure tests are maintainable, readable, and comprehensive.
                """,
                agent=self.crew.agents[0],
                expected_output="Complete test suite with multiple test categories"
            )
            
            self.crew.tasks = [test_task]
            result = self.crew.kickoff()
            
            test_content = str(result)
            
            return {
                "test_content": test_content,
                "test_files": self._extract_test_files(test_content),
                "coverage_analysis": self._analyze_coverage(test_content, code_content),
                "test_categories": self._categorize_tests(test_content)
            }
            
        except Exception as e:
            logger.error(f"Intelligent test generation failed: {e}")
            return {
                "test_content": f"Test generation failed: {str(e)}",
                "test_files": [],
                "coverage_analysis": {"estimated_coverage": 0},
                "test_categories": []
            }
    
    def generate_security_tests(self, code_content: str, tech_stack: List[str]) -> Dict[str, Any]:
        """Generate security-focused test cases."""
        try:
            security_task = Task(
                description=f"""
                Generate security-focused test cases for the following code:
                
                Technology Stack: {', '.join(tech_stack)}
                
                Code:
                {code_content}
                
                Generate security tests for:
                
                1. **Input Validation Tests**:
                   - SQL injection attempts
                   - XSS payload testing
                   - Command injection tests
                   - Path traversal attempts
                
                2. **Authentication Tests**:
                   - Invalid credential handling
                   - Session management tests
                   - Token validation tests
                   - Privilege escalation attempts
                
                3. **Authorization Tests**:
                   - Access control validation
                   - Role-based permission tests
                   - Resource access restrictions
                   - API endpoint security
                
                4. **Data Security Tests**:
                   - Sensitive data exposure
                   - Encryption validation
                   - Data sanitization tests
                   - Privacy compliance tests
                
                Provide complete test code with security-specific assertions and validation.
                """,
                agent=self.crew.agents[0],
                expected_output="Security-focused test suite"
            )
            
            self.crew.tasks = [security_task]
            result = self.crew.kickoff()
            
            return {
                "security_tests": str(result),
                "security_categories": self._extract_security_categories(str(result))
            }
            
        except Exception as e:
            logger.error(f"Security test generation failed: {e}")
            return {
                "security_tests": f"Security test generation failed: {str(e)}",
                "security_categories": []
            }
    
    def analyze_test_coverage(self, test_content: str, code_content: str) -> Dict[str, Any]:
        """Analyze test coverage and suggest improvements."""
        try:
            coverage_task = Task(
                description=f"""
                Analyze test coverage for the following code and tests:
                
                Code:
                {code_content[:2000]}...
                
                Tests:
                {test_content[:2000]}...
                
                Provide coverage analysis:
                1. **Function Coverage**: Which functions are tested vs untested
                2. **Branch Coverage**: Which code paths are covered
                3. **Edge Case Coverage**: Missing edge case tests
                4. **Integration Coverage**: Missing integration tests
                5. **Coverage Gaps**: Specific areas needing more tests
                
                Suggest additional tests to improve coverage.
                Estimate overall coverage percentage.
                """,
                agent=self.crew.agents[0],
                expected_output="Test coverage analysis with improvement suggestions"
            )
            
            self.crew.tasks = [coverage_task]
            result = self.crew.kickoff()
            
            return {
                "coverage_report": str(result),
                "coverage_percentage": self._estimate_coverage(str(result)),
                "missing_tests": self._extract_missing_tests(str(result))
            }
            
        except Exception as e:
            logger.error(f"Coverage analysis failed: {e}")
            return {
                "coverage_report": f"Coverage analysis failed: {str(e)}",
                "coverage_percentage": 0,
                "missing_tests": []
            }
    
    def _extract_test_files(self, test_content: str) -> List[Dict[str, str]]:
        """Extract test files from generated content."""
        import re
        
        files = []
        # Look for file patterns
        file_patterns = [
            r'```(?:python|javascript|java|typescript)\s*#?\s*([^`\n]+\.(?:py|js|java|ts))\s*\n(.*?)```',
            r'File:\s*([^`\n]+\.(?:py|js|java|ts))\s*\n```[^`]*\n(.*?)```'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, test_content, re.DOTALL)
            for filename, content in matches:
                files.append({
                    "filename": filename.strip(),
                    "content": content.strip(),
                    "type": "test"
                })
        
        return files[:10]  # Limit to 10 files
    
    def _analyze_coverage(self, test_content: str, code_content: str) -> Dict[str, Any]:
        """Analyze test coverage."""
        # Simple heuristic-based coverage analysis
        test_functions = len(re.findall(r'def test_|it\(|test\(', test_content, re.IGNORECASE))
        code_functions = len(re.findall(r'def |function |class ', code_content, re.IGNORECASE))
        
        estimated_coverage = min(100, (test_functions / max(1, code_functions)) * 80)
        
        return {
            "estimated_coverage": int(estimated_coverage),
            "test_functions": test_functions,
            "code_functions": code_functions,
            "coverage_quality": "Good" if estimated_coverage > 70 else "Needs Improvement"
        }
    
    def _categorize_tests(self, test_content: str) -> List[Dict[str, Any]]:
        """Categorize generated tests."""
        categories = []
        content_lower = test_content.lower()
        
        if 'unit test' in content_lower or 'def test_' in content_lower:
            categories.append({"type": "Unit Tests", "count": content_lower.count('def test_')})
        
        if 'integration test' in content_lower:
            categories.append({"type": "Integration Tests", "count": content_lower.count('integration')})
        
        if 'performance test' in content_lower or 'load test' in content_lower:
            categories.append({"type": "Performance Tests", "count": content_lower.count('performance')})
        
        if 'security test' in content_lower:
            categories.append({"type": "Security Tests", "count": content_lower.count('security')})
        
        return categories
    
    def _extract_security_categories(self, security_content: str) -> List[str]:
        """Extract security test categories."""
        categories = []
        content_lower = security_content.lower()
        
        if 'sql injection' in content_lower:
            categories.append("SQL Injection Tests")
        if 'xss' in content_lower or 'cross-site' in content_lower:
            categories.append("XSS Tests")
        if 'authentication' in content_lower:
            categories.append("Authentication Tests")
        if 'authorization' in content_lower:
            categories.append("Authorization Tests")
        
        return categories
    
    def _estimate_coverage(self, coverage_report: str) -> int:
        """Extract coverage percentage from report."""
        import re
        
        # Look for percentage patterns
        percentages = re.findall(r'(\d+)%', coverage_report)
        if percentages:
            return int(percentages[0])
        
        # Heuristic based on content
        if 'excellent' in coverage_report.lower():
            return 90
        elif 'good' in coverage_report.lower():
            return 75
        elif 'adequate' in coverage_report.lower():
            return 60
        else:
            return 45
    
    def _extract_missing_tests(self, coverage_report: str) -> List[str]:
        """Extract missing test suggestions."""
        import re
        
        missing = []
        lines = coverage_report.split('\n')
        
        for line in lines:
            if 'missing' in line.lower() or 'need' in line.lower() or 'should test' in line.lower():
                cleaned = line.strip('- *').strip()
                if cleaned and len(cleaned) > 10:
                    missing.append(cleaned)
        
        return missing[:5]  # Top 5 missing tests