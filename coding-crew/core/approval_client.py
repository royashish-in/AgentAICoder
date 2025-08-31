"""Approval client for human-in-loop workflow."""

from typing import Dict, Any
import uuid
import time


class ApprovalClient:
    """Client for handling human approval workflow."""
    
    def __init__(self):
        self.pending_approvals = {}
    
    def submit_for_approval(self, title: str, content: str, diagrams: list = None) -> str:
        """Submit content for human approval."""
        approval_id = str(uuid.uuid4())
        
        self.pending_approvals[approval_id] = {
            "title": title,
            "content": content,
            "diagrams": diagrams or [],
            "status": "pending",
            "submitted_at": time.time()
        }
        
        return approval_id
    
    def wait_for_approval(self, approval_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for human approval (mock implementation)."""
        # Mock approval for demo - in real implementation this would wait for human input
        return {
            "approved": True,
            "feedback": "Analysis looks good!",
            "approved_at": time.time()
        }