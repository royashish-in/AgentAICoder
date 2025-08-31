"""Integration layer for generating diagrams from AI analysis."""

from typing import Dict, Any
from core.drawio_generator import DrawIOGenerator
from core.diagram_parser import DiagramParser


class DiagramIntegration:
    """Integrate AI analysis with professional diagram generation."""
    
    def __init__(self):
        self.generator = DrawIOGenerator()
        self.parser = DiagramParser()
    
    def generate_diagrams_from_analysis(self, analysis_text: str) -> Dict[str, str]:
        """Generate professional diagrams from AI analysis text."""
        
        # Parse the analysis to extract diagram data
        diagram_data = self.parser.parse_analysis_output(analysis_text)
        
        # Generate professional draw.io XML diagrams
        diagrams = {}
        
        # System Architecture Diagram
        if diagram_data['components']:
            diagrams['system_architecture'] = self.generator.create_system_architecture(
                diagram_data['components']
            )
        
        # Component Relationship Diagram  
        if diagram_data['component_details']:
            diagrams['component_relationships'] = self.generator.create_component_diagram(
                diagram_data['component_details']
            )
        
        # Data Flow Diagram
        if diagram_data['data_flow']:
            diagrams['data_flow'] = self.generator.create_data_flow_diagram(
                diagram_data['data_flow']
            )
        
        return diagrams
    
    def enhance_analysis_with_diagrams(self, analysis_text: str) -> str:
        """Enhance analysis text by replacing basic XML with professional diagrams."""
        
        # Generate professional diagrams
        diagrams = self.generate_diagrams_from_analysis(analysis_text)
        
        # Replace any existing diagram sections with professional ones
        enhanced_text = analysis_text
        
        if 'system_architecture' in diagrams:
            # Replace system architecture diagram
            enhanced_text = self._replace_diagram_section(
                enhanced_text,
                'System Architecture Diagram',
                diagrams['system_architecture']
            )
        
        if 'component_relationships' in diagrams:
            # Replace component diagram
            enhanced_text = self._replace_diagram_section(
                enhanced_text,
                'Component Relationship Diagram',
                diagrams['component_relationships']
            )
        
        if 'data_flow' in diagrams:
            # Replace data flow diagram
            enhanced_text = self._replace_diagram_section(
                enhanced_text,
                'Data Flow Diagram',
                diagrams['data_flow']
            )
        
        return enhanced_text
    
    def _replace_diagram_section(self, text: str, section_name: str, new_diagram: str) -> str:
        """Replace a diagram section in the text with professional version."""
        
        # Look for existing diagram section
        import re
        
        # Pattern to match diagram sections with XML content
        pattern = rf'### {section_name}.*?```xml.*?```'
        
        replacement = f'''### {section_name}

```xml
{new_diagram}
```'''
        
        # Replace if found, otherwise append
        if re.search(pattern, text, re.DOTALL | re.IGNORECASE):
            return re.sub(pattern, replacement, text, flags=re.DOTALL | re.IGNORECASE)
        else:
            # Append new diagram section
            return f"{text}\n\n{replacement}"