"""Tests for web interface and approval workflow."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

# Add web directory to path
web_path = os.path.join(os.path.dirname(__file__), '../../web')
sys.path.insert(0, web_path)

# Mock static files for testing
from unittest.mock import patch
with patch('fastapi.staticfiles.StaticFiles'):
    from app import app

client = TestClient(app)

class TestWebInterface:
    
    def test_home_page(self):
        """Test home page loads correctly."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Coding Crew" in response.text
    
    def test_submit_analysis(self):
        """Test analysis submission."""
        analysis_data = {
            "id": "test-001",
            "title": "Test Analysis",
            "content": "Test content",
            "diagrams": [],
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        response = client.post("/api/analyses", json=analysis_data)
        assert response.status_code == 200
        assert response.json()["status"] == "submitted"
    
    def test_get_analyses(self):
        """Test retrieving analyses."""
        response = client.get("/api/analyses")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_approve_analysis(self):
        """Test analysis approval."""
        # First submit an analysis
        analysis_data = {
            "id": "test-002",
            "title": "Test Analysis 2",
            "content": "Test content 2",
            "diagrams": [],
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        client.post("/api/analyses", json=analysis_data)
        
        # Then approve it
        approval_data = {
            "analysis_id": "test-002",
            "approved": True,
            "feedback": "Looks good"
        }
        
        response = client.post("/api/approve/test-002", json=approval_data)
        assert response.status_code == 200
        assert response.json()["approved"] == True
    
    def test_approval_status(self):
        """Test approval status check."""
        response = client.get("/api/approval-status/test-002")
        assert response.status_code == 200
        assert "approved" in response.json()
    
    def test_nonexistent_analysis(self):
        """Test handling of nonexistent analysis."""
        response = client.get("/api/analyses/nonexistent")
        assert response.status_code == 404