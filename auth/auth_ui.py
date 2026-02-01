"""Authentication UI components for TikTok Re-Editor v3"""
import streamlit as st
from .user_manager import UserManager, UserStatus


def render_login_page():
    """Render the Google login page"""
    # 上部スペース（画面の28%）
    st.markdown("<div style='height: 28vh'></div>", unsafe_allow_html=True)

    # タイトルとサブタイトル（中央寄せ）
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="font-size: 2.5rem; color: #ffffff; text-shadow: 2px 2px 0px #fe2c55, -2px -2px 0px #00f2ea; font-weight: bold;">
            TikTok Re-Editor v3
        </h1>
        <p style="font-size: 1.2rem; color: #888; margin-bottom: 2rem;">
            Googleアカウントでログインしてください
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ボタン（中央寄せ）
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🔐 Googleでログイン", use_container_width=True, type="primary"):
            st.login()


def render_registration_form(email: str, google_id: str):
    """Render the registration form for new users"""
    st.markdown("""
    <style>
        .register-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## 新規登録")
    st.info(f"ようこそ！{email} でログインしています。利用登録を完了してください。")

    with st.form("registration_form"):
        real_name = st.text_input(
            "本名",
            placeholder="山田 太郎",
            help="管理者のみ確認できます"
        )
        nickname = st.text_input(
            "ニックネーム",
            placeholder="やまちゃん",
            help="アプリ内で表示されます"
        )

        st.markdown("---")
        st.markdown("**利用規約**")
        st.markdown("""
        - 本ツールは許可されたユーザーのみ使用できます
        - 生成されたコンテンツの著作権はユーザーに帰属します
        - 不正利用が発覚した場合、アカウントを停止する場合があります
        """)

        agree = st.checkbox("利用規約に同意する")

        submitted = st.form_submit_button("登録申請", type="primary", use_container_width=True)

        if submitted:
            if not real_name or not nickname:
                st.error("本名とニックネームを入力してください")
            elif not agree:
                st.error("利用規約に同意してください")
            else:
                try:
                    user_manager = UserManager()
                    user = user_manager.create_user(
                        google_id=google_id,
                        email=email,
                        real_name=real_name,
                        nickname=nickname
                    )
                    if user["status"] == UserStatus.APPROVED:
                        st.success("登録完了！管理者として承認されました。ページを更新してください。")
                    else:
                        st.success("登録申請が完了しました。管理者の承認をお待ちください。")
                    st.rerun()
                except Exception as e:
                    st.error(f"登録に失敗しました: {str(e)}")


def render_pending_page(nickname: str):
    """Render the pending approval page"""
    st.markdown("""
    <style>
        .pending-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            text-align: center;
        }
    </style>
    <div class="pending-container">
        <h1>⏳ 承認待ち</h1>
    </div>
    """, unsafe_allow_html=True)

    st.info(f"""
    **{nickname}** さん、登録申請ありがとうございます。

    現在、管理者による承認待ちです。
    承認されるまでしばらくお待ちください。

    承認されると、このページを更新してアプリを利用できるようになります。
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 ステータスを確認", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🚪 ログアウト", use_container_width=True):
            st.logout()


def render_rejected_page(nickname: str):
    """Render the rejected page"""
    st.markdown("""
    <style>
        .rejected-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            text-align: center;
        }
    </style>
    <div class="rejected-container">
        <h1>❌ 登録が却下されました</h1>
    </div>
    """, unsafe_allow_html=True)

    st.error(f"""
    **{nickname}** さん、申し訳ありませんが、登録申請が却下されました。

    ご質問がある場合は、管理者にお問い合わせください。
    """)

    if st.button("🚪 ログアウト", use_container_width=True):
        st.logout()


def render_banned_page(nickname: str, reason: str):
    """Render the banned page"""
    st.markdown("""
    <style>
        .banned-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            text-align: center;
        }
    </style>
    <div class="banned-container">
        <h1>🚫 アカウント停止</h1>
    </div>
    """, unsafe_allow_html=True)

    st.error(f"""
    **{nickname}** さん、アカウントが停止されています。

    **理由**: {reason or "不明"}

    ご質問がある場合は、管理者にお問い合わせください。
    """)

    if st.button("🚪 ログアウト", use_container_width=True):
        st.logout()


def check_auth():
    """
    Check authentication status and render appropriate UI.
    Returns True if user is authenticated and approved, False otherwise.
    """
    # Check if user is logged in via st.login (Streamlit 1.42+)
    if not st.user.is_logged_in:
        render_login_page()
        st.stop()
        return False

    # Get user info from Google OAuth
    email = st.user.email
    google_id = st.user.sub  # Google's unique user ID

    # Check if user exists in database
    user_manager = UserManager()
    user = user_manager.get_user_by_google_id(google_id)

    if not user:
        # New user - show registration form
        render_registration_form(email, google_id)
        st.stop()
        return False

    # Update last login
    user_manager.update_last_login(google_id)

    # Check user status
    status = user.get("status", UserStatus.PENDING)
    nickname = user.get("nickname", "ユーザー")

    if status == UserStatus.PENDING:
        render_pending_page(nickname)
        st.stop()
        return False

    if status == UserStatus.REJECTED:
        render_rejected_page(nickname)
        st.stop()
        return False

    if status == UserStatus.BANNED:
        render_banned_page(nickname, user.get("ban_reason", ""))
        st.stop()
        return False

    # User is approved
    return True


def get_current_user():
    """Get the current logged-in user info"""
    if not st.user.is_logged_in:
        return None

    google_id = st.user.sub

    user_manager = UserManager()
    return user_manager.get_user_by_google_id(google_id)


def is_current_user_admin():
    """Check if the current user is an admin"""
    user = get_current_user()
    if not user:
        return False

    # Also check the secrets admin list
    user_manager = UserManager()
    return user.get("is_admin", False) or user_manager.is_admin(user.get("email", ""))


def render_user_menu():
    """Render user menu in the sidebar or header"""
    user = get_current_user()
    if not user:
        return

    is_admin = is_current_user_admin()

    with st.expander(f"👤 {user['nickname']}" + (" 👑" if is_admin else ""), expanded=False):
        st.markdown(f"**メール**: {user['email']}")
        st.markdown(f"**ログイン回数**: {user['login_count']}")

        if is_admin:
            st.markdown("---")
            if st.button("🔧 管理者パネル", key="admin_panel_btn"):
                st.session_state.show_admin_panel = True
                st.rerun()

        st.markdown("---")
        if st.button("🚪 ログアウト", key="logout_btn"):
            st.logout()
