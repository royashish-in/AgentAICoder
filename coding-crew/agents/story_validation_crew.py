"""Story validation crew for ensuring JIRA story compliance."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
import logging

logger = logging.getLogger(__name__)

class StoryValidationCrew:
    """CrewAI-based story validation crew for compliance checking."""
    
    def __init__(self):
        from config import get_ollama_config
        ollama_config = get_ollama_config()
        self.llm = Ollama(model=ollama_config["model"], base_url=ollama_config["base_url"])
    
    def validate_story_completion(self, project: dict, generated_artifacts: dict) -> dict:
        """Validate that generated artifacts fulfill the JIRA story requirements."""
        
        validator_agent = Agent(
            role="Story Acceptance Validator",
            goal="Verify generated artifacts fulfill JIRA story requirements exactly",
            backstory="Expert in validating software deliverables against user story acceptance criteria",
            llm=self.llm,
            verbose=True
        )
        
        validation_task = Task(
            description=f"""
            VALIDATION OBJECTIVE: Verify generated artifacts fulfill this JIRA story:
            
            Story Requirements:
            {self._extract_story_requirement(project)}
            
            Generated Artifacts:
            - Code files: {generated_artifacts.get('code_files', [])}
            - Test files: {generated_artifacts.get('test_files', [])}
            - Documentation: {generated_artifacts.get('doc_files', [])}
            - Project structure: {generated_artifacts.get('folder_summary', {})}
            
            VALIDATION CHECKLIST:
            1. Can the story acceptance criteria be demonstrated with these artifacts?
            2. Are the minimal required files present for the story?
            3. Does the implementation match the story scope (not over/under-engineered)?
            4. Can a developer actually use this to fulfill the story requirement?
            
            For "locally runnable" stories, verify:
            - No external database dependencies in code
            - Package.json or equivalent build files present
            - Simple setup commands available
            
            OUTPUT FORMAT:
            VALIDATION: [PASS/FAIL]
            STORY_COMPLIANCE_SCORE: [0-100]
            GAPS: [List specific missing elements]
            RECOMMENDATIONS: [What needs to be fixed]
            """,
            agent=validator_agent,
            expected_output="Story compliance validation report with pass/fail status"
        )
        
        crew = Crew(
            agents=[validator_agent],
            tasks=[validation_task],
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            return self._parse_validation_result(str(result))
        except Exception as e:
            logger.error(f"Story validation failed: {str(e)}")
            return {
                "validation": "FAIL",
                "score": 0,
                "gaps": [f"Validation error: {str(e)}"],
                "recommendations": ["Fix validation system error"]
            }
    
    def _extract_story_requirement(self, project: dict) -> str:
        """Extract the core story requirement."""
        stories = project.get('user_stories', {}).get('user_stories', [])
        if not stories:
            return f"Project: {project.get('project_name', 'Unknown')}\nDescription: {project.get('description', 'No description')}"
        
        primary_story = stories[0]
        return f"""
        Story Key: {primary_story.get('key', 'N/A')}
        Summary: {primary_story.get('summary', 'N/A')}
        Description: {primary_story.get('description', 'N/A')}
        Status: {primary_story.get('status', 'Unknown')}
        
        ACCEPTANCE CRITERIA: The generated artifacts must directly enable this user story.
        """
    
    def _parse_validation_result(self, result: str) -> dict:
        """Parse validation result into structured format."""
        import re
        
        # Extract validation status
        validation_match = re.search(r'VALIDATION:\s*(\w+)', result, re.IGNORECASE)
        validation = validation_match.group(1) if validation_match else "UNKNOWN"
        
        # Extract score
        score_match = re.search(r'STORY_COMPLIANCE_SCORE:\s*(\d+)', result, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 0
        
        # Extract gaps
        gaps_match = re.search(r'GAPS:\s*(.+?)(?=RECOMMENDATIONS:|$)', result, re.IGNORECASE | re.DOTALL)
        gaps_text = gaps_match.group(1).strip() if gaps_match else ""
        gaps = [gap.strip() for gap in gaps_text.split('\n') if gap.strip() and not gap.strip().startswith('-')]
        
        # Extract recommendations
        rec_match = re.search(r'RECOMMENDATIONS:\s*(.+?)$', result, re.IGNORECASE | re.DOTALL)
        rec_text = rec_match.group(1).strip() if rec_match else ""
        recommendations = [rec.strip() for rec in rec_text.split('\n') if rec.strip() and not rec.strip().startswith('-')]
        
        return {
            "validation": validation.upper(),
            "score": score,
            "gaps": gaps,
            "recommendations": recommendations,
            "full_report": result
        }