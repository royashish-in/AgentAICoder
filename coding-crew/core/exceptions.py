"""Custom exception classes for specific error handling."""

from typing import Optional, Dict, Any


class AgentAIException(Exception):
    """Base exception for AgentAI platform."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class ValidationError(AgentAIException):
    """Raised when input validation fails."""
    pass


class SecurityError(AgentAIException):
    """Raised when security validation fails."""
    pass


class ProjectError(AgentAIException):
    """Base class for project-related errors."""
    pass


class ProjectNotFoundError(ProjectError):
    """Raised when project is not found."""
    pass


class ProjectCreationError(ProjectError):
    """Raised when project creation fails."""
    pass


class WorkflowError(AgentAIException):
    """Base class for workflow-related errors."""
    pass


class WorkflowExecutionError(WorkflowError):
    """Raised when workflow execution fails."""
    pass


class WorkflowValidationError(WorkflowError):
    """Raised when workflow validation fails."""
    pass


class AIAgentError(AgentAIException):
    """Base class for AI agent errors."""
    pass


class LLMConnectionError(AIAgentError):
    """Raised when LLM connection fails."""
    pass


class AgentExecutionError(AIAgentError):
    """Raised when agent execution fails."""
    pass


class FileSystemError(AgentAIException):
    """Base class for file system errors."""
    pass


class FileNotFoundError(FileSystemError):
    """Raised when file is not found."""
    pass


class FilePermissionError(FileSystemError):
    """Raised when file permission is denied."""
    pass


class JIRAIntegrationError(AgentAIException):
    """Base class for JIRA integration errors."""
    pass


class JIRAConnectionError(JIRAIntegrationError):
    """Raised when JIRA connection fails."""
    pass


class JIRAAuthenticationError(JIRAIntegrationError):
    """Raised when JIRA authentication fails."""
    pass


class MCPIntegrationError(AgentAIException):
    """Base class for MCP integration errors."""
    pass


class MCPConnectionError(MCPIntegrationError):
    """Raised when MCP connection fails."""
    pass


class MCPProtocolError(MCPIntegrationError):
    """Raised when MCP protocol error occurs."""
    pass