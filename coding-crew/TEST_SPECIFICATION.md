# Coding Crew Application - Test Specification

## Test Overview

This specification defines comprehensive testing procedures for the CrewAI-based coding crew application with Ollama integration.

## Prerequisites

### System Requirements
- Python 3.11+
- UV package manager
- Docker and Docker Compose
- Ollama with required models installed
- 8GB+ RAM (for LLM inference)

### Required Ollama Models
```bash
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:1.5b-base  
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest
```

### Environment Setup
```bash
# Start Ollama service
ollama serve

# Install dependencies
cd coding-crew
make dev-install

# Verify setup
uv run python scripts/verify_crewai_setup.py
```

## Test Categories

### 1. Unit Tests
**Scope**: Individual components and functions
**Coverage Target**: 90%
**Execution**: `make test`

#### Test Cases
- **CrewAI Workflow Orchestrator**
  - Workflow creation and state management
  - Stage transitions and approvals
  - Error handling and validation
  
- **LLM Configuration**
  - Model loading and switching
  - Configuration validation
  - Connection handling

- **Agent Creation**
  - Agent initialization with correct LLMs
  - Role and backstory assignment
  - Memory and iteration settings

### 2. Integration Tests
**Scope**: Component interactions
**Execution**: `uv run pytest tests/integration/ -v`

#### Test Cases
- **API Endpoints**
  - Workflow CRUD operations
  - Stage progression endpoints
  - Error response handling
  
- **CrewAI Integration**
  - Agent-to-agent communication
  - Task dependency resolution
  - Memory persistence

### 3. End-to-End Tests
**Scope**: Complete workflow scenarios
**Execution**: `uv run pytest tests/e2e/ -v`

#### Test Scenarios

##### Scenario 1: Simple Web App Workflow
```yaml
Input: "Build a simple web application with user authentication"
Expected Stages:
  1. Analysis → Architecture Review (5 iterations max)
  2. Human Approval → Development
  3. Coding → Code Review (5 iterations max)  
  4. Testing → Bug Fixes (5 iterations max)
  5. Documentation → Complete
```

##### Scenario 2: API Service Workflow
```yaml
Input: "Create a REST API for a todo application with CRUD operations"
Expected Stages:
  1. Analysis with system diagrams
  2. Human approval process
  3. Code generation with proper structure
  4. Comprehensive testing
  5. API documentation
```

##### Scenario 3: Error Handling Workflow
```yaml
Input: "Invalid or incomplete requirements"
Expected Behavior:
  - Graceful error handling
  - Meaningful error messages
  - Workflow state preservation
  - Recovery mechanisms
```

## Performance Tests

### Load Testing
**Tool**: `locust` or `pytest-benchmark`
**Metrics**: Response time, throughput, resource usage

#### Test Cases
- **Concurrent Workflows**: 5 simultaneous workflows
- **Large Requirements**: 10KB+ markdown input
- **Model Switching**: Rapid LLM model changes
- **Memory Usage**: Long-running workflows

### Benchmarks
- **Workflow Creation**: < 100ms
- **Analysis Phase**: < 5 minutes (with Ollama)
- **Code Generation**: < 3 minutes
- **Documentation**: < 2 minutes
- **Memory Usage**: < 2GB per workflow

## API Testing

### Endpoint Tests
**Tool**: `httpx` or `requests`
**Base URL**: `http://localhost:8000`

#### Core Endpoints
```bash
# Health check
GET /health
Expected: 200, {"status": "healthy", "framework": "crewai"}

# Create workflow
POST /workflows
Body: {"requirements": "Build a web app"}
Expected: 201, {"workflow_id": "uuid", "stage": "analysis"}

# Get workflow status
GET /workflows/{id}
Expected: 200, workflow status object

# Start analysis
POST /workflows/{id}/start-analysis
Expected: 200, analysis results

# Approve analysis
POST /workflows/{id}/approve
Body: {"workflow_id": "uuid", "approved": true}
Expected: 200, {"status": "approved"}

# Start development
POST /workflows/{id}/start-development
Expected: 200, development results

# Start testing
POST /workflows/{id}/start-testing
Expected: 200, testing results

# Start documentation
POST /workflows/{id}/start-documentation
Expected: 200, documentation results
```

## Ollama Integration Tests

### Model Availability Tests
```python
def test_ollama_models():
    """Test all required models are available."""
    models = ["llama3.1:8b", "qwen2.5-coder:1.5b-base", "llama3.2:latest"]
    for model in models:
        assert ollama_client.list_models().contains(model)
```

### LLM Response Tests
```python
def test_llm_responses():
    """Test LLM generates valid responses."""
    llm = get_analysis_llm()
    response = llm.invoke("Analyze this requirement: Build a web app")
    assert len(response.content) > 100
    assert "web" in response.content.lower()
```

## CrewAI Framework Tests

### Agent Execution Tests
```python
def test_analysis_agent_execution():
    """Test analysis agent produces expected output."""
    agent = create_analysis_agent()
    task = create_analysis_task("Build a web application")
    
    # Execute with timeout
    result = agent.execute_task(task, timeout=300)
    
    assert "architecture" in result.lower()
    assert "components" in result.lower()
```

### Crew Workflow Tests
```python
def test_crew_sequential_execution():
    """Test crew executes tasks in sequence."""
    crew = create_analysis_crew()
    result = crew.kickoff(inputs={"requirements": "Build API"})
    
    assert result.tasks_output is not None
    assert len(result.tasks_output) == 2  # Analysis + Review
```

## Error Handling Tests

### Ollama Connection Tests
- **Ollama Unavailable**: Service down scenarios
- **Model Not Found**: Missing model handling
- **Timeout Handling**: Long-running inference
- **Rate Limiting**: Too many requests

### CrewAI Error Tests
- **Agent Failures**: Agent execution errors
- **Task Failures**: Invalid task definitions
- **Memory Issues**: Large context handling
- **Iteration Limits**: Max iteration reached

## Security Tests

### Input Validation
- **Malicious Input**: SQL injection, XSS attempts
- **Large Payloads**: DoS via large requirements
- **Invalid JSON**: Malformed request bodies
- **Authentication**: API access control

### Data Privacy
- **Local Processing**: No external API calls
- **Data Persistence**: Secure local storage
- **Log Security**: No sensitive data in logs

## Test Execution Plan

### Phase 1: Unit Tests (Daily)
```bash
make test
uv run pytest tests/unit/ --cov=coding_crew --cov-fail-under=90
```

### Phase 2: Integration Tests (Pre-deployment)
```bash
# Start services
make run

# Run integration tests
uv run pytest tests/integration/ -v --timeout=300

# Stop services
make stop
```

### Phase 3: E2E Tests (Release)
```bash
# Full system test
uv run pytest tests/e2e/ -v --timeout=600

# Performance tests
uv run pytest tests/performance/ --benchmark-only
```

### Phase 4: Manual Testing (Release)
1. **Web Interface Testing** (when implemented)
2. **User Acceptance Testing**
3. **Documentation Review**
4. **Deployment Verification**

## Test Data

### Sample Requirements
```markdown
# Simple Web App
Build a web application with:
- User registration and login
- Dashboard with user profile
- Basic CRUD operations
- Responsive design

# API Service  
Create a REST API for:
- User management
- Authentication with JWT
- CRUD operations for todos
- Input validation
- Error handling

# Complex System
Design a microservices architecture for:
- E-commerce platform
- User service, product service, order service
- API gateway and load balancer
- Database per service
- Event-driven communication
```

## Success Criteria

### Functional Requirements
- ✅ All API endpoints respond correctly
- ✅ CrewAI workflow executes end-to-end
- ✅ Ollama models generate valid responses
- ✅ Human approval process works
- ✅ Error handling is graceful

### Performance Requirements
- ✅ Analysis phase completes in < 5 minutes
- ✅ System handles 5 concurrent workflows
- ✅ Memory usage stays under 2GB per workflow
- ✅ API response times < 2 seconds

### Quality Requirements
- ✅ Test coverage > 90%
- ✅ No critical security vulnerabilities
- ✅ All linting and type checks pass
- ✅ Documentation is complete and accurate

## Test Automation

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install UV
        run: pip install uv
      - name: Install dependencies
        run: uv sync --extra dev
      - name: Run tests
        run: make test
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Local Test Runner
```bash
#!/bin/bash
# scripts/run_tests.sh

echo "🧪 Running Coding Crew Test Suite"

# Unit tests
echo "Running unit tests..."
make test

# Integration tests (if Ollama available)
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Running integration tests..."
    uv run pytest tests/integration/ -v
else
    echo "⚠️  Ollama not available, skipping integration tests"
fi

# Performance tests
echo "Running performance tests..."
uv run pytest tests/performance/ --benchmark-only

echo "✅ Test suite complete!"
```

This test specification ensures comprehensive validation of the CrewAI-based coding crew application with proper Ollama integration testing.