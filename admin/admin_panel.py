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

    # ヘッダー
    cols = st.columns([1.5, 2, 2, 1, 1])
    cols[0].markdown("**名前**")
    cols[1].markdown("**メール**")
    cols[2].markdown("**申請日**")
    cols[3].markdown("")
    cols[4].markdown("")

    # データ行
    for user in pending_users:
        cols = st.columns([1.5, 2, 2, 1, 1])
        cols[0].write(f"{user['real_name']} ({user['nickname']})")
        cols[1].write(user['email'])
        cols[2].write(user['created_at'])
        if cols[3].button("✅ 承認", key=f"approve_{user['google_id']}"):
            if user_manager.approve_user(user['google_id']):
                st.rerun()
        if cols[4].button("❌ 却下", key=f"reject_{user['google_id']}"):
            if user_manager.reject_user(user['google_id']):
                st.rerun()


def _render_approved_users(user_manager: UserManager):
    """Render approved users list"""
    st.markdown("### 承認済みユーザー")

    approved_users = user_manager.get_users_by_status(UserStatus.APPROVED)

    if not approved_users:
        st.info("承認済みのユーザーはいません")
        return

    # ヘッダー
    cols = st.columns([1.5, 2, 1.5, 1.5, 0.8, 1, 1])
    cols[0].markdown("**名前**")
    cols[1].markdown("**メール**")
    cols[2].markdown("**登録日**")
    cols[3].markdown("**最終ログイン**")
    cols[4].markdown("**回数**")
    cols[5].markdown("")
    cols[6].markdown("")

    # データ行
    for user in approved_users:
        cols = st.columns([1.5, 2, 1.5, 1.5, 0.8, 1, 1])

        # 名前（管理者バッジ付き）
        admin_badge = "👑 " if user['is_admin'] else ""
        cols[0].write(f"{admin_badge}{user['real_name']} ({user['nickname']})")

        cols[1].write(user['email'])
        cols[2].write(user['created_at'][:10] if user['created_at'] else "")
        cols[3].write(user['last_login'][:10] if user['last_login'] else "")
        cols[4].write(str(user['login_count'] or 0))

        # BAN button
        with cols[5].popover("🚫 BAN"):
            ban_reason = st.text_input(
                "BAN理由",
                key=f"ban_reason_{user['google_id']}",
                placeholder="理由を入力..."
            )
            if st.button("BANする", key=f"ban_{user['google_id']}", type="primary"):
                if ban_reason:
                    if user_manager.ban_user(user['google_id'], ban_reason):
                        st.rerun()
                else:
                    st.error("理由を入力")

        # Admin toggle
        if user['is_admin']:
            if cols[6].button("👑→👤", key=f"demote_{user['google_id']}", help="管理者権限を剥奪"):
                if user_manager.set_admin(user['google_id'], False):
                    st.rerun()
        else:
            if cols[6].button("👤→👑", key=f"promote_{user['google_id']}", help="管理者に昇格"):
                if user_manager.set_admin(user['google_id'], True):
                    st.rerun()


def _render_banned_users(user_manager: UserManager):
    """Render banned and rejected users"""
    st.markdown("### BAN/却下済みユーザー")

    banned_users = user_manager.get_users_by_status(UserStatus.BANNED)
    rejected_users = user_manager.get_users_by_status(UserStatus.REJECTED)

    all_users = banned_users + rejected_users

    if not all_users:
        st.info("BAN/却下済みのユーザーはいません")
        return

    # ヘッダー
    cols = st.columns([1, 1.5, 2, 2, 1])
    cols[0].markdown("**状態**")
    cols[1].markdown("**名前**")
    cols[2].markdown("**メール**")
    cols[3].markdown("**理由**")
    cols[4].markdown("")

    # データ行
    for user in all_users:
        cols = st.columns([1, 1.5, 2, 2, 1])

        status_label = "🚫 BAN" if user['status'] == UserStatus.BANNED else "❌ 却下"
        cols[0].write(status_label)
        cols[1].write(f"{user['real_name']} ({user['nickname']})")
        cols[2].write(user['email'])
        cols[3].write(user['ban_reason'] or "-")

        if user['status'] == UserStatus.BANNED:
            if cols[4].button("🔓 解除", key=f"unban_{user['google_id']}"):
                if user_manager.unban_user(user['google_id']):
                    st.rerun()
        else:
            if cols[4].button("✅ 承認", key=f"approve_rejected_{user['google_id']}"):
                if user_manager.approve_user(user['google_id']):
                    st.rerun()
