# MCP Integration for AgentAI

This document describes how to integrate Model Context Protocol (MCP) servers for JIRA and GitHub with AgentAI.

## Overview

The MCP integration allows AgentAI to:
- Query JIRA for existing project context and requirements
- Search GitHub for similar projects and code patterns
- Create JIRA issues for project tracking
- Create GitHub repositories for code hosting

## Setup

### 1. Environment Configuration

Copy the MCP environment template:
```bash
cp coding-crew/.env.mcp.example coding-crew/.env.mcp
```

Edit the configuration:
```bash
# Enable MCP integration
MCP_ENABLED=true

# JIRA MCP Server
JIRA_MCP_URL=http://localhost:3001
JIRA_TOKEN=your_jira_api_token
JIRA_PROJECT=DEV

# GitHub MCP Server  
GITHUB_MCP_URL=http://localhost:3002
GITHUB_TOKEN=your_github_token
GITHUB_ORG=your_organization
```

### 2. MCP Server Setup

You need to run MCP servers for JIRA and GitHub. These are separate services that implement the MCP protocol.

#### JIRA MCP Server
```bash
# Example MCP server for JIRA
# This would be a separate service implementing MCP protocol
npm install -g @modelcontextprotocol/jira-server
mcp-jira-server --port 3001 --jira-url https://your-domain.atlassian.net
```

#### GitHub MCP Server
```bash
# Example MCP server for GitHub
# This would be a separate service implementing MCP protocol
npm install -g @modelcontextprotocol/github-server
mcp-github-server --port 3002
```

### 3. Load Environment Variables

Add to your shell profile or load manually:
```bash
source coding-crew/.env.mcp
```

## Usage

### Enhanced Project Creation

When MCP is enabled, AgentAI will:

1. **Context Gathering**: Query JIRA and GitHub for existing project context
2. **Enhanced Analysis**: Use external context to improve requirements analysis
3. **Artifact Creation**: Create JIRA issues and GitHub repositories automatically

### API Integration

The MCP integration is automatically used when:
- Creating new projects via the web interface
- Running the enhanced workflow orchestrator
- Generating project artifacts

### Example Workflow

```python
from core.workflow import WorkflowOrchestrator

# Create enhanced workflow with MCP context
orchestrator = WorkflowOrchestrator()
workflow_id = await orchestrator.create_workflow_with_context(
    requirements="Build a task management system",
    project_name="TaskMaster Pro"
)

# Create external artifacts
artifacts = await orchestrator.create_external_artifacts(workflow_id)
print(f"Created artifacts: {artifacts}")
```

## MCP Protocol Details

### JIRA Integration

**Endpoints:**
- `POST /search` - Search JIRA issues
- `POST /create_issue` - Create new issue

**Example Request:**
```json
{
  "jql": "project = DEV AND text ~ \"task management\"",
  "fields": ["summary", "description", "status"]
}
```

### GitHub Integration

**Endpoints:**
- `POST /search` - Search repositories
- `POST /create_repo` - Create repository

**Example Request:**
```json
{
  "q": "task management language:python",
  "type": "repositories"
}
```

## Troubleshooting

### MCP Not Working

1. Check if MCP is enabled: `echo $MCP_ENABLED`
2. Verify MCP servers are running on correct ports
3. Test connectivity: `curl http://localhost:3001/health`
4. Check AgentAI logs for MCP connection errors

### Authentication Issues

1. Verify JIRA API token has correct permissions
2. Ensure GitHub token has repo creation permissions
3. Check token expiration dates

### Fallback Behavior

If MCP services are unavailable, AgentAI will:
- Continue with standard workflow (no external context)
- Log warnings about MCP unavailability
- Skip external artifact creation

## Development

### Adding New MCP Services

1. Create new client in `core/mcp_integration.py`
2. Add configuration to `.env.mcp.example`
3. Update `get_project_context()` and `create_project_artifacts()` methods

### Testing MCP Integration

```bash
# Test with MCP disabled
MCP_ENABLED=false python -m pytest tests/test_mcp_integration.py

# Test with MCP enabled (requires running MCP servers)
MCP_ENABLED=true python -m pytest tests/test_mcp_integration.py
```

## Security Considerations

- Store API tokens securely (use environment variables)
- Implement proper authentication for MCP servers
- Validate all external data before processing
- Use HTTPS for production MCP server connections
- Implement rate limiting for external API calls