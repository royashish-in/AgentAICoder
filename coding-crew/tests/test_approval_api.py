"""Tests for approval API functionality."""

import pytest
from fastapi.testclient import TestClient
from web.backend.approval_api import app

client = TestClient(app)

class TestApprovalAPI:
    """Test approval workflow API."""
    
    def test_get_pending_analysis(self):
        """Test getting pending analysis data."""
        response = client.get("/api/analysis/pending")
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "system_diagrams" in data
        assert "quality_validation" in data["system_diagrams"]
    
    def test_approve_analysis(self):
        """Test analysis approval."""
        approval_data = {
            "approved": True,
            "comments": "Looks good, approved for development",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        response = client.post("/api/analysis/approve", json=approval_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["next_phase"] == "development"
    
    def test_reject_analysis(self):
        """Test analysis rejection."""
        rejection_data = {
            "approved": False,
            "comments": "Needs more detail in architecture",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        response = client.post("/api/analysis/approve", json=rejection_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["next_phase"] == "analysis"
    
    def test_login_success(self):
        """Test successful authentication."""
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "token" in data
    
    def test_login_failure(self):
        """Test failed authentication."""
        login_data = {
            "username": "wrong",
            "password": "wrong"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_audit_log(self):
        """Test audit log retrieval."""
        response = client.get("/api/audit/log")
        
        assert response.status_code == 200
        data = response.json()
        assert "log" in data