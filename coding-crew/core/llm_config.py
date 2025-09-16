"""LLM configuration for CrewAI with Ollama and Hugging Face support."""

from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFacePipeline
from typing import Dict, Any, Union
import yaml
import os


_config_cache = None

def load_config() -> Dict[str, Any]:
    """Load configuration from settings.yaml with caching."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")
    try:
        with open(config_path, 'r') as file:
            _config_cache = yaml.safe_load(file)
            return _config_cache
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {e}")


def get_llm(model_name: str) -> Union[ChatOllama, HuggingFacePipeline]:
    """Get configured LLM instance (Ollama or Hugging Face)."""
    config = load_config()
    provider = config.get('llm_provider', 'ollama')
    
    if provider == 'huggingface':
        return get_huggingface_llm(model_name)
    else:
        return get_ollama_llm(model_name)

def get_ollama_llm(model_name: str) -> ChatOllama:
    """Get configured Ollama LLM instance."""
    config = load_config()
    ollama_config = config['ollama']
    
    return ChatOllama(
        model=model_name,
        base_url=ollama_config['base_url'],
        temperature=0.1,
        num_predict=2048,
    )

def get_huggingface_llm(model_name: str) -> HuggingFacePipeline:
    """Get configured Hugging Face LLM instance."""
    config = load_config()
    hf_config = config.get('huggingface', {})
    
    return HuggingFacePipeline.from_model_id(
        model_id=model_name,
        task="text-generation",
        model_kwargs={"temperature": 0.1, "max_length": 2048},
        device=hf_config.get('device', 'auto')
    )


# Pre-configured LLM instances
def get_analysis_llm():
    """Get LLM for analysis tasks."""
    config = load_config()
    provider = config.get('llm_provider', 'ollama')
    model_key = 'analysis'
    
    try:
        if provider == 'huggingface':
            models = config.get('huggingface', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in huggingface config")
            return get_llm(models[model_key])
        else:
            models = config.get('ollama', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in ollama config")
            return get_llm(models[model_key])
    except KeyError as e:
        raise ValueError(f"Configuration error: {e}")

def get_coding_llm():
    """Get LLM for coding tasks."""
    config = load_config()
    provider = config.get('llm_provider', 'ollama')
    model_key = 'coding'
    
    try:
        if provider == 'huggingface':
            models = config.get('huggingface', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in huggingface config")
            return get_llm(models[model_key])
        else:
            models = config.get('ollama', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in ollama config")
            return get_llm(models[model_key])
    except KeyError as e:
        raise ValueError(f"Configuration error: {e}")

def get_review_llm():
    """Get LLM for review tasks."""
    config = load_config()
    provider = config.get('llm_provider', 'ollama')
    model_key = 'review'
    
    try:
        if provider == 'huggingface':
            models = config.get('huggingface', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in huggingface config")
            return get_llm(models[model_key])
        else:
            models = config.get('ollama', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in ollama config")
            return get_llm(models[model_key])
    except KeyError as e:
        raise ValueError(f"Configuration error: {e}")

def get_testing_llm():
    """Get LLM for testing tasks."""
    config = load_config()
    provider = config.get('llm_provider', 'ollama')
    model_key = 'testing'
    
    try:
        if provider == 'huggingface':
            models = config.get('huggingface', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in huggingface config")
            return get_llm(models[model_key])
        else:
            models = config.get('ollama', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in ollama config")
            return get_llm(models[model_key])
    except KeyError as e:
        raise ValueError(f"Configuration error: {e}")

def get_documentation_llm():
    """Get LLM for documentation tasks."""
    config = load_config()
    provider = config.get('llm_provider', 'ollama')
    model_key = 'documentation'
    
    try:
        if provider == 'huggingface':
            models = config.get('huggingface', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in huggingface config")
            return get_llm(models[model_key])
        else:
            models = config.get('ollama', {}).get('models', {})
            if model_key not in models:
                raise KeyError(f"Model '{model_key}' not found in ollama config")
            return get_llm(models[model_key])
    except KeyError as e:
        raise ValueError(f"Configuration error: {e}")