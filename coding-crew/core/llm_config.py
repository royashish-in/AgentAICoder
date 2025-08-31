"""LLM configuration for CrewAI with Ollama."""

from langchain_ollama import ChatOllama
from typing import Dict, Any
import yaml
import os


def load_config() -> Dict[str, Any]:
    """Load configuration from settings.yaml."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def get_ollama_llm(model_name: str) -> ChatOllama:
    """Get configured Ollama LLM instance."""
    config = load_config()
    ollama_config = config['ollama']
    
    return ChatOllama(
        model=model_name,  # Keep ollama/ prefix for CrewAI
        base_url=ollama_config['base_url'],
        temperature=0.1,
        num_predict=2048,
    )


# Pre-configured LLM instances
def get_analysis_llm() -> ChatOllama:
    """Get LLM for analysis tasks."""
    config = load_config()
    return get_ollama_llm(config['ollama']['models']['analysis'])


def get_coding_llm() -> ChatOllama:
    """Get LLM for coding tasks."""
    config = load_config()
    return get_ollama_llm(config['ollama']['models']['coding'])


def get_review_llm() -> ChatOllama:
    """Get LLM for review tasks."""
    config = load_config()
    return get_ollama_llm(config['ollama']['models']['review'])


def get_testing_llm() -> ChatOllama:
    """Get LLM for testing tasks."""
    config = load_config()
    return get_ollama_llm(config['ollama']['models']['testing'])


def get_documentation_llm() -> ChatOllama:
    """Get LLM for documentation tasks."""
    config = load_config()
    return get_ollama_llm(config['ollama']['models']['documentation'])