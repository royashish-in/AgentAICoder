"""Documentation phase agents."""

from crewai import Agent
from core.llm_config import get_llm_config

def create_documentation_agent():
    """Create documentation agent."""
    llm_config = get_llm_config()
    
    return Agent(
        role="Technical Documentation Specialist",
        goal="Generate comprehensive project documentation including API docs, user guides, and technical specifications",
        backstory="""You are an expert technical writer who creates clear, comprehensive 
        documentation for software projects. You excel at making complex technical 
        concepts accessible to different audiences.""",
        verbose=True,
        allow_delegation=False,
        llm=llm_config["documentation"]
    )