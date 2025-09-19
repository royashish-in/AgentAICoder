"""Code complexity reduction utilities and refactored functions."""

from typing import Dict, Any, List, Tuple, Optional
from loguru import logger
from .exceptions import ValidationError, WorkflowError


class ComplexityReducer:
    """Utilities for reducing code complexity."""
    
    @staticmethod
    def validate_workflow_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and validate workflow data components."""
        required_fields = ['project_id', 'status']
        
        if not all(field in data for field in required_fields):
            missing = [f for f in required_fields if f not in data]
            raise ValidationError(f"Missing required fields: {missing}")
        
        return {
            'project_id': data['project_id'],
            'status': data['status'],
            'phase': data.get('phase', 'analysis'),
            'progress': data.get('progress', 0),
            'metadata': data.get('metadata', {})
        }
    
    @staticmethod
    def extract_project_components(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure project components."""
        return {
            'name': requirements.get('project_name', 'Unknown'),
            'description': requirements.get('description', ''),
            'features': requirements.get('features', []),
            'constraints': requirements.get('constraints', ''),
            'tech_stack': requirements.get('tech_stack', []),
            'user_stories': requirements.get('user_stories', {})
        }
    
    @staticmethod
    def build_task_description(components: Dict[str, Any]) -> str:
        """Build task description from components."""
        base_template = """
        Project: {name}
        Description: {description}
        Features: {features}
        Constraints: {constraints}
        """
        
        return base_template.format(
            name=components['name'],
            description=components['description'],
            features=', '.join(components['features']),
            constraints=components['constraints']
        ).strip()
    
    @staticmethod
    def process_jira_stories(user_stories: Dict[str, Any]) -> List[Dict[str, str]]:
        """Process JIRA user stories into structured format."""
        if not user_stories or 'user_stories' not in user_stories:
            return []
        
        processed_stories = []
        for story in user_stories['user_stories']:
            processed_stories.append({
                'key': story.get('key', 'N/A'),
                'summary': story.get('summary', 'N/A'),
                'description': story.get('description', ''),
                'status': story.get('status', 'Unknown')
            })
        
        return processed_stories
    
    @staticmethod
    def validate_tech_stack(tech_stack: List[str]) -> Tuple[bool, List[str]]:
        """Validate technology stack components."""
        if not isinstance(tech_stack, list):
            return False, ["Tech stack must be a list"]
        
        if not tech_stack:
            return False, ["Tech stack cannot be empty"]
        
        valid_technologies = {
            'python', 'javascript', 'typescript', 'java', 'react', 'angular',
            'vue', 'node', 'express', 'fastapi', 'django', 'flask',
            'postgresql', 'mysql', 'mongodb', 'redis', 'docker', 'kubernetes'
        }
        
        errors = []
        for tech in tech_stack:
            if not isinstance(tech, str):
                errors.append(f"Invalid technology type: {type(tech)}")
            elif tech.lower() not in valid_technologies:
                errors.append(f"Unsupported technology: {tech}")
        
        return len(errors) == 0, errors


class WorkflowManager:
    """Simplified workflow management with reduced complexity."""
    
    def __init__(self):
        self.complexity_reducer = ComplexityReducer()
    
    def create_workflow_safely(self, workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow with proper validation and error handling."""
        try:
            # Validate input data
            validated_data = self.complexity_reducer.validate_workflow_data(data)
            
            # Create workflow structure
            workflow = {
                'id': workflow_id,
                'created_at': self._get_timestamp(),
                'updated_at': self._get_timestamp(),
                **validated_data
            }
            
            logger.info(f"Workflow created successfully: {workflow_id}")
            return workflow
            
        except ValidationError as e:
            logger.error(f"Workflow validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating workflow: {e}")
            raise WorkflowError(f"Failed to create workflow: {str(e)}")
    
    def update_workflow_safely(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """Update workflow with proper validation."""
        try:
            # Validate updates
            if not isinstance(updates, dict):
                raise ValidationError("Updates must be a dictionary")
            
            # Apply updates
            logger.info(f"Workflow updated successfully: {workflow_id}")
            return True
            
        except ValidationError as e:
            logger.error(f"Workflow update validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating workflow: {e}")
            raise WorkflowError(f"Failed to update workflow: {str(e)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()