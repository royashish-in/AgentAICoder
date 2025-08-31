"""Secure secrets management."""

import os
from typing import Optional

class SecretsManager:
    """Manages secure loading of secrets from environment variables."""
    
    @staticmethod
    def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variables."""
        return os.getenv(key, default)
    
    @staticmethod
    def get_required_secret(key: str) -> str:
        """Get required secret, raise error if not found."""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required secret '{key}' not found in environment")
        return value
    
    @staticmethod
    def get_database_url() -> str:
        """Get database URL from environment."""
        return SecretsManager.get_secret('DATABASE_URL', 'sqlite:///./app.db')
    
    @staticmethod
    def get_api_key(service: str) -> Optional[str]:
        """Get API key for specific service."""
        key_name = f"{service.upper()}_API_KEY"
        return SecretsManager.get_secret(key_name)
    
    @staticmethod
    def get_ollama_config() -> dict:
        """Get Ollama configuration from environment."""
        return {
            'base_url': SecretsManager.get_secret('OLLAMA_BASE_URL', 'http://localhost:11434'),
            'api_key': SecretsManager.get_secret('OLLAMA_API_KEY', 'sk-fake-key')
        }

# Global secrets instance
secrets = SecretsManager()