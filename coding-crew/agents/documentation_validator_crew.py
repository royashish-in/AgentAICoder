"""Documentation validation crew for ensuring docs align with requirements."""

from crewai import Agent, Task, Crew

class DocumentationValidatorCrew:
    """Validates documentation against project requirements and user stories."""
    
    def __init__(self):
        from core.llm_config import get_analysis_llm
        self.llm = get_analysis_llm()
    
    def validate_documentation(self, project_data: dict, documentation: str, requirements: str) -> dict:
        """Validate documentation against requirements and user stories."""
        
        validator_agent = Agent(
            role="Documentation Requirements Validator",
            goal="Ensure documentation fully addresses all project requirements and user stories",
            backstory="Senior technical reviewer specializing in requirements traceability and documentation completeness",
            llm=self.llm,
            verbose=True
        )
        
        validation_task = Task(
            description=f"""
            VALIDATE documentation against requirements:
            
            PROJECT REQUIREMENTS:
            {requirements}
            
            USER STORIES:
            {self._extract_user_stories(project_data)}
            
            GENERATED DOCUMENTATION:
            {documentation}
            
            VALIDATION CHECKLIST:
            1. Requirements Coverage: Does documentation address all stated requirements?
            2. User Story Alignment: Can users complete their stories using this documentation?
            3. Solution Description: Is it clear what the solution does and its purpose?
            4. Installation Guide: Are setup steps complete, accurate, and testable?
            5. Usage Documentation: Are all features explained with practical examples?
            6. Configuration Options: Are customization settings documented?
            7. API/Interface Docs: Are endpoints, functions, or UI elements documented?
            8. Troubleshooting: Are common issues and solutions provided?
            9. Missing Elements: What critical end-user information is missing?
            
            Provide validation result as:
            VALIDATION: PASS/FAIL
            COVERAGE_SCORE: 0-100
            MISSING_REQUIREMENTS: [list]
            STORY_GAPS: [list]
            RECOMMENDATIONS: [list]
            """,
            agent=validator_agent,
            expected_output="Structured validation report with pass/fail status and specific gaps"
        )
        
        crew = Crew(
            agents=[validator_agent],
            tasks=[validation_task],
            verbose=True
        )
        
        result = crew.kickoff()
        return self._parse_validation_result(str(result))
    
    def _extract_user_stories(self, project_data: dict) -> str:
        """Extract user stories for validation."""
        stories = project_data.get('user_stories', {}).get('user_stories', [])
        if not stories:
            return "No specific user stories provided"
        
        story_text = ""
        for story in stories:
            story_text += f"""
            Story {story.get('key', 'N/A')}: {story.get('summary', 'N/A')}
            Description: {story.get('description', 'N/A')}
            """
        return story_text
    
    def _parse_validation_result(self, result: str) -> dict:
        """Parse validation result into structured format."""
        import re
        
        validation_match = re.search(r'VALIDATION:\s*(PASS|FAIL)', result, re.IGNORECASE)
        score_match = re.search(r'COVERAGE_SCORE:\s*(\d+)', result)
        
        return {
            "validation_status": validation_match.group(1) if validation_match else "UNKNOWN",
            "coverage_score": int(score_match.group(1)) if score_match else 0,
            "validation_passed": validation_match and validation_match.group(1).upper() == "PASS",
            "full_report": result,
            "missing_requirements": self._extract_list_items(result, "MISSING_REQUIREMENTS"),
            "story_gaps": self._extract_list_items(result, "STORY_GAPS"),
            "recommendations": self._extract_list_items(result, "RECOMMENDATIONS")
        }
    
    def _extract_list_items(self, text: str, section: str) -> list:
        """Extract list items from validation result."""
        import re
        pattern = f"{section}:\\s*\\[(.*?)\\]"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            items = match.group(1).split(',')
            return [item.strip().strip('"\'') for item in items if item.strip()]
        return []