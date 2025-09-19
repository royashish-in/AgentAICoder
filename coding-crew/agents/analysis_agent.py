"""Analysis agent for parsing requirements and generating workload analysis."""

from typing import Dict, Any
from core.base_agent import BaseAgent
from core.diagram_generator import DiagramGenerator
from loguru import logger


class AnalysisAgent(BaseAgent):
    """Agent responsible for analyzing requirements and creating system diagrams."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("analysis", config)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process requirements and generate analysis."""
        requirements = input_data.get("requirements", "")
        
        logger.debug(
            f"Processing requirements",
            extra={
                "agent_id": self.agent_id,
                "requirements_length": len(requirements)
            }
        )
        
        # Parse requirements
        parsed_requirements = await self._parse_requirements(requirements)
        
        # Generate workload analysis
        workload_analysis = await self._generate_workload_analysis(parsed_requirements)
        
        # Create system diagrams
        system_diagrams = await self._create_system_diagrams(parsed_requirements)
        
        return {
            "parsed_requirements": parsed_requirements,
            "workload_analysis": workload_analysis,
            "system_diagrams": system_diagrams,
            "analysis_complete": True
        }
    
    async def _parse_requirements(self, requirements: str) -> Dict[str, Any]:
        """Parse markdown requirements into structured data."""
        # TODO: Implement Ollama integration for requirement parsing
        return {
            "title": "Parsed Requirements",
            "sections": [],
            "complexity": "medium",
            "estimated_components": 5
        }
    
    async def _generate_workload_analysis(self, parsed_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workload analysis based on parsed requirements."""
        # TODO: Implement Ollama integration for workload analysis
        return {
            "estimated_effort": "medium",
            "recommended_architecture": "microservices",
            "key_components": [],
            "technology_stack": []
        }
    
    async def _create_system_diagrams(self, parsed_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create aesthetic draw.io XML diagrams."""
        from core.drawio_generator import DrawIODiagramGenerator
        
        diagram_gen = DrawIODiagramGenerator()
        
        # Extract components for diagram generation
        components = self._extract_components(parsed_requirements)
        
        # Generate proper draw.io XML diagrams
        system_diagram = diagram_gen.generate_system_architecture({"components": components})
        
        # Dynamic workflow stages based on project complexity
        workflow_stages = self._get_workflow_stages(parsed_requirements)
        workflow_diagram = diagram_gen.generate_workflow_diagram(workflow_stages)
        
        logger.info(f"Generated draw.io XML diagrams")
        
        return {
            "system_architecture": system_diagram,
            "workflow_diagram": workflow_diagram,
            "quality_validation": self._validate_diagram_quality(system_diagram, workflow_diagram)
        }
    
    def _extract_components(self, parsed_requirements: Dict[str, Any]) -> list:
        """Extract system components from parsed requirements."""
        # Extract components from requirements or use dynamic defaults
        if "components" in parsed_requirements:
            return parsed_requirements["components"]
        
        # Generate components based on requirements complexity
        complexity = parsed_requirements.get("complexity", "medium")
        component_count = parsed_requirements.get("estimated_components", 3)
        
        # Dynamic component generation based on analysis
        base_components = [
            {"name": "User Interface", "type": "ui"},
            {"name": "Application Logic", "type": "service"},
            {"name": "Data Storage", "type": "storage"}
        ]
        
        if component_count > 3:
            base_components.extend([
                {"name": "API Gateway", "type": "service"},
                {"name": "External Services", "type": "external"}
            ])
        
        return base_components[:component_count]
    
    def _get_workflow_stages(self, parsed_requirements: Dict[str, Any]) -> list:
        """Get workflow stages based on project requirements."""
        complexity = parsed_requirements.get("complexity", "medium")
        
        # Base workflow stages
        stages = ["Requirements Analysis", "Architecture Design", "Implementation"]
        
        # Add stages based on complexity
        if complexity in ["medium", "high"]:
            stages.extend(["Code Review", "Testing"])
        
        if complexity == "high":
            stages.extend(["Integration Testing", "Documentation"])
        
        return stages
    
    def _validate_diagram_quality(self, system_diagram: str, workflow_diagram: str) -> Dict[str, bool]:
        """Validate diagram quality dynamically."""
        return {
            "proper_xml_format": "<mxfile>" in system_diagram and "<mxfile>" in workflow_diagram,
            "has_components": "mxCell" in system_diagram,
            "has_workflow_stages": "mxCell" in workflow_diagram,
            "valid_structure": "<root>" in system_diagram and "<root>" in workflow_diagram,
            "aesthetic_styling": "fillColor=" in system_diagram
        }
    
    def chat_about_analysis(self, message: str, context: Dict[str, Any]) -> str:
        """Chat as the AI architect who created this analysis."""
        message_lower = message.lower()
        tech_stack = context.get('recommended_tech_stack', [])
        timeline = context.get('estimated_timeline', '2-4 weeks')
        project_name = context.get('project_requirements', {}).get('name', 'this project')
        
        if any(word in message_lower for word in ['implement', 'code', 'develop', 'build']):
            return f"As the architect for {project_name}, I've designed the system to be implemented by our specialized coding agents using {', '.join(tech_stack)}. They'll follow my architectural specifications exactly - proper layering, clean interfaces, and the patterns I've defined. The coding agents handle implementation while I ensure architectural integrity."
        
        elif any(word in message_lower for word in ['react', 'angular']) and 'react' in message_lower and 'angular' in message_lower:
            return f"I included both React and Angular in the stack because they serve different architectural layers. React handles the dynamic UI components with optimal performance, while Angular provides the enterprise framework structure. For {project_name}, this hybrid approach gives us both flexibility and robustness."
        
        elif 'react' in message_lower:
            return f"I chose React for {project_name} because of its component-based architecture and virtual DOM performance. It aligns perfectly with the modular design I've specified - each UI component maps to a clear architectural boundary."
        
        elif 'angular' in message_lower:
            return f"Angular is in my architecture for {project_name} because it provides the enterprise-grade structure needed for complex business logic. Its dependency injection and TypeScript integration support the scalable patterns I've designed."
        
        elif any(word in message_lower for word in ['tech', 'technology', 'stack']):
            return f"I selected {', '.join(tech_stack)} after analyzing {project_name}'s requirements. Each technology serves a specific architectural purpose in my design - this combination provides optimal performance, maintainability, and allows our coding agents to implement clean, scalable code."
        
        elif any(word in message_lower for word in ['timeline', 'time', 'estimate']):
            return f"My {timeline} estimate for {project_name} is based on architectural complexity analysis. This accounts for the coding agents implementing my design, iterative testing cycles, and deployment validation. The modular architecture I've created allows for parallel development streams."
        
        elif any(word in message_lower for word in ['architecture', 'design', 'structure']):
            return f"I've architected {project_name} with modern patterns - clean separation of concerns, scalable data flows, and maintainable component boundaries. The coding agents will implement exactly what I've specified in the technical design, following the architectural principles I've established."
        
        elif any(word in message_lower for word in ['test', 'testing']):
            test_plan = context.get('test_plan', '')
            if test_plan:
                return f"I've designed a comprehensive testing strategy for {project_name}. The test plan covers unit tests for each architectural component, integration tests for data flows, and end-to-end validation. Our testing agents will implement these tests following my specifications."
            else:
                return f"Testing for {project_name} will follow the architectural boundaries I've defined - unit tests for each component, integration tests for service interactions, and system tests for the complete workflow."
        
        elif any(word in message_lower for word in ['diagram', 'visual']):
            return f"I've created system diagrams that visualize the architecture for {project_name}. These show component relationships, data flows, and deployment structure. The diagrams serve as blueprints for our coding agents during implementation."
        
        else:
            return f"I'm the AI architect who analyzed and designed {project_name}. I can explain my technology choices, architectural decisions, timeline estimates, or how our coding agents will implement my design. What specific aspect of the architecture interests you?"