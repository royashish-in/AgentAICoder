"""Draw.io diagram generation with aesthetic templates."""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from pathlib import Path
import json


class DrawIODiagramGenerator:
    """Generate aesthetic draw.io XML diagrams."""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "diagram_templates"
        self.templates_dir.mkdir(exist_ok=True)
        
    def generate_system_architecture(self, analysis_data: Dict[str, Any]) -> str:
        """Generate system architecture diagram."""
        
        # Create root mxfile element
        root = ET.Element("mxfile", host="app.diagrams.net", modified="2024-01-01T00:00:00.000Z")
        diagram = ET.SubElement(root, "diagram", id="system-arch", name="System Architecture")
        
        # Create mxGraphModel
        graph_model = ET.SubElement(diagram, "mxGraphModel", 
                                   dx="1426", dy="827", grid="1", gridSize="10", 
                                   guides="1", tooltips="1", connect="1", 
                                   arrows="1", fold="1", page="1", pageScale="1")
        
        # Root cell
        root_cell = ET.SubElement(graph_model, "root")
        ET.SubElement(root_cell, "mxCell", id="0")
        ET.SubElement(root_cell, "mxCell", id="1", parent="0")
        
        # Add components based on analysis
        components = self._extract_components(analysis_data)
        y_pos = 100
        
        for i, component in enumerate(components):
            cell_id = f"component_{i}"
            
            # Create component cell with aesthetic styling
            cell = ET.SubElement(root_cell, "mxCell", 
                               id=cell_id, 
                               value=component["name"],
                               style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;shadow=1;fontSize=14;fontStyle=1",
                               vertex="1",
                               parent="1")
            
            # Add geometry
            geometry = ET.SubElement(cell, "mxGeometry", 
                                   x="200", y=str(y_pos), 
                                   width="200", height="80", 
                                   **{"as": "geometry"})
            
            y_pos += 120
        
        # Convert to string
        return ET.tostring(root, encoding='unicode')
    
    def generate_workflow_diagram(self, workflow_stages: List[str]) -> str:
        """Generate workflow process diagram."""
        
        root = ET.Element("mxfile", host="app.diagrams.net")
        diagram = ET.SubElement(root, "diagram", id="workflow", name="Workflow")
        
        graph_model = ET.SubElement(diagram, "mxGraphModel", 
                                   dx="1426", dy="827", grid="1", gridSize="10")
        
        root_cell = ET.SubElement(graph_model, "root")
        ET.SubElement(root_cell, "mxCell", id="0")
        ET.SubElement(root_cell, "mxCell", id="1", parent="0")
        
        # Add workflow stages
        x_pos = 100
        for i, stage in enumerate(workflow_stages):
            cell_id = f"stage_{i}"
            
            # Stage box with gradient
            cell = ET.SubElement(root_cell, "mxCell",
                               id=cell_id,
                               value=stage,
                               style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;shadow=1;gradientColor=#ffffff",
                               vertex="1",
                               parent="1")
            
            geometry = ET.SubElement(cell, "mxGeometry",
                                   x=str(x_pos), y="200",
                                   width="120", height="60",
                                   **{"as": "geometry"})
            
            # Add arrow to next stage
            if i < len(workflow_stages) - 1:
                arrow_id = f"arrow_{i}"
                arrow = ET.SubElement(root_cell, "mxCell",
                                    id=arrow_id,
                                    style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#666666",
                                    edge="1",
                                    parent="1",
                                    source=cell_id,
                                    target=f"stage_{i+1}")
                
                arrow_geom = ET.SubElement(arrow, "mxGeometry", relative="1", **{"as": "geometry"})
            
            x_pos += 180
        
        return ET.tostring(root, encoding='unicode')
    
    def _extract_components(self, analysis_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract system components from analysis data."""
        if analysis_data and "components" in analysis_data:
            return analysis_data["components"]
        
        # Return empty list if no components specified - let caller handle defaults
        return []
    
    def save_diagram(self, diagram_xml: str, filename: str) -> Path:
        """Save diagram XML to file."""
        filepath = self.templates_dir / f"{filename}.xml"
        filepath.write_text(diagram_xml, encoding='utf-8')
        return filepath