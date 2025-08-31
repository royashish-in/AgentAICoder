"""Development phase agents for code generation and review."""

from crewai import Agent
from core.llm_config import get_llm_config

def create_coding_agent():
    """Create coding agent for code generation."""
    llm_config = get_llm_config()
    
    return Agent(
        role="Senior Software Developer",
        goal="Generate high-quality, production-ready code based on approved system architecture",
        backstory="""You are an experienced software developer with expertise in multiple 
        programming languages and frameworks. You excel at translating system designs 
        into clean, maintainable, and well-structured code.""",
        verbose=True,
        allow_delegation=False,
        llm=llm_config["coding"]
    )

def create_code_review_agent():
    """Create code review agent for quality assurance."""
    llm_config = get_llm_config()
    
    return Agent(
        role="Senior Code Reviewer & Quality Assurance Engineer",
        goal="Review generated code for quality, security, performance, and best practices",
        backstory="""You are a meticulous code reviewer with deep knowledge of software 
        engineering best practices, security vulnerabilities, and performance optimization. 
        You provide constructive feedback to improve code quality.""",
        verbose=True,
        allow_delegation=False,
        llm=llm_config["review"]
    )