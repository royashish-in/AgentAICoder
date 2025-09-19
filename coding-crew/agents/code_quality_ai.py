"""AI-powered code review and optimization suggestions."""

from crewai import Agent, Task, Crew
from typing import Dict, List, Any
from loguru import logger


class CodeQualityAI:
    """AI agent for automated code review and quality suggestions."""
    
    def __init__(self):
        from core.llm_config import get_analysis_llm
        self.llm = get_analysis_llm()
        self.crew = self._create_crew()
    
    def _create_crew(self) -> Crew:
        """Create code quality review crew."""
        
        code_reviewer = Agent(
            role="Senior Code Reviewer",
            goal="Analyze code for quality issues, security vulnerabilities, and optimization opportunities",
            backstory="You are an expert code reviewer with 15+ years of experience in software engineering best practices, security, and performance optimization.",
            llm=self.llm,
            verbose=True
        )
        
        return Crew(
            agents=[code_reviewer],
            tasks=[],
            verbose=True
        )
    
    def review_code(self, code_content: str, tech_stack: List[str]) -> Dict[str, Any]:
        """Perform comprehensive code review."""
        try:
            review_task = Task(
                description=f"""
                Perform a comprehensive code review of the following code:
                
                Technology Stack: {', '.join(tech_stack)}
                
                Code to Review:
                {code_content}
                
                Analyze for:
                1. **Code Quality Issues**:
                   - Naming conventions and readability
                   - Function/class complexity
                   - Code duplication
                   - Dead code or unused imports
                
                2. **Security Vulnerabilities**:
                   - Input validation issues
                   - SQL injection risks
                   - XSS vulnerabilities
                   - Authentication/authorization flaws
                
                3. **Performance Optimizations**:
                   - Inefficient algorithms or loops
                   - Database query optimization
                   - Memory usage improvements
                   - Caching opportunities
                
                4. **Best Practices**:
                   - Design patterns usage
                   - Error handling
                   - Logging and monitoring
                   - Documentation quality
                
                5. **Maintainability**:
                   - Code organization
                   - Separation of concerns
                   - Testability
                   - Configuration management
                
                Provide specific, actionable recommendations with code examples where applicable.
                Format as structured analysis with severity levels (Critical, High, Medium, Low).
                """,
                agent=self.crew.agents[0],
                expected_output="Detailed code quality analysis with specific recommendations"
            )
            
            self.crew.tasks = [review_task]
            result = self.crew.kickoff()
            
            return {
                "review_content": str(result),
                "issues_found": self._extract_issues(str(result)),
                "recommendations": self._extract_recommendations(str(result)),
                "quality_score": self._calculate_quality_score(str(result))
            }
            
        except Exception as e:
            logger.error(f"Code quality review failed: {e}")
            return {
                "review_content": f"Code review failed: {str(e)}",
                "issues_found": [],
                "recommendations": [],
                "quality_score": 0
            }
    
    def suggest_optimizations(self, code_content: str, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest specific code optimizations based on performance data."""
        try:
            optimization_task = Task(
                description=f"""
                Analyze the following code for performance optimizations:
                
                Code:
                {code_content}
                
                Performance Metrics:
                {performance_metrics}
                
                Provide specific optimization suggestions:
                1. **Algorithm Improvements**: More efficient algorithms or data structures
                2. **Database Optimizations**: Query improvements, indexing suggestions
                3. **Caching Strategies**: Where and how to implement caching
                4. **Memory Optimizations**: Reduce memory usage and garbage collection
                5. **Concurrency Improvements**: Async/await, threading, or parallel processing
                
                For each suggestion, provide:
                - Current issue description
                - Proposed solution with code example
                - Expected performance improvement
                - Implementation complexity (Low/Medium/High)
                """,
                agent=self.crew.agents[0],
                expected_output="Specific performance optimization recommendations"
            )
            
            self.crew.tasks = [optimization_task]
            result = self.crew.kickoff()
            
            return {
                "optimization_content": str(result),
                "optimizations": self._extract_optimizations(str(result))
            }
            
        except Exception as e:
            logger.error(f"Code optimization analysis failed: {e}")
            return {
                "optimization_content": f"Optimization analysis failed: {str(e)}",
                "optimizations": []
            }
    
    def _extract_issues(self, review_content: str) -> List[Dict[str, Any]]:
        """Extract structured issues from review content."""
        import re
        
        issues = []
        # Look for severity patterns
        severity_patterns = [
            (r'Critical[:\s]+(.*?)(?=High|Medium|Low|$)', 'Critical'),
            (r'High[:\s]+(.*?)(?=Critical|Medium|Low|$)', 'High'),
            (r'Medium[:\s]+(.*?)(?=Critical|High|Low|$)', 'Medium'),
            (r'Low[:\s]+(.*?)(?=Critical|High|Medium|$)', 'Low')
        ]
        
        for pattern, severity in severity_patterns:
            matches = re.findall(pattern, review_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if match.strip():
                    issues.append({
                        "severity": severity,
                        "description": match.strip()[:200] + "..." if len(match.strip()) > 200 else match.strip(),
                        "category": "code_quality"
                    })
        
        return issues[:10]  # Limit to top 10 issues
    
    def _extract_recommendations(self, review_content: str) -> List[str]:
        """Extract actionable recommendations."""
        import re
        
        # Look for recommendation patterns
        rec_patterns = [
            r'Recommendation[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'Suggest[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'Should[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)'
        ]
        
        recommendations = []
        for pattern in rec_patterns:
            matches = re.findall(pattern, review_content, re.DOTALL | re.IGNORECASE)
            recommendations.extend([match.strip() for match in matches if match.strip()])
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _extract_optimizations(self, optimization_content: str) -> List[Dict[str, Any]]:
        """Extract structured optimizations."""
        import re
        
        optimizations = []
        # Simple pattern matching for optimization suggestions
        lines = optimization_content.split('\n')
        current_opt = {}
        
        for line in lines:
            line = line.strip()
            if 'optimization' in line.lower() or 'improvement' in line.lower():
                if current_opt:
                    optimizations.append(current_opt)
                current_opt = {
                    "title": line,
                    "description": "",
                    "complexity": "Medium"
                }
            elif current_opt and line:
                current_opt["description"] += line + " "
                if 'low complexity' in line.lower():
                    current_opt["complexity"] = "Low"
                elif 'high complexity' in line.lower():
                    current_opt["complexity"] = "High"
        
        if current_opt:
            optimizations.append(current_opt)
        
        return optimizations[:5]  # Top 5 optimizations
    
    def _calculate_quality_score(self, review_content: str) -> int:
        """Calculate overall code quality score (0-100)."""
        content_lower = review_content.lower()
        
        # Deduct points for issues
        score = 100
        score -= content_lower.count('critical') * 20
        score -= content_lower.count('high') * 10
        score -= content_lower.count('medium') * 5
        score -= content_lower.count('low') * 2
        
        # Add points for good practices mentioned
        score += content_lower.count('good') * 2
        score += content_lower.count('excellent') * 3
        score += content_lower.count('well') * 1
        
        return max(0, min(100, score))