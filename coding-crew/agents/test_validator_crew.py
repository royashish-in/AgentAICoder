"""Automated test validation crew for story-test alignment."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
import logging

logger = logging.getLogger(__name__)

class AutomatedTestValidator:
    """Automated validation of test-story alignment."""
    
    def __init__(self):
        from config import get_ollama_config
        ollama_config = get_ollama_config()
        self.llm = Ollama(model=ollama_config["model"], base_url=ollama_config["base_url"])
    
    def validate_test_story_alignment(self, test_plan: str, story: dict) -> dict:
        """Validate test plan covers story requirements with auto-approval."""
        
        test_validator_agent = Agent(
            role="Test-Story Alignment Validator",
            goal="Validate test plans cover story requirements completely",
            backstory="Expert in ensuring test coverage matches user story acceptance criteria",
            llm=self.llm,
            verbose=True
        )
        
        validation_task = Task(
            description=f"""
            Validate test plan covers story requirements:
            
            Story Requirements:
            Key: {story.get('key', 'N/A')}
            Summary: {story.get('summary', 'N/A')}
            Description: {story.get('description', 'N/A')}
            
            Test Plan:
            {test_plan}
            
            VALIDATION CRITERIA:
            1. Every story acceptance criterion has corresponding test scenario
            2. Tests are minimal but sufficient for story validation
            3. No excessive testing beyond story scope
            4. Tests can demonstrate story fulfillment
            5. Test setup matches story constraints (e.g., local vs external dependencies)
            
            SCORING:
            - Coverage: Does test plan cover all story requirements? (0-40 points)
            - Appropriateness: Are tests appropriate for story scope? (0-30 points)
            - Feasibility: Can tests actually validate the story? (0-30 points)
            
            OUTPUT FORMAT:
            ALIGNMENT_SCORE: [0-100]
            COVERAGE_GAPS: [List missing test scenarios]
            EXCESSIVE_TESTS: [List unnecessary tests beyond story scope]
            RECOMMENDATION: [AUTO_APPROVE/ESCALATE_TO_HUMAN]
            JUSTIFICATION: [Reason for recommendation]
            
            Auto-approve if alignment score >= 90 and no critical gaps.
            """,
            agent=test_validator_agent,
            expected_output="Test-story alignment validation with auto-approval decision"
        )
        
        crew = Crew(
            agents=[test_validator_agent],
            tasks=[validation_task],
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            return self._parse_test_validation_result(str(result))
        except Exception as e:
            logger.error(f"Test validation failed: {str(e)}")
            return {
                "alignment_score": 0,
                "recommendation": "ESCALATE_TO_HUMAN",
                "justification": f"Validation error: {str(e)}",
                "coverage_gaps": ["Validation system error"],
                "excessive_tests": [],
                "approved": False
            }
    
    def _parse_test_validation_result(self, result: str) -> dict:
        """Parse test validation result into structured format."""
        import re
        
        # Extract alignment score
        score_match = re.search(r'ALIGNMENT_SCORE:\s*(\d+)', result, re.IGNORECASE)
        alignment_score = int(score_match.group(1)) if score_match else 0
        
        # Extract recommendation
        rec_match = re.search(r'RECOMMENDATION:\s*(\w+)', result, re.IGNORECASE)
        recommendation = rec_match.group(1) if rec_match else "ESCALATE_TO_HUMAN"
        
        # Extract justification
        just_match = re.search(r'JUSTIFICATION:\s*(.+?)(?=COVERAGE_GAPS:|$)', result, re.IGNORECASE | re.DOTALL)
        justification = just_match.group(1).strip() if just_match else "No justification provided"
        
        # Extract coverage gaps
        gaps_match = re.search(r'COVERAGE_GAPS:\s*(.+?)(?=EXCESSIVE_TESTS:|RECOMMENDATION:|$)', result, re.IGNORECASE | re.DOTALL)
        gaps_text = gaps_match.group(1).strip() if gaps_match else ""
        coverage_gaps = [gap.strip() for gap in gaps_text.split('\n') if gap.strip() and not gap.strip().startswith('-')]
        
        # Extract excessive tests
        excess_match = re.search(r'EXCESSIVE_TESTS:\s*(.+?)(?=RECOMMENDATION:|$)', result, re.IGNORECASE | re.DOTALL)
        excess_text = excess_match.group(1).strip() if excess_match else ""
        excessive_tests = [test.strip() for test in excess_text.split('\n') if test.strip() and not test.strip().startswith('-')]
        
        # Determine approval
        approved = (recommendation.upper() == "AUTO_APPROVE" and alignment_score >= 90)
        
        return {
            "alignment_score": alignment_score,
            "recommendation": recommendation.upper(),
            "justification": justification,
            "coverage_gaps": coverage_gaps,
            "excessive_tests": excessive_tests,
            "approved": approved,
            "full_report": result
        }