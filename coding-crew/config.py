"""Configuration settings for AgentAI system."""

import re
from typing import Dict, List, Any

class Config:
    """Configuration class for AgentAI system."""
    
    # Workflow phases and progress
    WORKFLOW_PHASES = {
        "requirements": {"name": "Requirements Analysis", "progress": 10},
        "approval": {"name": "Human Approval", "progress": 50},
        "development": {"name": "Development", "progress": 75},
        "testing": {"name": "Testing", "progress": 85},
        "deployment": {"name": "Deployment", "progress": 100}
    }
    
    # Timing delays (in seconds)
    DELAYS = {
        "analysis": 2,
        "rework": 3,
        "code_generation": 5,
        "testing": 3
    }
    
    # Default fallback values
    FALLBACK = {
        "tech_stack": ["Python"],
        "timeline": "2-4 weeks"
    }
    
    # Status strings
    STATUS = {
        "analyzing": "analyzing",
        "analysis_complete": "analysis_complete",
        "development": "development",
        "testing": "testing",
        "completed": "completed",
        "pending": "pending",
        "approved": "approved",
        "rejected": "rejected",
        "rework": "rework"
    }
    
    # Actor names
    ACTORS = {
        "human": "Human Reviewer",
        "ai_system": "AI System (CrewAI)",
        "fallback": "Fallback System"
    }
    
    # UI Configuration
    UI = {
        "refresh_interval": 3000,
        "form_defaults": {
            "target_users": "developers",
            "scale": "small"
        }
    }
    
    # Ollama Configuration
    OLLAMA = {
        "model": "ollama/llama3.1:8b",
        "base_url": "http://localhost:11434"
    }
    
    # Server Configuration
    SERVER = {
        "host": "0.0.0.0",
        "port": 8001
    }

def extract_tech_stack_from_analysis(analysis_text: str) -> List[str]:
    """Extract technology stack from AI analysis text."""
    tech_patterns = [
        r'(?i)technology\s+stack[:\s]*([^\n]+)',
        r'(?i)recommended\s+technologies[:\s]*([^\n]+)',
        r'(?i)tech\s+stack[:\s]*([^\n]+)',
        r'(?i)technologies[:\s]*([^\n]+)'
    ]
    
    technologies = set()
    
    # Common technology keywords to look for
    tech_keywords = {
        'python', 'javascript', 'typescript', 'java', 'c#', 'go', 'rust',
        'react', 'vue', 'angular', 'fastapi', 'django', 'flask', 'express',
        'postgresql', 'mysql', 'mongodb', 'redis', 'sqlite',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp',
        'pytest', 'jest', 'junit', 'mocha'
    }
    
    # Extract from patterns
    for pattern in tech_patterns:
        matches = re.findall(pattern, analysis_text)
        for match in matches:
            words = re.findall(r'\b\w+\b', match.lower())
            technologies.update(word.title() for word in words if word in tech_keywords)
    
    # Scan entire text for tech keywords
    words = re.findall(r'\b\w+\b', analysis_text.lower())
    technologies.update(word.title() for word in words if word in tech_keywords)
    
    return list(technologies) if technologies else Config.FALLBACK["tech_stack"]

def extract_timeline_from_analysis(analysis_text: str) -> str:
    """Extract timeline estimate from AI analysis text."""
    timeline_patterns = [
        r'(?i)timeline[:\s]*([^\n]+)',
        r'(?i)estimated\s+time[:\s]*([^\n]+)',
        r'(?i)duration[:\s]*([^\n]+)',
        r'(?i)(\d+[-–]\d+\s+(?:weeks?|months?))',
        r'(?i)(\d+\s+(?:weeks?|months?))'
    ]
    
    for pattern in timeline_patterns:
        matches = re.findall(pattern, analysis_text)
        if matches:
            return matches[0].strip()
    
    return Config.FALLBACK["timeline"]

def get_workflow_config() -> Dict[str, Any]:
    """Get workflow configuration."""
    return Config.WORKFLOW_PHASES

def get_delays_config() -> Dict[str, int]:
    """Get timing delays configuration."""
    return Config.DELAYS

def get_status_config() -> Dict[str, str]:
    """Get status strings configuration."""
    return Config.STATUS

def get_actors_config() -> Dict[str, str]:
    """Get actor names configuration."""
    return Config.ACTORS

def get_ui_config() -> Dict[str, Any]:
    """Get UI configuration."""
    return Config.UI

def get_ollama_config() -> Dict[str, str]:
    """Get Ollama configuration."""
    return Config.OLLAMA

def extract_diagrams_from_analysis(analysis_text: str) -> List[str]:
    """Generate diagrams from analysis content."""
    from core.simple_diagram_generator import SimpleDiagramGenerator
    
    generator = SimpleDiagramGenerator()
    diagrams = []
    
    # Extract components and create architecture diagram
    tech_stack = extract_tech_stack_from_analysis(analysis_text)
    if tech_stack:
        arch_diagram = generator.generate_system_architecture(tech_stack)
        diagrams.append(arch_diagram)
    
    # Create workflow diagram
    workflow_stages = ["Analysis", "Development", "Testing", "Deployment"]
    workflow_diagram = generator.generate_workflow_diagram(workflow_stages)
    diagrams.append(workflow_diagram)
    
    return diagrams

def get_server_config() -> Dict[str, Any]:
    """Get server configuration."""
    return Config.SERVER