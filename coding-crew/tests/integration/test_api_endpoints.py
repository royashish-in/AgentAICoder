"""Integration tests for API endpoints."""

import pytest
import httpx
import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from coding_crew.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test API endpoint integration."""
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["framework"] == "crewai"
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Coding Crew API" in data["message"]
        assert data["version"] == "0.1.0"
    
    def test_create_workflow(self):
        """Test workflow creation."""
        payload = {
            "requirements": "Build a simple web application with user authentication"
        }
        
        response = client.post("/workflows", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "workflow_id" in data
        assert data["status"] == "created"
        assert data["stage"] == "analysis"
        assert data["framework"] == "crewai"
    
    def test_get_workflow_status(self):
        """Test getting workflow status."""
        # Create workflow first
        payload = {"requirements": "Test requirements"}
        response = client.post("/workflows", json=payload)
        workflow_id = response.json()["workflow_id"]
        
        response = client.get(f"/workflows/{workflow_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == workflow_id
        assert data["stage"] == "analysis"
        assert data["approved"] is False
        assert data["completed"] is False
    
    def test_get_nonexistent_workflow(self):
        """Test getting non-existent workflow."""
        response = client.get("/workflows/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "active_workflows" in data
        assert data["system_health"] == "healthy"
        assert data["framework"] == "crewai"
    
    def test_workflow_approval_flow(self):
        """Test workflow approval process."""
        # Create workflow
        payload = {"requirements": "Test requirements"}
        response = client.post("/workflows", json=payload)
        workflow_id = response.json()["workflow_id"]
        
        # Simulate analysis completion by updating stage
        # In real scenario, this would be done by start-analysis endpoint
        
        # Test approval
        approval_payload = {
            "workflow_id": workflow_id,
            "approved": True,
            "feedback": "Analysis looks good"
        }
        
        # This will fail until analysis is completed, which is expected
        response = client.post(f"/workflows/{workflow_id}/approve", json=approval_payload)
        
        # Should fail because workflow is not in approval stage
        assert response.status_code == 400
        assert "not in approval stage" in response.json()["detail"]