#!/usr/bin/env python3
"""Test XML validation for draw.io diagrams."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.analysis_crew import AnalysisCrew

def test_xml_validation():
    """Test the XML validation functionality."""
    crew = AnalysisCrew()
    
    # Test valid XML
    valid_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram name="Test">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Component" style="rounded=1;fillColor=#dae8fc;" vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    
    # Test invalid XML
    invalid_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<diagram>
  <nodes>
    <node id="1" x="100" y="50">
      <label>Invalid Format</label>
    </node>
  </nodes>
</diagram>'''
    
    print("Testing XML validation...")
    print(f"Valid XML passes: {crew._validate_drawio_xml(valid_xml)}")
    print(f"Invalid XML fails: {not crew._validate_drawio_xml(invalid_xml)}")
    
    # Test a simple requirements analysis
    test_requirements = {
        "project_name": "XML Test Project",
        "description": "Test project for XML validation",
        "target_users": "developers",
        "scale": "small",
        "features": ["basic functionality"],
        "constraints": "none"
    }
    
    print("\nRunning analysis with XML validation...")
    try:
        result = crew.analyze_requirements(test_requirements)
        print("Analysis completed successfully")
        
        # Check if diagrams were extracted
        diagrams = crew._extract_diagrams(result)
        print(f"Number of valid diagrams extracted: {len(diagrams)}")
        
        if diagrams:
            print("First diagram preview:")
            print(diagrams[0][:200] + "..." if len(diagrams[0]) > 200 else diagrams[0])
        
    except Exception as e:
        print(f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    test_xml_validation()