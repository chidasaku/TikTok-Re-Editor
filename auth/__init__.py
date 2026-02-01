"""Authentication module for TikTok Re-Editor v3"""
from .lark_base import LarkBaseClient
from .user_manager import UserManager, UserStatus
from .auth_ui import (
    check_auth,
    get_current_user,
    is_current_user_admin,
    render_user_menu,
    render_login_page,
    render_registration_form,
    render_pending_page,
    render_rejected_page,
    render_banned_page,
)

__all__ = [
    "LarkBaseClient",
    "UserManager",
    "UserStatus",
    "check_auth",
    "get_current_user",
    "is_current_user_admin",
    "render_user_menu",
    "render_login_page",
    "render_registration_form",
    "render_pending_page",
    "render_rejected_page",
    "render_banned_page",
]
