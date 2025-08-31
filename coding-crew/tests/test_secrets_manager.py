"""Retrospective tests for secrets manager."""

import pytest
import os
from unittest.mock import patch
from core.secrets_manager import SecretsManager

class TestSecretsManager:
    
    def test_get_secret_with_value(self):
        """Test getting secret that exists."""
        with patch.dict(os.environ, {'TEST_SECRET': 'secret_value'}):
            result = SecretsManager.get_secret('TEST_SECRET')
            assert result == 'secret_value'
    
    def test_get_secret_with_default(self):
        """Test getting secret with default value."""
        with patch.dict(os.environ, {}, clear=True):
            result = SecretsManager.get_secret('MISSING_SECRET', 'default')
            assert result == 'default'
    
    def test_get_required_secret_success(self):
        """Test getting required secret that exists."""
        with patch.dict(os.environ, {'REQUIRED_SECRET': 'value'}):
            result = SecretsManager.get_required_secret('REQUIRED_SECRET')
            assert result == 'value'
    
    def test_get_required_secret_missing(self):
        """Test getting required secret that doesn't exist."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Required secret 'MISSING' not found"):
                SecretsManager.get_required_secret('MISSING')
    
    def test_get_database_url_default(self):
        """Test database URL with default value."""
        with patch.dict(os.environ, {}, clear=True):
            result = SecretsManager.get_database_url()
            assert result == 'sqlite:///./app.db'
    
    def test_get_database_url_from_env(self):
        """Test database URL from environment."""
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}):
            result = SecretsManager.get_database_url()
            assert result == 'postgresql://test'
    
    def test_get_api_key(self):
        """Test API key retrieval."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test123'}):
            result = SecretsManager.get_api_key('openai')
            assert result == 'sk-test123'
    
    def test_get_ollama_config_defaults(self):
        """Test Ollama config with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = SecretsManager.get_ollama_config()
            assert config['base_url'] == 'http://localhost:11434'
            assert config['api_key'] == 'sk-fake-key'
    
    def test_get_ollama_config_from_env(self):
        """Test Ollama config from environment."""
        with patch.dict(os.environ, {
            'OLLAMA_BASE_URL': 'http://prod-ollama:11434',
            'OLLAMA_API_KEY': 'real-key'
        }):
            config = SecretsManager.get_ollama_config()
            assert config['base_url'] == 'http://prod-ollama:11434'
            assert config['api_key'] == 'real-key'