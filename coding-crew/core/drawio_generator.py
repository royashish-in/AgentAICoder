"""Professional draw.io XML diagram generator with aesthetic styling."""

from typing import Dict, List, Any
import uuid


class DrawIOGenerator:
    """Generate aesthetic draw.io XML diagrams."""
    
    def __init__(self):
        self.colors = {
            'primary': '#4A90E2',
            'secondary': '#7ED321', 
            'accent': '#F5A623',
            'danger': '#D0021B',
            'dark': '#4A4A4A',
            'light': '#F8F9FA'
        }
        
        self.gradients = {
            'blue': 'gradientColor=#E3F2FD;gradientDirection=north',
            'green': 'gradientColor=#E8F5E8;gradientDirection=north',
            'orange': 'gradientColor=#FFF3E0;gradientDirection=north'
        }
    
    def create_system_architecture(self, components: List[str]) -> str:
        """Create professional system architecture diagram."""
        
        # Calculate positions
        positions = self._calculate_positions(len(components))
        
        # Generate cells
        cells = ['<mxCell id="0"/>']
        cells.append('<mxCell id="1" parent="0"/>')
        
        # Add components
        for i, component in enumerate(components):
            cell_id = str(uuid.uuid4())
            x, y = positions[i]
            
            style = (
                f"rounded=1;whiteSpace=wrap;html=1;"
                f"fillColor={self.colors['primary']};"
                f"{self.gradients['blue']};"
                f"strokeColor=#1976D2;strokeWidth=2;"
                f"shadow=1;fontSize=14;fontColor=white;fontStyle=1"
            )
            
            cells.append(
                f'<mxCell id="{cell_id}" value="{component}" '
                f'style="{style}" vertex="1" parent="1">'
                f'<mxGeometry x="{x}" y="{y}" width="120" height="60" as="geometry"/>'
                f'</mxCell>'
            )
        
        # Add connections
        if len(components) > 1:
            for i in range(len(components) - 1):
                conn_id = str(uuid.uuid4())
                source_id = cells[i + 2].split('"')[1]  # Extract ID
                target_id = cells[i + 3].split('"')[1]
                
                conn_style = (
                    f"edgeStyle=orthogonalEdgeStyle;rounded=1;"
                    f"orthogonalLoop=1;jettySize=auto;html=1;"
                    f"strokeColor={self.colors['dark']};strokeWidth=2;"
                    f"endArrow=classic;endFill=1"
                )
                
                cells.append(
                    f'<mxCell id="{conn_id}" style="{conn_style}" '
                    f'edge="1" parent="1" source="{source_id}" target="{target_id}"/>'
                )
        
        return self._wrap_diagram(cells)
    
    def create_component_diagram(self, components: Dict[str, List[str]]) -> str:
        """Create component relationship diagram."""
        cells = ['<mxCell id="0"/>']
        cells.append('<mxCell id="1" parent="0"/>')
        
        y_offset = 50
        component_ids = {}
        
        # Create component groups
        for comp_name, features in components.items():
            # Main component
            comp_id = str(uuid.uuid4())
            component_ids[comp_name] = comp_id
            
            style = (
                f"swimlane;fontStyle=1;align=center;verticalAlign=top;"
                f"childLayout=stackLayout;horizontal=1;startSize=26;"
                f"horizontalStack=0;resizeParent=1;resizeParentMax=0;"
                f"resizeLast=0;collapsible=1;marginBottom=0;"
                f"fillColor={self.colors['secondary']};"
                f"{self.gradients['green']};"
                f"strokeColor=#388E3C;strokeWidth=2;shadow=1"
            )
            
            height = 26 + (len(features) * 26)
            cells.append(
                f'<mxCell id="{comp_id}" value="{comp_name}" '
                f'style="{style}" vertex="1" parent="1">'
                f'<mxGeometry x="50" y="{y_offset}" width="200" height="{height}" as="geometry"/>'
                f'</mxCell>'
            )
            
            # Add features
            for j, feature in enumerate(features):
                feature_id = str(uuid.uuid4())
                feature_style = (
                    f"text;strokeColor=none;fillColor=none;align=left;"
                    f"verticalAlign=top;spacingLeft=4;spacingRight=4;"
                    f"overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];"
                    f"portConstraint=eastwest;fontSize=12"
                )
                
                cells.append(
                    f'<mxCell id="{feature_id}" value="• {feature}" '
                    f'style="{feature_style}" vertex="1" parent="{comp_id}">'
                    f'<mxGeometry y="{26 + j * 26}" width="200" height="26" as="geometry"/>'
                    f'</mxCell>'
                )
            
            y_offset += height + 50
        
        return self._wrap_diagram(cells)
    
    def create_data_flow_diagram(self, flow_steps: List[Dict[str, str]]) -> str:
        """Create data flow diagram with process steps."""
        cells = ['<mxCell id="0"/>']
        cells.append('<mxCell id="1" parent="0"/>')
        
        step_ids = []
        
        # Create flow steps
        for i, step in enumerate(flow_steps):
            step_id = str(uuid.uuid4())
            step_ids.append(step_id)
            
            x = 50 + (i * 200)
            y = 100
            
            # Different shapes for different step types
            if step.get('type') == 'start':
                style = (
                    f"ellipse;whiteSpace=wrap;html=1;"
                    f"fillColor={self.colors['accent']};"
                    f"{self.gradients['orange']};"
                    f"strokeColor=#F57C00;strokeWidth=2;shadow=1;"
                    f"fontSize=12;fontStyle=1"
                )
            elif step.get('type') == 'process':
                style = (
                    f"rounded=1;whiteSpace=wrap;html=1;"
                    f"fillColor={self.colors['primary']};"
                    f"{self.gradients['blue']};"
                    f"strokeColor=#1976D2;strokeWidth=2;shadow=1;"
                    f"fontSize=12;fontColor=white;fontStyle=1"
                )
            else:  # end or default
                style = (
                    f"ellipse;whiteSpace=wrap;html=1;"
                    f"fillColor={self.colors['danger']};"
                    f"strokeColor=#C62828;strokeWidth=2;shadow=1;"
                    f"fontSize=12;fontColor=white;fontStyle=1"
                )
            
            cells.append(
                f'<mxCell id="{step_id}" value="{step["name"]}" '
                f'style="{style}" vertex="1" parent="1">'
                f'<mxGeometry x="{x}" y="{y}" width="120" height="60" as="geometry"/>'
                f'</mxCell>'
            )
        
        # Add flow arrows
        for i in range(len(step_ids) - 1):
            arrow_id = str(uuid.uuid4())
            arrow_style = (
                f"edgeStyle=orthogonalEdgeStyle;rounded=1;"
                f"orthogonalLoop=1;jettySize=auto;html=1;"
                f"strokeColor={self.colors['dark']};strokeWidth=3;"
                f"endArrow=classic;endFill=1;shadow=1"
            )
            
            cells.append(
                f'<mxCell id="{arrow_id}" style="{arrow_style}" '
                f'edge="1" parent="1" source="{step_ids[i]}" target="{step_ids[i+1]}"/>'
            )
        
        return self._wrap_diagram(cells)
    
    def _calculate_positions(self, count: int) -> List[tuple]:
        """Calculate optimal positions for components."""
        positions = []
        
        if count <= 3:
            # Horizontal layout
            for i in range(count):
                x = 50 + (i * 200)
                y = 100
                positions.append((x, y))
        else:
            # Grid layout
            cols = 2
            for i in range(count):
                row = i // cols
                col = i % cols
                x = 50 + (col * 200)
                y = 50 + (row * 150)
                positions.append((x, y))
        
        return positions
    
    def _wrap_diagram(self, cells: List[str]) -> str:
        """Wrap cells in proper draw.io XML structure."""
        cells_xml = '\n    '.join(cells)
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="Coding Crew Generator" version="22.1.11">
  <diagram name="System Architecture" id="system-arch">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="1">
      <root>
        {cells_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''