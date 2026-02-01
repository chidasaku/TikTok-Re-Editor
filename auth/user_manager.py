"""User management for TikTok Re-Editor v3"""
from datetime import datetime
from typing import Optional, Dict, List, Any
import streamlit as st
from .lark_base import LarkBaseClient


class UserStatus:
    """User status constants (Japanese)"""
    PENDING = "承認待ち"
    APPROVED = "承認済み"
    REJECTED = "却下"
    BANNED = "BAN"


class UserManager:
    """User management with Lark Base backend"""

    def __init__(self):
        """Initialize with Lark Base client"""
        self.client = LarkBaseClient()
        self.admin_emails = st.secrets.get("admin", {}).get("emails", [])

    def get_user_by_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Google ID"""
        record = self.client.get_record_by_field("google_id", google_id)
        if record:
            return self._record_to_user(record)
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        record = self.client.get_record_by_field("email", email)
        if record:
            return self._record_to_user(record)
        return None

    def create_user(self, google_id: str, email: str, real_name: str, nickname: str) -> Dict[str, Any]:
        """Create a new user with pending status"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if email is in admin list - auto-approve
        is_admin = email in self.admin_emails
        status = UserStatus.APPROVED if is_admin else UserStatus.PENDING

        fields = {
            "google_id": google_id,
            "email": email,
            "real_name": real_name,
            "nickname": nickname,
            "status": status,
            "is_admin": is_admin,
            "created_at": now,
            "last_login": now,
            "login_count": 1
        }

        record = self.client.create_record(fields)
        return self._record_to_user(record)

    def update_last_login(self, google_id: str) -> None:
        """Update user's last login time and increment login count"""
        try:
            record = self.client.get_record_by_field("google_id", google_id)
            if record:
                record_id = record["record_id"]
                current_count = record.get("fields", {}).get("login_count")
                # Handle None, empty string, or non-numeric values
                if current_count is None or current_count == "":
                    current_count = 0
                elif isinstance(current_count, str):
                    try:
                        current_count = int(current_count)
                    except ValueError:
                        current_count = 0
                else:
                    current_count = int(current_count)

                self.client.update_record(record_id, {
                    "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "login_count": current_count + 1
                })
        except Exception:
            # Silently fail - login tracking is not critical
            pass

    def is_admin(self, email: str) -> bool:
        """Check if user is admin"""
        # Check secrets first
        if email in self.admin_emails:
            return True
        # Check database
        user = self.get_user_by_email(email)
        return user.get("is_admin", False) if user else False

    def approve_user(self, google_id: str) -> bool:
        """Approve a user"""
        return self._update_status(google_id, UserStatus.APPROVED)

    def reject_user(self, google_id: str) -> bool:
        """Reject a user"""
        return self._update_status(google_id, UserStatus.REJECTED)

    def ban_user(self, google_id: str, reason: str) -> bool:
        """Ban a user with reason"""
        record = self.client.get_record_by_field("google_id", google_id)
        if record:
            record_id = record["record_id"]
            self.client.update_record(record_id, {
                "status": UserStatus.BANNED,
                "ban_reason": reason
            })
            return True
        return False

    def unban_user(self, google_id: str) -> bool:
        """Unban a user"""
        record = self.client.get_record_by_field("google_id", google_id)
        if record:
            record_id = record["record_id"]
            self.client.update_record(record_id, {
                "status": UserStatus.APPROVED,
                "ban_reason": ""
            })
            return True
        return False

    def set_admin(self, google_id: str, is_admin: bool) -> bool:
        """Set or remove admin status"""
        record = self.client.get_record_by_field("google_id", google_id)
        if record:
            record_id = record["record_id"]
            self.client.update_record(record_id, {"is_admin": is_admin})
            return True
        return False

    def get_users_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all users with a specific status"""
        filter_condition = {
            "conjunction": "and",
            "conditions": [
                {
                    "field_name": "status",
                    "operator": "is",
                    "value": [status]
                }
            ]
        }
        records = self.client.search_records(filter_condition)
        return [self._record_to_user(r) for r in records]

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        records = self.client.get_all_records()
        return [self._record_to_user(r) for r in records]

    def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics"""
        users = self.get_all_users()
        stats = {
            "total": len(users),
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "banned": 0,
            "admins": 0
        }
        for user in users:
            status = user.get("status", "")
            if status in stats:
                stats[status] += 1
            if user.get("is_admin"):
                stats["admins"] += 1
        return stats

    def _update_status(self, google_id: str, status: str) -> bool:
        """Update user status"""
        record = self.client.get_record_by_field("google_id", google_id)
        if record:
            record_id = record["record_id"]
            self.client.update_record(record_id, {"status": status})
            return True
        return False

    def _record_to_user(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lark Base record to user dict"""
        fields = record.get("fields", {})
        return {
            "record_id": record.get("record_id"),
            "google_id": fields.get("google_id", ""),
            "email": fields.get("email", ""),
            "real_name": fields.get("real_name", ""),
            "nickname": fields.get("nickname", ""),
            "status": fields.get("status", UserStatus.PENDING),
            "is_admin": fields.get("is_admin", False),
            "ban_reason": fields.get("ban_reason", ""),
            "created_at": fields.get("created_at", ""),
            "last_login": fields.get("last_login", ""),
            "login_count": fields.get("login_count", 0)
        }
