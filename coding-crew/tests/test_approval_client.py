"""Tests for approval client integration."""

import pytest
from unittest.mock import Mock, patch
from core.approval_client import ApprovalClient

class TestApprovalClient:
    
    def setup_method(self):
        """Setup test client."""
        self.client = ApprovalClient("http://test:8000")
    
    @patch('requests.post')
    def test_submit_for_approval(self, mock_post):
        """Test submitting analysis for approval."""
        mock_post.return_value.raise_for_status = Mock()
        
        analysis_id = self.client.submit_for_approval(
            title="Test Analysis",
            content="Test content",
            diagrams=["diagram1.xml"]
        )
        
        assert analysis_id is not None
        assert len(analysis_id) == 36  # UUID length
        mock_post.assert_called_once()
    
    @patch('requests.get')
    def test_wait_for_approval_approved(self, mock_get):
        """Test waiting for approval - approved case."""
        mock_get.return_value.raise_for_status = Mock()
        mock_get.return_value.json.return_value = {
            "approved": True,
            "feedback": "Approved",
            "status": "approved"
        }
        
        result = self.client.wait_for_approval("test-id", timeout=1)
        
        assert result["approved"] == True
        assert result["status"] == "approved"
    
    @patch('requests.get')
    def test_wait_for_approval_rejected(self, mock_get):
        """Test waiting for approval - rejected case."""
        mock_get.return_value.raise_for_status = Mock()
        mock_get.return_value.json.return_value = {
            "approved": False,
            "feedback": "Needs revision",
            "status": "rejected"
        }
        
        result = self.client.wait_for_approval("test-id", timeout=1)
        
        assert result["approved"] == False
        assert result["status"] == "rejected"
    
    @patch('requests.get')
    def test_wait_for_approval_timeout(self, mock_get):
        """Test approval timeout."""
        mock_get.return_value.raise_for_status = Mock()
        mock_get.return_value.json.return_value = {"status": "pending"}
        
        with pytest.raises(TimeoutError):
            self.client.wait_for_approval("test-id", timeout=1)