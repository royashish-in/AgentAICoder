"""Enhanced development crew with technology-specific agents."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
import logging
from .tech_specific_agents import TechSpecificAgentFactory, BestPracticesManager, CodeTemplateManager

logger = logging.getLogger(__name__)

class EnhancedDevelopmentCrew:
    """Enhanced development crew with tech-specific agents and best practices."""
    
    def __init__(self):
        from core.llm_config import get_coding_llm
        self.llm = get_coding_llm()
        
        self.agent_factory = TechSpecificAgentFactory()
        self.best_practices = BestPracticesManager()
        self.templates = CodeTemplateManager()
    
    def generate_code(self, project: dict, analysis: str) -> dict:
        """Generate code using technology-specific agents."""
        try:
            # Extract technology stack
            tech_stack = self._extract_tech_stack_from_analysis(analysis)
            primary_tech = self._determine_primary_tech(tech_stack)
            
            # Get tech-specific agent
            coding_agent = self.agent_factory.create_agent(tech_stack)
            
            # Get best practices for this technology
            practices = self.best_practices.get_practices(primary_tech)
            
            # Create enhanced coding task
            coding_task = Task(
                description=f"""
                STORY REQUIREMENT: {self._extract_story_requirement(project)}
                
                TECHNOLOGY STACK: {', '.join(tech_stack)}
                PRIMARY TECHNOLOGY: {primary_tech}
                
                BEST PRACTICES TO FOLLOW:
                {self._format_best_practices(practices)}
                
                CODE TEMPLATES AVAILABLE:
                {self._get_available_templates(primary_tech)}
                
                INSTRUCTIONS:
                1. Generate code that fulfills the story requirement
                2. Follow {primary_tech}-specific best practices listed above
                3. Use appropriate code templates where applicable
                4. Implement proper project structure for {primary_tech}
                5. Include necessary dependencies and configuration
                6. Add inline comments referencing best practices used
                
                QUALITY STANDARDS:
                - Follow language/framework conventions
                - Implement proper error handling
                - Include basic security measures
                - Ensure code is testable
                - Use consistent naming conventions
                
                DELIVERABLES:
                - Complete, runnable codebase
                - Proper project structure
                - Configuration files
                - Basic documentation
                - Example usage
                """,
                agent=coding_agent,
                expected_output="Complete codebase following technology-specific best practices"
            )
            
            # Execute with single agent (avoid output conflicts)
            crew = Crew(
                agents=[coding_agent],
                tasks=[coding_task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            # Extract and save new patterns for future use
            self._extract_and_save_patterns(str(result), primary_tech)
            
            logger.info(f"Enhanced development crew completed for {primary_tech}")
            return {
                "code": str(result),
                "status": "completed",
                "technology": primary_tech,
                "best_practices_used": practices,
                "files_generated": self._extract_files(str(result))
            }
            
        except Exception as e:
            logger.error(f"Enhanced development crew failed: {str(e)}")
            return {
                "code": f"Code generation failed: {str(e)}",
                "status": "failed",
                "files_generated": []
            }
    
    def _extract_tech_stack_from_analysis(self, analysis: str) -> list:
        """Extract technology stack from analysis."""
        tech_patterns = {
            'React': ['react', 'reactjs', 'jsx'],
            'JavaScript': ['javascript', 'js', 'node.js'],
            'TypeScript': ['typescript', 'ts'],
            'Python': ['python'],
            'Django': ['django'],
            'FastAPI': ['fastapi'],
            'Flask': ['flask'],
            'Java': ['java'],
            'Spring': ['spring boot', 'spring'],
            'C#': ['c#', 'csharp'],
            '.NET': ['.net', 'dotnet', 'asp.net']
        }
        
        analysis_lower = analysis.lower()
        detected_tech = []
        
        for tech, keywords in tech_patterns.items():
            if any(keyword in analysis_lower for keyword in keywords):
                detected_tech.append(tech)
        
        return detected_tech or ['Generic']
    
    def _determine_primary_tech(self, tech_stack: list) -> str:
        """Determine primary technology."""
        priority = {
            'React': 10, 'JavaScript': 9, 'TypeScript': 8,
            'Python': 10, 'Django': 9, 'FastAPI': 8,
            'Java': 10, 'Spring': 9,
            'C#': 10, '.NET': 9
        }
        
        best_tech = 'Generic'
        best_score = 0
        
        for tech in tech_stack:
            score = priority.get(tech, 0)
            if score > best_score:
                best_score = score
                best_tech = tech
        
        return best_tech
    
    def _extract_story_requirement(self, project: dict) -> str:
        """Extract story requirement."""
        stories = project.get('user_stories', {}).get('user_stories', [])
        if stories:
            story = stories[0]
            return f"{story.get('key', 'N/A')}: {story.get('summary', 'N/A')}"
        return project.get('description', 'No specific requirements')
    
    def _format_best_practices(self, practices: dict) -> str:
        """Format best practices for prompt."""
        if not practices:
            return "No specific best practices available"
        
        formatted = ""
        for category, items in practices.items():
            if isinstance(items, list):
                formatted += f"\n{category.upper()}:\n"
                for item in items:
                    formatted += f"- {item}\n"
            elif isinstance(items, dict):
                formatted += f"\n{category.upper()}:\n"
                for key, value in items.items():
                    formatted += f"- {key}: {value}\n"
        
        return formatted
    
    def _get_available_templates(self, technology: str) -> str:
        """Get available templates for technology."""
        templates_dir = self.templates.templates_dir / technology.lower()
        if templates_dir.exists():
            templates = [f.stem for f in templates_dir.glob("*.template")]
            return f"Available templates: {', '.join(templates)}"
        return "No templates available"
    
    def _extract_files(self, code_output: str) -> list:
        """Extract generated file names."""
        import re
        
        patterns = [
            r'```\w+\s*#\s*(\S+\.\w+)',
            r'File:\s*(\S+\.\w+)',
            r'(\S+\.\w+):',
            r'create\s+(\S+\.\w+)',
            r'save\s+(\S+\.\w+)'
        ]
        
        files = set()
        for pattern in patterns:
            matches = re.findall(pattern, code_output, re.IGNORECASE)
            files.update(matches)
        
        return list(files)
    
    def _extract_and_save_patterns(self, code_output: str, technology: str):
        """Extract and save new coding patterns for future use."""
        # Look for patterns that could be reused
        patterns_found = []
        
        # Extract import patterns
        import re
        imports = re.findall(r'import\s+.*', code_output)
        if imports:
            patterns_found.extend(imports[:5])  # Save top 5 import patterns
        
        # Extract class/function patterns
        classes = re.findall(r'class\s+\w+.*:', code_output)
        functions = re.findall(r'def\s+\w+.*:', code_output)
        
        # Save useful patterns
        for pattern in patterns_found[:3]:  # Limit to avoid noise
            self.best_practices.add_practice(
                technology, 
                "common_patterns", 
                pattern.strip()
            )