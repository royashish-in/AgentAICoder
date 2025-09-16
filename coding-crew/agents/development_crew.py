"""Development crew using CrewAI and Ollama for code generation."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
import logging
import html
from config import get_ollama_config

logger = logging.getLogger(__name__)

class DevelopmentCrew:
    """CrewAI-based development crew for code generation."""
    
    def __init__(self):
        from core.llm_config import get_coding_llm
        self.llm = get_coding_llm()
        self.crew = self._create_crew()
    
    def _create_crew(self) -> Crew:
        """Create the development crew with agents and tasks."""
        
        # Coding Agent
        coding_agent = Agent(
            role="Senior Software Developer",
            goal="Generate high-quality, production-ready code based on approved architecture",
            backstory="You are an expert developer with 10+ years of experience in multiple programming languages and frameworks.",
            llm=self.llm,
            verbose=True
        )
        
        # Code Review Agent
        review_agent = Agent(
            role="Code Reviewer",
            goal="Review generated code for quality, security, and best practices",
            backstory="You are a senior code reviewer who ensures code quality, security, and maintainability standards.",
            llm=self.llm,
            verbose=True
        )
        
        return Crew(
            agents=[coding_agent, review_agent],
            tasks=[],
            verbose=True
        )
    
    def generate_code(self, project: dict, analysis: str) -> dict:
        """Generate code based on approved analysis."""
        try:
            # Extract technology stack from analysis
            tech_stack = self._extract_tech_stack_from_analysis(analysis)
            tech_stack_str = ', '.join(tech_stack) if tech_stack else 'Not specified'
            
            # Create coding task with story-first approach
            coding_task = Task(
                description=f"""
                PRIMARY GOAL: Generate code that fulfills this JIRA story:
                {html.escape(self._extract_story_acceptance_criteria(project))}
                
                SUCCESS CRITERIA: The generated code must demonstrably meet the story requirements.
                
                SECONDARY GUIDANCE (only where it supports the primary goal):
                - Analysis recommendations: {html.escape(analysis[:500])}...
                - Technology stack: {html.escape(tech_stack_str)}
                - Project context: {html.escape(project.get('project_name', 'Unknown'))}
                
                {self._format_jira_development_context(project)}
                
                CRITICAL INSTRUCTIONS:
                1. If analysis conflicts with story requirements, prioritize the story
                2. Generate minimal viable implementation that fulfills the story
                3. Include all files needed to demonstrate story completion
                4. Ensure setup is appropriate for story constraints
                
                SELF-VALIDATION: Before finalizing, ask yourself:
                "Does this code directly fulfill the JIRA story requirement?"
                If no, revise to prioritize story fulfillment over architectural complexity.
                
                Generate:
                1. Code that directly enables the story requirement
                2. Configuration files needed for the story
                3. Dependencies appropriate for story constraints
                4. Setup instructions that match story needs
                5. Minimal error handling for story scenarios
                """,
                agent=self.crew.agents[0],
                expected_output="Complete codebase with all necessary files using the specified technology stack"
            )
            
            # Update crew with only coding task (no review to avoid output override)
            self.crew.tasks = [coding_task]
            
            # Execute the crew
            result = self.crew.kickoff()
            
            logger.info("Development crew completed successfully")
            return {
                "code": str(result),
                "status": "completed",
                "files_generated": self._extract_files(str(result))
            }
            
        except Exception as e:
            logger.error(f"Development crew failed: {str(e)}")
            return {
                "code": f"Code generation failed: {str(e)}",
                "status": "failed",
                "files_generated": []
            }
    
    def _extract_files(self, code_output: str) -> list:
        """Extract file names from generated code output."""
        import re
        
        # Look for file patterns in the output
        file_patterns = [
            r'```(\w+)\s*#\s*(\S+\.[\w]+)',  # ```python # main.py
            r'File:\s*(\S+\.[\w]+)',         # File: main.py
            r'(\S+\.[\w]+):',                # main.py:
        ]
        
        files = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, code_output)
            for match in matches:
                if isinstance(match, tuple):
                    files.add(match[-1])  # Get the filename part
                else:
                    files.add(match)
        
        return list(files)
    
    def _extract_story_acceptance_criteria(self, project: dict) -> str:
        """Extract the core story requirement without hard-coding patterns."""
        stories = project.get('user_stories', {}).get('user_stories', [])
        if not stories:
            return f"Project Requirement: {project.get('description', 'No specific story requirements')}"
        
        # Take the first story as primary
        primary_story = stories[0]
        
        return f"""
        Story: {html.escape(str(primary_story.get('key', 'N/A')))}
        Requirement: {html.escape(str(primary_story.get('summary', 'N/A')))}
        Details: {html.escape(str(primary_story.get('description', 'N/A')))}
        
        ACCEPTANCE CRITERIA: The code must directly enable this user story.
        """
    
    def _format_jira_development_context(self, project: dict) -> str:
        """Format JIRA context for development phase."""
        if not project.get('user_stories') or not project['user_stories'].get('user_stories'):
            return ""
        
        stories = project['user_stories']['user_stories']
        context = f"\n\n## JIRA Stories Implementation Guide ({len(stories)} stories):\n"
        
        for i, story in enumerate(stories, 1):
            context += f"\n### Story {i}: {story.get('key', 'N/A')}\n"
            context += f"**Summary:** {story.get('summary', 'N/A')}\n"
            if story.get('description'):
                context += f"**Description:** {story['description']}\n"
            context += f"**Status:** {story.get('status', 'Unknown')}\n"
        
        context += "\n**Development Instructions:**\n"
        context += "- PRIMARY: Fulfill the story requirements exactly\n"
        context += "- Implement minimal viable solution for the story\n"
        context += "- Include story ID references in code comments\n"
        context += "- Ensure code demonstrates story completion\n"
        context += "- Avoid over-engineering beyond story needs\n"
        
        return context
    
    def _extract_tech_stack_from_analysis(self, analysis: str) -> list:
        """Extract technology stack from analysis content."""
        tech_stack = []
        
        # Common patterns to look for technology mentions
        tech_patterns = {
            'javascript': ['javascript', 'js', 'node.js', 'nodejs'],
            'typescript': ['typescript', 'ts'],
            'react': ['react', 'reactjs'],
            'vue': ['vue', 'vue.js', 'vuejs'],
            'angular': ['angular'],
            'java': ['java', 'spring boot', 'spring'],
            'python': ['python', 'django', 'flask', 'fastapi'],
            'c#': ['c#', 'csharp', '.net', 'dotnet', 'asp.net'],
            'go': ['go', 'golang'],
            'rust': ['rust'],
            'php': ['php', 'laravel', 'symfony'],
            'ruby': ['ruby', 'rails'],
            'swift': ['swift', 'ios'],
            'kotlin': ['kotlin', 'android'],
            'scala': ['scala'],
            'html': ['html', 'css'],
            'mysql': ['mysql'],
            'postgresql': ['postgresql', 'postgres'],
            'mongodb': ['mongodb', 'mongo'],
            'redis': ['redis'],
            'docker': ['docker'],
            'kubernetes': ['kubernetes', 'k8s']
        }
        
        analysis_lower = analysis.lower()
        
        for tech, keywords in tech_patterns.items():
            if any(keyword in analysis_lower for keyword in keywords):
                tech_stack.append(tech.title())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_stack = []
        for tech in tech_stack:
            if tech.lower() not in seen:
                seen.add(tech.lower())
                unique_stack.append(tech)
        
        return unique_stack[:10]  # Limit to top 10 technologies