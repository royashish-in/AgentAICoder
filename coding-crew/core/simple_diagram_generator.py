"""Simple, working Draw.io diagram generator."""

import base64
import json
from typing import List, Dict, Any

class SimpleDiagramGenerator:
    """Generate simple, working Draw.io diagrams."""
    
    def generate_system_architecture(self, components: List[str]) -> str:
        """Generate basic system architecture diagram."""
        
        # Simple mxGraph JSON structure
        cells = [
            {"id": "0"},
            {"id": "1", "parent": "0"}
        ]
        
        # Add components as boxes
        for i, component in enumerate(components):
            cells.append({
                "id": f"comp_{i}",
                "value": component,
                "style": "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;",
                "vertex": True,
                "parent": "1",
                "geometry": {
                    "x": 50 + (i % 3) * 200,
                    "y": 50 + (i // 3) * 100,
                    "width": 150,
                    "height": 60
                }
            })
        
        # Create mxfile structure
        diagram_data = {
            "cells": cells
        }
        
        # Encode as Draw.io expects
        compressed = base64.b64encode(json.dumps(diagram_data).encode()).decode()
        
        return f"""<mxfile host="app.diagrams.net">
  <diagram name="Architecture">
    <mxGraphModel dx="1426" dy="827" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {self._generate_cells(components)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    
    def generate_workflow_diagram(self, stages: List[str]) -> str:
        """Generate simple workflow diagram."""
        
        return f"""<mxfile host="app.diagrams.net">
  <diagram name="Workflow">
    <mxGraphModel dx="1426" dy="827" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {self._generate_workflow_cells(stages)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    
    def _generate_cells(self, components: List[str]) -> str:
        """Generate XML cells for components."""
        cells_xml = ""
        
        for i, component in enumerate(components):
            x = 50 + (i % 3) * 200
            y = 50 + (i // 3) * 100
            
            cells_xml += f"""
        <mxCell id="comp_{i}" value="{component}" 
               style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" 
               vertex="1" parent="1">
          <mxGeometry x="{x}" y="{y}" width="150" height="60" as="geometry"/>
        </mxCell>"""
        
        return cells_xml
    
    def _generate_workflow_cells(self, stages: List[str]) -> str:
        """Generate XML cells for workflow stages."""
        cells_xml = ""
        
        for i, stage in enumerate(stages):
            x = 50 + i * 180
            
            cells_xml += f"""
        <mxCell id="stage_{i}" value="{stage}" 
               style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;" 
               vertex="1" parent="1">
          <mxGeometry x="{x}" y="100" width="120" height="60" as="geometry"/>
        </mxCell>"""
            
            # Add arrow to next stage
            if i < len(stages) - 1:
                cells_xml += f"""
        <mxCell id="arrow_{i}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;" 
               edge="1" parent="1" source="stage_{i}" target="stage_{i+1}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>"""
        
        return cells_xml