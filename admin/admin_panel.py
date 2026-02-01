"""Admin panel for user management"""
import streamlit as st
from auth.user_manager import UserManager, UserStatus


def render_admin_panel():
    """Render the admin panel UI"""
    st.markdown("## 管理者パネル")

    user_manager = UserManager()

    # Get stats
    stats = user_manager.get_user_stats()

    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("承認待ち", stats.get(UserStatus.PENDING, 0))
    with col2:
        st.metric("承認済み", stats.get(UserStatus.APPROVED, 0))
    with col3:
        st.metric("BAN", stats.get(UserStatus.BANNED, 0))
    with col4:
        st.metric("管理者", stats.get("admins", 0))

    st.divider()

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["承認待ち", "承認済みユーザー", "BAN/却下済み"])

    with tab1:
        _render_pending_users(user_manager)

    with tab2:
        _render_approved_users(user_manager)

    with tab3:
        _render_banned_users(user_manager)

    st.divider()

    # Link to Lark Base
    st.markdown(
        "📊 [Lark Baseで直接編集](https://pjp6vm1896tv.jp.larksuite.com/base/IM0NbgSIxanEJMslH7Dji0o1pjh)"
    )


def _render_pending_users(user_manager: UserManager):
    """Render pending users list"""
    st.markdown("### 承認待ちユーザー")

    pending_users = user_manager.get_users_by_status(UserStatus.PENDING)

    if not pending_users:
        st.info("承認待ちのユーザーはいません")
        return

    for user in pending_users:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"""
                **{user['real_name']}** ({user['nickname']})
                📧 {user['email']}
                📅 申請日: {user['created_at']}
                """)

            with col2:
                if st.button("✅ 承認", key=f"approve_{user['google_id']}", type="primary"):
                    if user_manager.approve_user(user['google_id']):
                        st.success(f"{user['nickname']}さんを承認しました")
                        st.rerun()

            with col3:
                if st.button("❌ 却下", key=f"reject_{user['google_id']}"):
                    if user_manager.reject_user(user['google_id']):
                        st.warning(f"{user['nickname']}さんを却下しました")
                        st.rerun()

            st.divider()


def _render_approved_users(user_manager: UserManager):
    """Render approved users list"""
    st.markdown("### 承認済みユーザー")

    approved_users = user_manager.get_users_by_status(UserStatus.APPROVED)

    if not approved_users:
        st.info("承認済みのユーザーはいません")
        return

    for user in approved_users:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                admin_badge = "👑 " if user['is_admin'] else ""
                st.markdown(f"""
                {admin_badge}**{user['real_name']}** ({user['nickname']})
                📧 {user['email']}
                📅 登録日: {user['created_at']}
                🕐 最終ログイン: {user['last_login']}
                🔢 ログイン回数: {user['login_count']}
                """)

            with col2:
                # BAN button with reason input
                with st.popover("🚫 BAN"):
                    ban_reason = st.text_input(
                        "BAN理由",
                        key=f"ban_reason_{user['google_id']}",
                        placeholder="理由を入力..."
                    )
                    if st.button("BANする", key=f"ban_{user['google_id']}", type="primary"):
                        if ban_reason:
                            if user_manager.ban_user(user['google_id'], ban_reason):
                                st.success(f"{user['nickname']}さんをBANしました")
                                st.rerun()
                        else:
                            st.error("BAN理由を入力してください")

            with col3:
                # Admin toggle
                if user['is_admin']:
                    if st.button("👑→👤", key=f"demote_{user['google_id']}", help="管理者権限を剥奪"):
                        if user_manager.set_admin(user['google_id'], False):
                            st.success(f"{user['nickname']}さんの管理者権限を剥奪しました")
                            st.rerun()
                else:
                    if st.button("👤→👑", key=f"promote_{user['google_id']}", help="管理者に昇格"):
                        if user_manager.set_admin(user['google_id'], True):
                            st.success(f"{user['nickname']}さんを管理者に昇格しました")
                            st.rerun()

            st.divider()


def _render_banned_users(user_manager: UserManager):
    """Render banned and rejected users"""
    st.markdown("### BAN/却下済みユーザー")

    banned_users = user_manager.get_users_by_status(UserStatus.BANNED)
    rejected_users = user_manager.get_users_by_status(UserStatus.REJECTED)

    all_users = banned_users + rejected_users

    if not all_users:
        st.info("BAN/却下済みのユーザーはいません")
        return

    for user in all_users:
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                status_label = "🚫 BAN" if user['status'] == UserStatus.BANNED else "❌ 却下"
                reason = f"\n⚠️ 理由: {user['ban_reason']}" if user['ban_reason'] else ""
                st.markdown(f"""
                {status_label} **{user['real_name']}** ({user['nickname']})
                📧 {user['email']}
                📅 登録日: {user['created_at']}{reason}
                """)

            with col2:
                if user['status'] == UserStatus.BANNED:
                    if st.button("🔓 BAN解除", key=f"unban_{user['google_id']}"):
                        if user_manager.unban_user(user['google_id']):
                            st.success(f"{user['nickname']}さんのBANを解除しました")
                            st.rerun()
                else:
                    if st.button("✅ 承認", key=f"approve_rejected_{user['google_id']}"):
                        if user_manager.approve_user(user['google_id']):
                            st.success(f"{user['nickname']}さんを承認しました")
                            st.rerun()

            st.divider()
