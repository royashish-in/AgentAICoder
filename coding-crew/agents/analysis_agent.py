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