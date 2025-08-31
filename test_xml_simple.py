#!/usr/bin/env python3
"""Simple XML validation test without dependencies."""

import xml.etree.ElementTree as ET

def validate_drawio_xml(xml_content: str) -> bool:
    """Validate draw.io XML structure."""
    try:
        # Parse XML to check basic structure
        root = ET.fromstring(xml_content)
        
        # Check required elements
        if root.tag != 'mxfile':
            print(f"❌ Root tag is '{root.tag}', expected 'mxfile'")
            return False
        
        diagram = root.find('diagram')
        if diagram is None:
            print("❌ No 'diagram' element found")
            return False
        
        model = diagram.find('mxGraphModel')
        if model is None:
            print("❌ No 'mxGraphModel' element found")
            return False
        
        root_elem = model.find('root')
        if root_elem is None:
            print("❌ No 'root' element found")
            return False
        
        # Check for required root cells
        cells = root_elem.findall('mxCell')
        if len(cells) < 2:
            print(f"❌ Only {len(cells)} cells found, need at least 2")
            return False
        
        print(f"✅ Valid draw.io XML with {len(cells)} cells")
        return True
        
    except Exception as e:
        print(f"❌ XML parsing failed: {str(e)}")
        return False

# Test XML from generated project
test_xml = '''<mxfile host="app.diagrams.net">
  <diagram name="System Architecture">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0" value="PyRead Application"/>
        <mxCell id="2" value="Web Scraper" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="3" value="Article Title Extractor" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="250" y="100" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="4" value="Console Printer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="400" y="100" width="120" height="60" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

print("Testing draw.io XML from generated project:")
validate_drawio_xml(test_xml)