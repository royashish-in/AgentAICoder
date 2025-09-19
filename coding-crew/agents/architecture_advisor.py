"""AI architecture advisor for system design recommendations."""

from crewai import Agent, Task, Crew
from typing import Dict, List, Any
from loguru import logger


class ArchitectureAdvisor:
    """AI agent for system architecture analysis and recommendations."""
    
    def __init__(self):
        from core.llm_config import get_analysis_llm
        self.llm = get_analysis_llm()
        self.crew = self._create_crew()
    
    def _create_crew(self) -> Crew:
        """Create architecture advisory crew."""
        
        architect = Agent(
            role="Senior Software Architect",
            goal="Analyze system architecture and provide expert recommendations for scalability, maintainability, and best practices",
            backstory="You are a distinguished software architect with 20+ years of experience designing large-scale systems, microservices, and distributed architectures across various industries.",
            llm=self.llm,
            verbose=True
        )
        
        return Crew(
            agents=[architect],
            tasks=[],
            verbose=True
        )
    
    def analyze_architecture(self, code_content: str, requirements: Dict[str, Any], tech_stack: List[str]) -> Dict[str, Any]:
        """Analyze current architecture and provide recommendations."""
        try:
            analysis_task = Task(
                description=f"""
                Analyze the system architecture based on the following information:
                
                Technology Stack: {', '.join(tech_stack)}
                
                Requirements:
                - Project: {requirements.get('project_name', 'Unknown')}
                - Scale: {requirements.get('scale', 'Medium')}
                - Target Users: {requirements.get('target_users', 'General')}
                - Features: {requirements.get('features', [])}
                
                Current Code Structure:
                {code_content[:3000]}...
                
                Provide comprehensive architecture analysis:
                
                1. **Current Architecture Assessment**:
                   - Architecture pattern identification (MVC, microservices, layered, etc.)
                   - Component organization and separation of concerns
                   - Data flow and dependency analysis
                   - Scalability bottlenecks and limitations
                
                2. **Design Pattern Recommendations**:
                   - Appropriate design patterns for the use case
                   - Anti-patterns to avoid
                   - Refactoring suggestions for better patterns
                   - Pattern implementation examples
                
                3. **Scalability Improvements**:
                   - Horizontal vs vertical scaling strategies
                   - Caching layer recommendations
                   - Database optimization suggestions
                   - Load balancing and distribution strategies
                
                4. **Security Architecture**:
                   - Security layer recommendations
                   - Authentication and authorization patterns
                   - Data protection strategies
                   - API security best practices
                
                5. **Maintainability Enhancements**:
                   - Code organization improvements
                   - Dependency management strategies
                   - Testing architecture recommendations
                   - Documentation and monitoring strategies
                
                6. **Technology Stack Optimization**:
                   - Current stack assessment
                   - Alternative technology suggestions
                   - Integration improvement recommendations
                   - Performance optimization opportunities
                
                Provide specific, actionable recommendations with implementation priorities.
                """,
                agent=self.crew.agents[0],
                expected_output="Comprehensive architecture analysis with specific recommendations"
            )
            
            self.crew.tasks = [analysis_task]
            result = self.crew.kickoff()
            
            analysis_content = str(result)
            
            return {
                "analysis_content": analysis_content,
                "architecture_score": self._calculate_architecture_score(analysis_content),
                "recommendations": self._extract_recommendations(analysis_content),
                "design_patterns": self._extract_design_patterns(analysis_content),
                "scalability_suggestions": self._extract_scalability_suggestions(analysis_content)
            }
            
        except Exception as e:
            logger.error(f"Architecture analysis failed: {e}")
            return {
                "analysis_content": f"Architecture analysis failed: {str(e)}",
                "architecture_score": 0,
                "recommendations": [],
                "design_patterns": [],
                "scalability_suggestions": []
            }
    
    def suggest_refactoring(self, code_content: str, architecture_issues: List[str]) -> Dict[str, Any]:
        """Suggest specific refactoring strategies."""
        try:
            refactoring_task = Task(
                description=f"""
                Analyze the following code for refactoring opportunities:
                
                Current Issues Identified:
                {', '.join(architecture_issues)}
                
                Code:
                {code_content[:2000]}...
                
                Provide specific refactoring recommendations:
                
                1. **Structural Refactoring**:
                   - Class and method extraction opportunities
                   - Interface segregation improvements
                   - Dependency inversion implementations
                   - Single responsibility principle violations
                
                2. **Performance Refactoring**:
                   - Algorithm optimization opportunities
                   - Data structure improvements
                   - Caching implementation strategies
                   - Database query optimizations
                
                3. **Maintainability Refactoring**:
                   - Code duplication elimination
                   - Complex method simplification
                   - Configuration externalization
                   - Error handling improvements
                
                4. **Security Refactoring**:
                   - Input validation enhancements
                   - Authentication/authorization improvements
                   - Sensitive data handling
                   - Logging and monitoring additions
                
                For each refactoring suggestion, provide:
                - Current problem description
                - Proposed solution with code examples
                - Implementation steps
                - Expected benefits
                - Risk assessment and mitigation
                """,
                agent=self.crew.agents[0],
                expected_output="Detailed refactoring recommendations with implementation guidance"
            )
            
            self.crew.tasks = [refactoring_task]
            result = self.crew.kickoff()
            
            return {
                "refactoring_content": str(result),
                "refactoring_tasks": self._extract_refactoring_tasks(str(result))
            }
            
        except Exception as e:
            logger.error(f"Refactoring analysis failed: {e}")
            return {
                "refactoring_content": f"Refactoring analysis failed: {str(e)}",
                "refactoring_tasks": []
            }
    
    def design_system_architecture(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design optimal system architecture from requirements."""
        try:
            design_task = Task(
                description=f"""
                Design an optimal system architecture based on these requirements:
                
                Project Requirements:
                - Name: {requirements.get('project_name', 'Unknown')}
                - Description: {requirements.get('description', '')}
                - Scale: {requirements.get('scale', 'Medium')}
                - Target Users: {requirements.get('target_users', 'General')}
                - Features: {requirements.get('features', [])}
                - Constraints: {requirements.get('constraints', '')}
                
                Design a comprehensive system architecture including:
                
                1. **High-Level Architecture**:
                   - Overall system design pattern
                   - Component breakdown and responsibilities
                   - Data flow and interaction patterns
                   - Deployment architecture
                
                2. **Technology Stack Recommendations**:
                   - Frontend technology choices with justification
                   - Backend framework and language selection
                   - Database technology and design
                   - Infrastructure and deployment tools
                
                3. **Scalability Design**:
                   - Horizontal scaling strategies
                   - Caching layer design
                   - Load balancing approach
                   - Database scaling considerations
                
                4. **Security Architecture**:
                   - Authentication and authorization design
                   - Data protection strategies
                   - API security implementation
                   - Monitoring and logging architecture
                
                5. **Integration Architecture**:
                   - External service integration patterns
                   - API design and versioning strategy
                   - Event-driven architecture considerations
                   - Message queue and communication patterns
                
                Provide detailed architecture diagrams in text format and implementation roadmap.
                """,
                agent=self.crew.agents[0],
                expected_output="Complete system architecture design with implementation guidance"
            )
            
            self.crew.tasks = [design_task]
            result = self.crew.kickoff()
            
            return {
                "architecture_design": str(result),
                "components": self._extract_components(str(result)),
                "tech_recommendations": self._extract_tech_recommendations(str(result)),
                "implementation_roadmap": self._extract_roadmap(str(result))
            }
            
        except Exception as e:
            logger.error(f"Architecture design failed: {e}")
            return {
                "architecture_design": f"Architecture design failed: {str(e)}",
                "components": [],
                "tech_recommendations": [],
                "implementation_roadmap": []
            }
    
    def _calculate_architecture_score(self, analysis_content: str) -> int:
        """Calculate architecture quality score."""
        content_lower = analysis_content.lower()
        
        score = 70  # Base score
        
        # Positive indicators
        score += content_lower.count('good') * 3
        score += content_lower.count('excellent') * 5
        score += content_lower.count('well-designed') * 4
        score += content_lower.count('scalable') * 3
        
        # Negative indicators
        score -= content_lower.count('poor') * 5
        score -= content_lower.count('problematic') * 4
        score -= content_lower.count('issue') * 2
        score -= content_lower.count('concern') * 2
        
        return max(0, min(100, score))
    
    def _extract_recommendations(self, analysis_content: str) -> List[Dict[str, Any]]:
        """Extract structured recommendations."""
        import re
        
        recommendations = []
        
        # Look for recommendation patterns
        patterns = [
            r'Recommendation[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'Suggest[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'Should[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, analysis_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if match.strip():
                    recommendations.append({
                        "title": match.strip()[:100] + "..." if len(match.strip()) > 100 else match.strip(),
                        "description": match.strip(),
                        "priority": "Medium",
                        "category": "Architecture"
                    })
        
        return recommendations[:8]
    
    def _extract_design_patterns(self, analysis_content: str) -> List[str]:
        """Extract recommended design patterns."""
        patterns = []
        content_lower = analysis_content.lower()
        
        pattern_keywords = [
            'singleton', 'factory', 'observer', 'strategy', 'decorator',
            'adapter', 'facade', 'mvc', 'mvp', 'mvvm', 'repository',
            'unit of work', 'dependency injection', 'builder'
        ]
        
        for keyword in pattern_keywords:
            if keyword in content_lower:
                patterns.append(keyword.title())
        
        return list(set(patterns))
    
    def _extract_scalability_suggestions(self, analysis_content: str) -> List[str]:
        """Extract scalability improvement suggestions."""
        suggestions = []
        lines = analysis_content.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['scalability', 'scale', 'performance', 'optimization']):
                cleaned = line.strip('- *').strip()
                if cleaned and len(cleaned) > 20:
                    suggestions.append(cleaned)
        
        return suggestions[:6]
    
    def _extract_refactoring_tasks(self, refactoring_content: str) -> List[Dict[str, Any]]:
        """Extract structured refactoring tasks."""
        tasks = []
        lines = refactoring_content.split('\n')
        
        current_task = {}
        for line in lines:
            line = line.strip()
            if 'refactor' in line.lower() or 'extract' in line.lower() or 'improve' in line.lower():
                if current_task:
                    tasks.append(current_task)
                current_task = {
                    "title": line,
                    "description": "",
                    "complexity": "Medium",
                    "impact": "Medium"
                }
            elif current_task and line:
                current_task["description"] += line + " "
        
        if current_task:
            tasks.append(current_task)
        
        return tasks[:5]
    
    def _extract_components(self, architecture_design: str) -> List[str]:
        """Extract system components from architecture design."""
        components = []
        content_lower = architecture_design.lower()
        
        component_keywords = [
            'frontend', 'backend', 'database', 'api gateway', 'load balancer',
            'cache', 'message queue', 'authentication service', 'user service',
            'notification service', 'file storage', 'monitoring'
        ]
        
        for keyword in component_keywords:
            if keyword in content_lower:
                components.append(keyword.title())
        
        return list(set(components))
    
    def _extract_tech_recommendations(self, architecture_design: str) -> List[str]:
        """Extract technology recommendations."""
        recommendations = []
        content_lower = architecture_design.lower()
        
        tech_keywords = [
            'react', 'angular', 'vue', 'node.js', 'python', 'java',
            'postgresql', 'mongodb', 'redis', 'nginx', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp'
        ]
        
        for keyword in tech_keywords:
            if keyword in content_lower:
                recommendations.append(keyword.upper())
        
        return list(set(recommendations))
    
    def _extract_roadmap(self, architecture_design: str) -> List[str]:
        """Extract implementation roadmap steps."""
        roadmap = []
        lines = architecture_design.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['phase', 'step', 'stage', 'milestone']):
                cleaned = line.strip('- *').strip()
                if cleaned and len(cleaned) > 15:
                    roadmap.append(cleaned)
        
        return roadmap[:6]