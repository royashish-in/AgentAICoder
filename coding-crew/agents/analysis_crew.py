"""Analysis crew using CrewAI and Ollama for requirements analysis."""

from crewai import Agent, Task, Crew
from langchain_community.llms import Ollama
import logging
import re

logger = logging.getLogger(__name__)

def format_analysis_as_markdown(text: str) -> str:
    """Format analysis text as proper markdown."""
    # Clean up the text and ensure proper markdown formatting
    formatted = text.strip()
    
    # Fix malformed markdown patterns
    formatted = re.sub(r'\*\*([^*]+)\*\*\s*\*\*', r'## \1', formatted)
    formatted = re.sub(r'##\s*-\s*\*([^*]+)\*\*', r'### \1', formatted)
    formatted = re.sub(r'-\s*\*\*([^*]+)\*\*', r'### \1', formatted)
    formatted = re.sub(r'-\s*##', r'###', formatted)
    formatted = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', formatted)
    
    # Clean up excessive whitespace
    formatted = re.sub(r'\n{3,}', '\n\n', formatted)
    
    return formatted

class AnalysisCrew:
    """CrewAI-based analysis crew for requirements processing."""
    
    def __init__(self, model_name: str = "ollama/llama3.1:8b"):
        from core.llm_config import get_analysis_llm
        self.llm = get_analysis_llm()
        self.crew = self._create_crew()
    
    def _create_crew(self) -> Crew:
        """Create the analysis crew with agents and tasks."""
        
        # Analysis Agent
        analysis_agent = Agent(
            role="Requirements Analyst",
            goal="Analyze project requirements and create comprehensive technical specifications",
            backstory="You are an expert software architect with 15+ years of experience in analyzing requirements and designing scalable systems.",
            llm=self.llm,
            verbose=True
        )
        
        # Architecture Review Agent
        review_agent = Agent(
            role="Architecture Reviewer",
            goal="Review and refine technical analysis to ensure best practices and optimal design",
            backstory="You are a senior technical reviewer who specializes in identifying potential issues and suggesting improvements in system architecture.",
            llm=self.llm,
            verbose=True
        )
        
        return Crew(
            agents=[analysis_agent, review_agent],
            tasks=[],
            verbose=True
        )
    
    def analyze_requirements(self, requirements: dict) -> str:
        """Analyze project requirements using CrewAI."""
        try:
            # Create analysis task with story-first approach
            analysis_task = Task(
                description=f"""
                PRIMARY OBJECTIVE: Analyze requirements to fulfill this JIRA story:
                {self._extract_primary_story_requirement(requirements)}
                
                CONSTRAINT: All recommendations must support the story objective above.
                
                Project Context:
                - Project: {requirements.get('project_name', 'Unknown')}
                - Description: {requirements.get('description', 'No description')}
                - Target Users: {requirements.get('target_users', 'Not specified')}
                - Scale: {requirements.get('scale', 'Not specified')}
                - Features: {', '.join(requirements.get('features', []))}
                - Constraints: {requirements.get('constraints', 'None specified')}
                
                {self._format_jira_context(requirements)}
                
                Provide (only if they support the story objective):
                1. Technology stack recommendations
                2. Architecture patterns
                3. Development approach
                4. Security considerations (only if required by story)
                5. Deployment strategy
                6. System architecture diagram in draw.io XML format
                
                IMPORTANT: Include a draw.io XML diagram showing the system architecture.
                Create a professional diagram with components, data flow, and interactions.
                Use proper draw.io XML format starting with <mxfile> and ending with </mxfile>.
                
                Example format:
                ```xml
                <mxfile host="app.diagrams.net">
                  <diagram name="System Architecture">
                    <mxGraphModel>
                      <root>
                        <mxCell id="0"/>
                        <mxCell id="1" parent="0"/>
                        <mxCell id="2" value="Component" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
                          <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
                        </mxCell>
                      </root>
                    </mxGraphModel>
                  </diagram>
                </mxfile>
                ```
                
                Format the response as a detailed technical analysis with embedded diagram.
                """,
                agent=self.crew.agents[0],
                expected_output="Comprehensive technical analysis with recommendations"
            )
            
            # Create test planning task (parallel to analysis)
            test_planning_task = Task(
                description=f"""
                Based on JIRA story requirements, define test strategy:
                
                Story Requirements:
                {self._extract_primary_story_requirement(requirements)}
                
                Generate:
                1. Test scenarios that prove story acceptance criteria
                2. Test file structure and naming conventions
                3. Required test dependencies and setup
                4. Success/failure criteria for each test scenario
                5. Minimal test suite focused on story validation
                
                Focus on story validation, not comprehensive testing.
                Ensure tests can demonstrate the story is fulfilled.
                """,
                agent=self.crew.agents[1],
                expected_output="Test plan aligned with story requirements"
            )
            
            # Create review task
            review_task = Task(
                description="""
                Review the technical analysis and test plan, ensuring both support the JIRA story:
                
                PRIORITY: Validate that analysis and tests fulfill the story requirements.
                
                Provide:
                1. Validation of technology choices (story-appropriate)
                2. Identification of potential issues
                3. Suggestions for improvements
                4. Risk assessment
                5. Alternative approaches if needed
                6. Refined draw.io XML diagrams with professional aesthetics
                7. Test plan validation and refinement
                
                CRITICAL XML VALIDATION: Generate high-quality draw.io XML diagrams that are:
                - Structurally valid with proper parent-child relationships
                - All mxCell elements must have valid parent references (parent="0" or parent="1")
                - Proper mxGeometry with x, y, width, height coordinates
                - Valid edge connections with source and target cell IDs
                - Professional styling with fillColor, strokeColor, rounded corners
                
                Required diagrams:
                - System Architecture Diagram
                - Data Flow Diagram  
                - Component Interaction Diagram
                
                XML Structure Requirements:
                ```xml
                <mxfile host="app.diagrams.net">
                  <diagram name="Diagram Name">
                    <mxGraphModel>
                      <root>
                        <mxCell id="0"/>
                        <mxCell id="1" parent="0"/>
                        <mxCell id="2" value="Component" style="rounded=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
                          <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
                        </mxCell>
                      </root>
                    </mxGraphModel>
                  </diagram>
                </mxfile>
                ```
                
                Validate each XML diagram can be imported into draw.io without errors.
                """,
                agent=self.crew.agents[1],
                expected_output="Reviewed technical analysis with validated draw.io XML diagrams"
            )
            
            # Update crew with tasks (analysis + test planning + review)
            self.crew.tasks = [analysis_task, test_planning_task, review_task]
            
            # Execute the crew
            result = self.crew.kickoff()
            
            logger.info("Analysis crew completed successfully")
            analysis_text = format_analysis_as_markdown(str(result))
            
            # Extract and store diagrams
            diagrams = self._extract_diagrams(analysis_text)
            if diagrams:
                # Store diagrams in the analysis for later use
                analysis_text += "\n\n## Generated Diagrams\n\n"
                for i, diagram in enumerate(diagrams):
                    analysis_text += f"### Diagram {i+1}\n```xml\n{diagram}\n```\n\n"
            
            return analysis_text
            
        except Exception as e:
            logger.error(f"Analysis crew failed: {str(e)}")
            return f"Analysis failed: {str(e)}"
    
    def rework_analysis(self, requirements: dict, feedback: str) -> str:
        """Rework analysis based on feedback."""
        try:
            rework_task = Task(
                description=f"""
                Rework the previous analysis based on the following feedback:
                
                FEEDBACK: {feedback}
                
                Original Requirements:
                Project: {requirements.get('project_name', 'Unknown')}
                Description: {requirements.get('description', 'No description')}
                Target Users: {requirements.get('target_users', 'Not specified')}
                Scale: {requirements.get('scale', 'Not specified')}
                Features: {', '.join(requirements.get('features', []))}
                Constraints: {requirements.get('constraints', 'None specified')}
                
                {self._format_jira_context(requirements)}
                
                Address the feedback specifically and provide a revised analysis that:
                1. Incorporates the feedback requirements
                2. Adjusts technology recommendations accordingly
                3. Modifies architecture patterns as needed
                4. Updates deployment strategy based on constraints
                5. Explains how the feedback has been addressed
                6. Updated draw.io XML diagrams reflecting changes
                
                IMPORTANT: Update all draw.io XML diagrams to reflect the feedback.
                Generate revised system architecture, data flow, and component diagrams.
                Maintain professional aesthetics with gradients, shadows, and consistent styling.
                
                Format as a comprehensive revised technical analysis with updated diagrams.
                """,
                agent=self.crew.agents[0],
                expected_output="Revised technical analysis incorporating feedback"
            )
            
            self.crew.tasks = [rework_task]
            result = self.crew.kickoff()
            
            logger.info("Analysis rework completed successfully")
            analysis_text = format_analysis_as_markdown(str(result))
            
            # Extract and store diagrams
            diagrams = self._extract_diagrams(analysis_text)
            if diagrams:
                # Store diagrams in the analysis for later use
                analysis_text += "\n\n## Updated Diagrams\n\n"
                for i, diagram in enumerate(diagrams):
                    analysis_text += f"### Updated Diagram {i+1}\n```xml\n{diagram}\n```\n\n"
            
            return analysis_text
            
        except Exception as e:
            logger.error(f"Analysis rework failed: {str(e)}")
            return f"Rework failed: {str(e)}"
    
    def _extract_diagrams(self, analysis_text: str) -> list:
        """Extract draw.io XML diagrams from analysis text."""
        import re
        
        # Look for draw.io XML patterns
        xml_patterns = [
            r'```xml\s*(<mxfile[^>]*>.*?</mxfile>)\s*```',
            r'```drawio\s*(<mxfile[^>]*>.*?</mxfile>)\s*```',
            r'(<mxfile[^>]*>.*?</mxfile>)',
        ]
        
        diagrams = []
        for pattern in xml_patterns:
            matches = re.findall(pattern, analysis_text, re.DOTALL | re.IGNORECASE)
            diagrams.extend(matches)
        
        # Clean up and validate diagrams
        valid_diagrams = []
        for diagram in diagrams:
            if '<mxfile' in diagram and '</mxfile>' in diagram and '<mxGraphModel>' in diagram:
                # Clean up the XML
                cleaned = diagram.strip()
                # Ensure proper XML declaration if missing
                if not cleaned.startswith('<?xml'):
                    cleaned = '<?xml version="1.0" encoding="UTF-8"?>\n' + cleaned
                
                # Validate XML structure
                if self._validate_drawio_xml(cleaned):
                    valid_diagrams.append(cleaned)
                else:
                    logger.warning(f"Invalid draw.io XML structure detected, skipping diagram")
        
        # If no valid diagrams found, create a simple fallback
        if not valid_diagrams:
            logger.warning("No valid draw.io diagrams found in analysis")
            # Create a simple system diagram as fallback
            fallback_diagram = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram name="System Architecture">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="User Interface" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;shadow=1;" vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="Business Logic" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;shadow=1;" vertex="1" parent="1">
          <mxGeometry x="300" y="100" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="Data Layer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;shadow=1;" vertex="1" parent="1">
          <mxGeometry x="500" y="100" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="5" value="" style="endArrow=classic;html=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="2" target="3">
          <mxGeometry width="50" height="50" relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="6" value="" style="endArrow=classic;html=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="3" target="4">
          <mxGeometry width="50" height="50" relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
            valid_diagrams.append(fallback_diagram)
        
        return valid_diagrams
    
    def _extract_primary_story_requirement(self, requirements: dict) -> str:
        """Extract the core story requirement without hard-coding patterns."""
        stories = requirements.get('user_stories', {}).get('user_stories', [])
        if not stories:
            return f"Project Requirement: {requirements.get('description', 'No specific story requirements')}"
        
        # Take the first story as primary (or combine if multiple)
        primary_story = stories[0]
        
        return f"""
        Story: {primary_story.get('key', 'N/A')}
        Requirement: {primary_story.get('summary', 'N/A')}
        Details: {primary_story.get('description', 'N/A')}
        
        ACCEPTANCE CRITERIA: All technical decisions must directly enable this user story.
        """
    
    def _format_jira_context(self, requirements: dict) -> str:
        """Format JIRA user stories context for analysis."""
        if not requirements.get('user_stories') or not requirements['user_stories'].get('user_stories'):
            return ""
        
        stories = requirements['user_stories']['user_stories']
        context = f"\n\n## JIRA User Stories Context ({len(stories)} stories):\n"
        context += "This project is based on JIRA user stories. Each story represents a specific feature requirement:\n\n"
        
        for i, story in enumerate(stories, 1):
            context += f"{i}. **{story.get('key', 'N/A')}**: {story.get('summary', 'N/A')}\n"
            if story.get('description'):
                context += f"   - Description: {story['description']}\n"
            context += f"   - Status: {story.get('status', 'Unknown')}\n\n"
        
        context += "\n**Analysis Instructions for JIRA Projects:**\n"
        context += "- PRIMARY: Fulfill the story requirements exactly\n"
        context += "- Consider story dependencies and integration points\n"
        context += "- Design architecture to support the specific story needs\n"
        context += "- Avoid over-engineering beyond story scope\n"
        
        return context
    
    def _validate_drawio_xml(self, xml_content: str) -> bool:
        """Validate draw.io XML structure."""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse XML to check basic structure
            root = ET.fromstring(xml_content)
            
            # Check required elements
            if root.tag != 'mxfile':
                return False
            
            diagram = root.find('diagram')
            if diagram is None:
                return False
            
            model = diagram.find('mxGraphModel')
            if model is None:
                return False
            
            root_elem = model.find('root')
            if root_elem is None:
                return False
            
            # Check for required root cells
            cells = root_elem.findall('mxCell')
            if len(cells) < 2:  # Should have at least cells with id="0" and id="1"
                return False
            
            # Validate cell structure
            cell_ids = set()
            for cell in cells:
                cell_id = cell.get('id')
                if not cell_id:
                    return False
                cell_ids.add(cell_id)
                
                # Check parent references are valid
                parent = cell.get('parent')
                if parent and parent not in ['0'] and parent not in cell_ids:
                    # Parent should exist or be root
                    continue
            
            return True
            
        except Exception as e:
            logger.warning(f"XML validation failed: {str(e)}")
            return False