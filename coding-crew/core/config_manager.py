"""Configuration management with environment-aware loading."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages environment-aware configuration loading."""
    
    def __init__(self):
        self._config: Optional[Dict[str, Any]] = None
        self._environment = os.getenv('ENVIRONMENT', 'development').lower()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration for current environment."""
        if self._config is None:
            config_dir = Path(__file__).parent.parent / "config"
            config_file = config_dir / f"{self._environment}.yaml"
            
            try:
                with open(config_file, 'r') as f:
                    self._config = yaml.safe_load(f)
                self._config = self._substitute_env_vars(self._config)
            except Exception:
                self._config = self._get_default_config()
        
        return self._config
    
    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute environment variables in config."""
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            var_expr = config[2:-1]
            if ':-' in var_expr:
                var_name, default_value = var_expr.split(':-', 1)
                return os.getenv(var_name, default_value)
            return os.getenv(var_expr, config)
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "environment": self._environment,
            "llm": {"provider": "ollama", "base_url": "http://localhost:11434"},
            "web": {"host": "127.0.0.1", "port": 8000},
            "workflow": {"max_iterations": {"development": 3}},
            "logging": {"level": "INFO"}
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key path."""
        config = self.load_config()
        keys = key_path.split('.')
        
        value = config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

# Global configuration instance
config = ConfigManager()