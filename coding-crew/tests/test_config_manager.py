"""Tests for configuration manager."""

import pytest
import os
from unittest.mock import patch, mock_open
from core.config_manager import ConfigManager

class TestConfigManager:
    
    def test_environment_detection_default(self):
        """Test default environment detection."""
        with patch.dict(os.environ, {}, clear=True):
            manager = ConfigManager()
            assert manager._environment == 'development'
    
    def test_environment_detection_from_env(self):
        """Test environment detection from environment variable."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            manager = ConfigManager()
            assert manager._environment == 'production'
    
    def test_config_loading_default(self):
        """Test loading default configuration."""
        manager = ConfigManager()
        config = manager._get_default_config()
        
        assert config['environment'] == manager._environment
        assert 'llm' in config
        assert 'web' in config
        assert config['llm']['provider'] == 'ollama'
    
    def test_env_var_substitution_with_default(self):
        """Test environment variable substitution with default value."""
        manager = ConfigManager()
        
        # Test ${VAR:-default} format
        config = {'test_key': '${TEST_VAR:-default_value}'}
        result = manager._substitute_env_vars(config)
        
        assert result['test_key'] == 'default_value'
    
    def test_env_var_substitution_with_env_value(self):
        """Test environment variable substitution with actual env value."""
        manager = ConfigManager()
        
        with patch.dict(os.environ, {'TEST_VAR': 'env_value'}):
            config = {'test_key': '${TEST_VAR:-default_value}'}
            result = manager._substitute_env_vars(config)
            
            assert result['test_key'] == 'env_value'
    
    def test_get_config_value_by_path(self):
        """Test getting configuration value by dot-separated path."""
        manager = ConfigManager()
        manager._config = {
            'llm': {
                'provider': 'ollama',
                'base_url': 'http://localhost:11434'
            }
        }
        
        assert manager.get('llm.provider') == 'ollama'
        assert manager.get('llm.base_url') == 'http://localhost:11434'
        assert manager.get('nonexistent.key', 'default') == 'default'
    
    def test_nested_env_var_substitution(self):
        """Test nested environment variable substitution."""
        manager = ConfigManager()
        
        config = {
            'database': {
                'host': '${DB_HOST:-localhost}',
                'port': '${DB_PORT:-5432}'
            }
        }
        
        with patch.dict(os.environ, {'DB_HOST': 'prod-db'}):
            result = manager._substitute_env_vars(config)
            
            assert result['database']['host'] == 'prod-db'
            assert result['database']['port'] == '5432'  # default value