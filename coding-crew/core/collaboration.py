"""Collaboration Features with code review workflows, team sharing, and change tracking."""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class CollaborationManager:
    def __init__(self, workspace_path: str = "generated_projects"):
        self.workspace_path = workspace_path
        self.reviews_db = os.path.join(workspace_path, "code_reviews.json")
        self.teams_db = os.path.join(workspace_path, "teams.json")
        self.changes_db = os.path.join(workspace_path, "changes.json")
        self._ensure_databases()

    def _ensure_databases(self):
        """Ensure collaboration databases exist."""
        for db_path in [self.reviews_db, self.teams_db, self.changes_db]:
            if not os.path.exists(db_path):
                with open(db_path, 'w') as f:
                    json.dump({}, f, indent=2)

    def create_code_review(self, review_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create new code review request."""
        review_id = str(uuid.uuid4())
        
        review_data = {
            "id": review_id,
            "title": review_config.get("title", "Code Review"),
            "description": review_config.get("description", ""),
            "author": review_config.get("author", "unknown"),
            "project_id": review_config.get("project_id"),
            "files": review_config.get("files", []),
            "reviewers": review_config.get("reviewers", []),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "comments": [],
            "approvals": [],
            "changes_requested": []
        }
        
        # Save review
        reviews_data = self._load_db(self.reviews_db)
        reviews_data[review_id] = review_data
        self._save_db(self.reviews_db, reviews_data)
        
        return {
            "review_id": review_id,
            "status": "created",
            "review_data": review_data
        }

    def add_review_comment(self, review_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add comment to code review."""
        reviews_data = self._load_db(self.reviews_db)
        
        if review_id not in reviews_data:
            return {"status": "error", "message": "Review not found"}
        
        comment = {
            "id": str(uuid.uuid4()),
            "author": comment_data.get("author", "unknown"),
            "content": comment_data.get("content", ""),
            "file_path": comment_data.get("file_path"),
            "line_number": comment_data.get("line_number"),
            "timestamp": datetime.now().isoformat(),
            "type": comment_data.get("type", "general")  # general, suggestion, issue
        }
        
        reviews_data[review_id]["comments"].append(comment)
        self._save_db(self.reviews_db, reviews_data)
        
        return {"status": "success", "comment": comment}

    def approve_review(self, review_id: str, reviewer: str, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Approve or request changes for code review."""
        reviews_data = self._load_db(self.reviews_db)
        
        if review_id not in reviews_data:
            return {"status": "error", "message": "Review not found"}
        
        approval = {
            "reviewer": reviewer,
            "status": approval_data.get("status", "approved"),  # approved, changes_requested
            "comment": approval_data.get("comment", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        if approval["status"] == "approved":
            reviews_data[review_id]["approvals"].append(approval)
        else:
            reviews_data[review_id]["changes_requested"].append(approval)
        
        # Update review status
        total_reviewers = len(reviews_data[review_id]["reviewers"])
        approvals_count = len(reviews_data[review_id]["approvals"])
        changes_count = len(reviews_data[review_id]["changes_requested"])
        
        if changes_count > 0:
            reviews_data[review_id]["status"] = "changes_requested"
        elif approvals_count >= total_reviewers:
            reviews_data[review_id]["status"] = "approved"
        
        self._save_db(self.reviews_db, reviews_data)
        
        return {"status": "success", "review_status": reviews_data[review_id]["status"]}

    def create_team(self, team_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create new team for project collaboration."""
        team_id = str(uuid.uuid4())
        
        team_data = {
            "id": team_id,
            "name": team_config.get("name", f"Team {team_id[:8]}"),
            "description": team_config.get("description", ""),
            "owner": team_config.get("owner", "unknown"),
            "members": team_config.get("members", []),
            "projects": team_config.get("projects", []),
            "permissions": team_config.get("permissions", {
                "read": True,
                "write": False,
                "admin": False
            }),
            "created_at": datetime.now().isoformat()
        }
        
        teams_data = self._load_db(self.teams_db)
        teams_data[team_id] = team_data
        self._save_db(self.teams_db, teams_data)
        
        return {"team_id": team_id, "status": "created", "team_data": team_data}

    def add_team_member(self, team_id: str, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add member to team."""
        teams_data = self._load_db(self.teams_db)
        
        if team_id not in teams_data:
            return {"status": "error", "message": "Team not found"}
        
        member = {
            "username": member_data.get("username"),
            "role": member_data.get("role", "member"),  # member, reviewer, admin
            "permissions": member_data.get("permissions", {"read": True, "write": False}),
            "joined_at": datetime.now().isoformat()
        }
        
        teams_data[team_id]["members"].append(member)
        self._save_db(self.teams_db, teams_data)
        
        return {"status": "success", "member": member}

    def share_project(self, project_id: str, share_config: Dict[str, Any]) -> Dict[str, Any]:
        """Share project with team or individuals."""
        share_data = {
            "project_id": project_id,
            "shared_with": share_config.get("shared_with", []),  # usernames or team_ids
            "permissions": share_config.get("permissions", {"read": True, "write": False}),
            "shared_by": share_config.get("shared_by", "unknown"),
            "shared_at": datetime.now().isoformat(),
            "message": share_config.get("message", "")
        }
        
        # In a real implementation, this would update project permissions
        # For now, we'll just track the sharing action
        
        return {"status": "success", "share_data": share_data}

    def track_change(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track changes made to projects."""
        change_id = str(uuid.uuid4())
        
        change = {
            "id": change_id,
            "project_id": change_data.get("project_id"),
            "author": change_data.get("author", "unknown"),
            "type": change_data.get("type", "modification"),  # creation, modification, deletion
            "files_changed": change_data.get("files_changed", []),
            "description": change_data.get("description", ""),
            "timestamp": datetime.now().isoformat(),
            "diff": change_data.get("diff", ""),
            "approved_by": change_data.get("approved_by", [])
        }
        
        changes_data = self._load_db(self.changes_db)
        changes_data[change_id] = change
        self._save_db(self.changes_db, changes_data)
        
        return {"change_id": change_id, "status": "tracked", "change": change}

    def get_project_history(self, project_id: str) -> List[Dict[str, Any]]:
        """Get change history for project."""
        changes_data = self._load_db(self.changes_db)
        
        project_changes = [
            change for change in changes_data.values()
            if change.get("project_id") == project_id
        ]
        
        # Sort by timestamp (newest first)
        project_changes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return project_changes

    def get_pending_reviews(self, reviewer: str) -> List[Dict[str, Any]]:
        """Get pending code reviews for reviewer."""
        reviews_data = self._load_db(self.reviews_db)
        
        pending_reviews = [
            review for review in reviews_data.values()
            if reviewer in review.get("reviewers", []) and review.get("status") == "pending"
        ]
        
        return pending_reviews

    def get_team_activity(self, team_id: str, days: int = 7) -> Dict[str, Any]:
        """Get team activity summary."""
        teams_data = self._load_db(self.teams_db)
        
        if team_id not in teams_data:
            return {"status": "error", "message": "Team not found"}
        
        team = teams_data[team_id]
        
        # Get recent changes for team projects
        changes_data = self._load_db(self.changes_db)
        reviews_data = self._load_db(self.reviews_db)
        
        team_projects = team.get("projects", [])
        recent_changes = []
        recent_reviews = []
        
        for change in changes_data.values():
            if change.get("project_id") in team_projects:
                recent_changes.append(change)
        
        for review in reviews_data.values():
            if review.get("project_id") in team_projects:
                recent_reviews.append(review)
        
        return {
            "team_id": team_id,
            "team_name": team.get("name"),
            "members_count": len(team.get("members", [])),
            "projects_count": len(team_projects),
            "recent_changes": len(recent_changes),
            "pending_reviews": len([r for r in recent_reviews if r.get("status") == "pending"]),
            "activity_summary": {
                "changes": recent_changes[:10],  # Last 10 changes
                "reviews": recent_reviews[:5]    # Last 5 reviews
            }
        }

    def collaboration_dashboard(self) -> Dict[str, Any]:
        """Get collaboration dashboard data."""
        reviews_data = self._load_db(self.reviews_db)
        teams_data = self._load_db(self.teams_db)
        changes_data = self._load_db(self.changes_db)
        
        return {
            "total_reviews": len(reviews_data),
            "pending_reviews": len([r for r in reviews_data.values() if r.get("status") == "pending"]),
            "total_teams": len(teams_data),
            "total_changes": len(changes_data),
            "recent_activity": {
                "reviews": list(reviews_data.values())[-5:],  # Last 5 reviews
                "changes": list(changes_data.values())[-10:]  # Last 10 changes
            }
        }

    def _load_db(self, db_path: str) -> Dict[str, Any]:
        """Load database file."""
        with open(db_path, 'r') as f:
            return json.load(f)

    def _save_db(self, db_path: str, data: Dict[str, Any]):
        """Save database file."""
        with open(db_path, 'w') as f:
            json.dump(data, f, indent=2)