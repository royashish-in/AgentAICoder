"""Tests for diagram generation utilities."""

import pytest
from core.diagram_generator import DiagramGenerator


class TestDiagramGenerator:
    """Test diagram generation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = DiagramGenerator()
    
    def test_generate_system_architecture(self):
        """Test system architecture diagram generation."""
        components = [
            {"name": "Web Frontend", "type": "ui"},
            {"name": "REST API", "type": "service"},
            {"name": "Core Logic", "type": "logic"},
            {"name": "PostgreSQL", "type": "storage"}
        ]
        
        diagram = self.generator.generate_system_architecture(components)
        
        assert "mxGraphModel" in diagram
        assert "Web Frontend" in diagram
        assert "shadow=1" in diagram
        assert "fillColor=" in diagram
    
    def test_generate_agent_workflow(self):
        """Test agent workflow diagram generation."""
        agents = ["Analysis Agent", "Review Agent", "Code Agent", "Test Agent"]
        
        diagram = self.generator.generate_agent_workflow(agents)
        
        assert "mxGraphModel" in diagram
        assert "Analysis Agent" in diagram
        assert "strokeWidth=2" in diagram
    
    def test_validate_diagram_quality(self):
        """Test diagram quality validation."""
        good_diagram = '''<mxGraphModel shadow="1">
            <mxCell fillColor="#dae8fc" strokeColor="#6c8ebf" rounded="1"/>
        </mxGraphModel>'''
        
        quality = self.generator.validate_diagram_quality(good_diagram)
        
        assert quality["has_shadows"] is True
        assert quality["has_gradients"] is True
        assert quality["has_rounded_corners"] is True
    
    def test_template_loading(self):
        """Test template file loading."""
        template = self.generator._load_template("system_architecture.xml")
        
        assert "mxGraphModel" in template
        assert "Frontend Layer" in template
        assert len(template) > 100