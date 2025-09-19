"""Input sanitization and security framework."""

import html
import re
import bleach
from typing import Any, Dict, List, Union
from loguru import logger


class InputSanitizer:
    """Comprehensive input sanitization for all user inputs."""
    
    ALLOWED_HTML_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    ALLOWED_ATTRIBUTES = {}
    
    @staticmethod
    def sanitize_html(input_text: str) -> str:
        """Sanitize HTML content to prevent XSS."""
        if not isinstance(input_text, str):
            return str(input_text)
        
        # Use bleach for comprehensive HTML sanitization
        cleaned = bleach.clean(
            input_text,
            tags=InputSanitizer.ALLOWED_HTML_TAGS,
            attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
            strip=True
        )
        return cleaned
    
    @staticmethod
    def sanitize_project_name(name: str) -> str:
        """Sanitize project names for safe file system usage."""
        if not isinstance(name, str):
            raise ValueError("Project name must be a string")
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        sanitized = re.sub(r'\.{2,}', '.', sanitized)  # Prevent path traversal
        sanitized = sanitized.strip('. ')  # Remove leading/trailing dots and spaces
        
        if not sanitized:
            raise ValueError("Project name cannot be empty after sanitization")
        
        return sanitized
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary values."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_html(value)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = InputSanitizer.sanitize_list(value)
            else:
                sanitized[key] = value
        return sanitized
    
    @staticmethod
    def sanitize_list(data: List[Any]) -> List[Any]:
        """Recursively sanitize list values."""
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(InputSanitizer.sanitize_html(item))
            elif isinstance(item, dict):
                sanitized.append(InputSanitizer.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(InputSanitizer.sanitize_list(item))
            else:
                sanitized.append(item)
        return sanitized
    
    @staticmethod
    def validate_project_id(project_id: str) -> bool:
        """Validate project ID format."""
        if not isinstance(project_id, str):
            return False
        
        # Allow alphanumeric, hyphens, and underscores only
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, project_id)) and len(project_id) <= 100


class SecurityValidator:
    """Security validation utilities."""
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_dirs: List[str]) -> bool:
        """Validate file paths to prevent directory traversal."""
        import os
        
        try:
            # Normalize the path
            normalized = os.path.normpath(file_path)
            
            # Check for path traversal attempts
            if '..' in normalized or normalized.startswith('/'):
                return False
            
            # Check if path starts with allowed directories
            return any(normalized.startswith(allowed_dir) for allowed_dir in allowed_dirs)
        
        except Exception:
            return False
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate JSON structure has required fields."""
        try:
            return all(field in data for field in required_fields)
        except Exception:
            return False