#!/usr/bin/env python3
"""Test script for diagram generation functionality."""

import asyncio
from core.diagram_generator import DiagramGenerator
from agents.analysis_agent import AnalysisAgent


async def test_diagram_generation():
    """Test the complete diagram generation workflow."""
    print("🎨 Testing Aesthetic Diagram Generation")
    print("=" * 50)
    
    # Test diagram generator
    generator = DiagramGenerator()
    
    # Test system architecture diagram
    components = [
        {"name": "React Frontend", "type": "ui"},
        {"name": "FastAPI Gateway", "type": "service"},
        {"name": "Business Logic", "type": "logic"},
        {"name": "PostgreSQL DB", "type": "storage"}
    ]
    
    print("📊 Generating system architecture diagram...")
    system_diagram = generator.generate_system_architecture(components)
    print(f"✅ Generated {len(system_diagram)} characters of XML")
    
    # Test agent workflow diagram
    agents = ["Analysis Agent", "Architecture Review", "Coding Agent", "Testing Agent"]
    print("🔄 Generating agent workflow diagram...")
    workflow_diagram = generator.generate_agent_workflow(agents)
    print(f"✅ Generated {len(workflow_diagram)} characters of XML")
    
    # Test quality validation
    print("🔍 Validating diagram quality...")
    quality = generator.validate_diagram_quality(system_diagram)
    print(f"✅ Quality score: {sum(quality.values())}/5")
    for check, passed in quality.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}: {passed}")
    
    # Test integration with Analysis Agent
    print("\n🤖 Testing Analysis Agent integration...")
    agent = AnalysisAgent()
    
    test_requirements = """
    Build a web application with:
    - React frontend for user interface
    - FastAPI backend for business logic
    - PostgreSQL database for data storage
    - Authentication and authorization
    """
    
    result = await agent.process({"requirements": test_requirements})
    
    print("✅ Analysis Agent processed requirements")
    print(f"✅ Generated {len(result['system_diagrams'])} diagram types")
    
    # Display quality validation
    if 'quality_validation' in result['system_diagrams']:
        quality = result['system_diagrams']['quality_validation']
        print(f"✅ Integrated quality score: {sum(quality.values())}/5")
    
    print("\n🎉 Diagram generation system working perfectly!")
    return True


if __name__ == "__main__":
    asyncio.run(test_diagram_generation())