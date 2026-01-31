import streamlit as st
import os
import tempfile
import base64
from dotenv import load_dotenv
from utils.transcription import GladiaAPI
from utils.text_formatter import GeminiFormatter
from utils.voicevox import VoiceVoxAPI
from utils.video_generator_ffmpeg import VideoGeneratorFFmpeg

# 環境変数を読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="TikTok Re-Editor v3",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 翻訳を無効化
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# カスタムCSS - TikTokスタイルのボタンとUI
st.markdown("""
<style>
    /* TikTokカラー: シアン #00f2ea, ピンク #fe2c55, 黒背景 */

    /* ダークテーマの背景 */
    .stApp {
        background: #000000;
        color: #ffffff;
    }

    /* ヘッダースタイル */
    h1 {
        color: #ffffff !important;
        text-shadow:
            2px 2px 0px #fe2c55,
            -2px -2px 0px #00f2ea;
        font-weight: bold !important;
    }

    h2, h3 {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(0, 242, 234, 0.5);
    }

    /* サイドバーを非表示 */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* 本文の左右余白を均等に */
    .block-container {
        padding: 2rem 3rem 2rem 3rem !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
    }

    .stApp {
        overflow-x: hidden !important;
    }

    /* expanderのスタイル - コンパクトに */
    [data-testid="stExpander"] {
        background: #00f2ea !important;
        border: none !important;
        border-radius: 8px !important;
        margin-bottom: 20px !important;
        width: fit-content !important;
    }
    [data-testid="stExpander"] summary {
        color: #000000 !important;
        font-weight: bold !important;
        padding: 8px 16px !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: #00d4d4 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #1a1a1a !important;
        border: 1px solid #00f2ea !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin-top: 10px !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] label {
        color: #ffffff !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] a {
        color: #00f2ea !important;
    }


    /* 全てのボタンを左寄せ・同じ大きさに統一（BROWSE FILES除く） */
    .stButton > button,
    .stButton button,
    .stDownloadButton > button,
    .stDownloadButton button,
    button[kind="primary"] {
        background: #000000 !important;
        color: white !important;
        border: 2px solid #00f2ea !important;
        border-radius: 10px !important;
        padding: 12px 30px !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.5) !important;
        transition: all 0.3s ease !important;
        width: auto !important;
        max-width: 100% !important;
        min-height: 45px !important;
        height: 45px !important;
        line-height: 1.2 !important;
        margin-right: auto !important;
        margin-left: 0 !important;
        display: block !important;
    }

    .stButton > button:hover:not(:disabled),
    .stButton button:hover:not(:disabled),
    .stDownloadButton > button:hover,
    .stDownloadButton button:hover,
    button[kind="primary"]:hover {
        background: #1a1a1a !important;
        border: 3px solid #00f2ea !important;
        color: #00f2ea !important;
        box-shadow:
            0 0 40px rgba(0, 242, 234, 1),
            0 0 60px rgba(0, 242, 234, 0.6),
            inset 0 0 20px rgba(0, 242, 234, 0.2) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }

    /* テキストエリア */
    .stTextArea textarea {
        background: rgba(10, 10, 10, 0.9) !important;
        color: #ffffff !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.3) !important;
        caret-color: #00f2ea !important;
        padding: 10px !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

    /* テキストインプット */
    .stTextInput input {
        background: rgba(10, 10, 10, 0.9) !important;
        color: #ffffff !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.3) !important;
        caret-color: #00f2ea !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
    }

    /* セレクトボックス */
    .stSelectbox > div > div {
        background: rgba(10, 10, 10, 0.9) !important;
        color: #ffffff !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 10px !important;
    }

    /* スライダー */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #00f2ea 0%, #fe2c55 100%) !important;
    }

    /* 各種ラベルを白文字に */
    .stFileUploader label,
    [data-testid="stFileUploader"] label,
    .stFileUploader p,
    [data-testid="stFileUploader"] p,
    .stTextArea label,
    .stTextInput label,
    .stSelectbox label,
    .stSlider label {
        color: #ffffff !important;
    }

    /* インフォボックス */
    .stInfo {
        background: rgba(0, 242, 234, 0.1) !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.3) !important;
        color: #ffffff !important;
    }

    /* ファイルアップローダー */
    .stFileUploader {
        background: rgba(10, 10, 10, 0.9) !important;
        border: 2px solid rgba(0, 242, 234, 0.5) !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }

    /* オーディオプレイヤー */
    audio {
        width: 100% !important;
        filter:
            drop-shadow(0 0 10px rgba(0, 242, 234, 0.5))
            drop-shadow(0 0 20px rgba(254, 44, 85, 0.3));
    }

    /* iPhone 15風フレーム */
    .iphone-frame {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 40px 0;
    }

    .iphone-device {
        width: 240px;
        background: #1c1c1e;
        border-radius: 50px;
        padding: 12px;
        box-shadow:
            inset 0 0 0 3px #2c2c2e,
            inset 0 0 0 4px #1c1c1e,
            0 0 0 2px #0a0a0a,
            0 40px 80px rgba(0, 0, 0, 0.8),
            0 0 60px rgba(0, 242, 234, 0.1);
        position: relative;
    }

    /* サイドボタン */
    .iphone-device::before {
        content: "";
        position: absolute;
        right: -3px;
        top: 120px;
        width: 4px;
        height: 60px;
        background: #2c2c2e;
        border-radius: 0 2px 2px 0;
    }

    .iphone-device::after {
        content: "";
        position: absolute;
        left: -3px;
        top: 100px;
        width: 4px;
        height: 30px;
        background: #2c2c2e;
        border-radius: 2px 0 0 2px;
        box-shadow: 0 50px 0 #2c2c2e, 0 90px 0 #2c2c2e;
    }

    /* Dynamic Island */
    .iphone-dynamic-island {
        width: 100px;
        height: 32px;
        background: #000;
        border-radius: 20px;
        margin: 0 auto 8px auto;
        position: relative;
        z-index: 10;
        box-shadow: inset 0 0 4px rgba(255,255,255,0.1);
    }

    .iphone-screen {
        background: #000;
        border-radius: 42px;
        overflow: hidden;
        position: relative;
        border: 1px solid #333;
    }

    .iphone-screen video {
        width: 100% !important;
        height: auto !important;
        max-height: 450px !important;
        display: block !important;
    }

    /* ホームインジケーター */
    .iphone-home-indicator {
        width: 130px;
        height: 5px;
        background: #fff;
        border-radius: 3px;
        margin: 10px auto 5px auto;
        opacity: 0.8;
    }

    /* タブスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: transparent !important;
        padding: 15px 10px 20px 10px;
        border: none !important;
        display: flex !important;
        flex-direction: row !important;
    }

    .stTabs [data-baseweb="tab"] {
        flex: 1 !important;
        width: 100% !important;
        height: 45px !important;
        padding: 12px 30px !important;
        background: #000000 !important;
        border: 2px solid #00f2ea !important;
        border-radius: 10px !important;
        color: white !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.5) !important;
        transition: all 0.25s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #1a1a1a !important;
        border: 3px solid #00f2ea !important;
        color: #00f2ea !important;
        box-shadow: 0 0 40px rgba(0, 242, 234, 1) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }

    /* サクセスボックス - ピンク系 */
    .stSuccess {
        background: rgba(254, 44, 85, 0.1) !important;
        border: 2px solid rgba(254, 44, 85, 0.5) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# セッションステートの初期化
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None
if 'formatted_text' not in st.session_state:
    st.session_state.formatted_text = None
if 'filename' not in st.session_state:
    st.session_state.filename = None
if 'generated_audio' not in st.session_state:
    st.session_state.generated_audio = None
if 'sample_audio' not in st.session_state:
    st.session_state.sample_audio = None
if 'generated_sns_content' not in st.session_state:
    st.session_state.generated_sns_content = None
if 'generated_video' not in st.session_state:
    st.session_state.generated_video = None
if 'preview_video' not in st.session_state:
    st.session_state.preview_video = None
if 'speaker_id' not in st.session_state:
    st.session_state.speaker_id = None
if 'speed' not in st.session_state:
    st.session_state.speed = 1.0
if 'pause_length' not in st.session_state:
    st.session_state.pause_length = 1.0
if 'audio_text' not in st.session_state:
    st.session_state.audio_text = None
if 'rephrased_result' not in st.session_state:
    st.session_state.rephrased_result = None
if 'hiragana_text' not in st.session_state:
    st.session_state.hiragana_text = None
if 'audio_segments' not in st.session_state:
    st.session_state.audio_segments = None
if 'audio_upload_mode' not in st.session_state:
    st.session_state.audio_upload_mode = False
if 'audio_file_path' not in st.session_state:
    st.session_state.audio_file_path = None
if 'audio_file_data' not in st.session_state:
    st.session_state.audio_file_data = None
if 'audio_words' not in st.session_state:
    st.session_state.audio_words = []
if 'edited_segments' not in st.session_state:
    st.session_state.edited_segments = None
if 'timestamped_segments' not in st.session_state:
    st.session_state.timestamped_segments = None
if 'gladia_words' not in st.session_state:
    st.session_state.gladia_words = []
if 'audio_upload_sns_content' not in st.session_state:
    st.session_state.audio_upload_sns_content = None

# ブラウザのlocalStorageからAPIキーを読み込むJavaScript
import streamlit.components.v1 as components

# セッションステートにAPIキーを初期化
if 'gladia_api_key' not in st.session_state:
    st.session_state.gladia_api_key = ""
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""

# localStorageから読み込むHTML/JavaScript
load_keys_js = """
<script>
    const gladiaKey = localStorage.getItem('tiktok_reeditor_gladia_key') || '';
    const geminiKey = localStorage.getItem('tiktok_reeditor_gemini_key') || '';

    // Streamlitにデータを送信
    if (gladiaKey || geminiKey) {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: {gladia: gladiaKey, gemini: geminiKey}
        }, '*');
    }
</script>
"""

# API設定（折りたたみ式）- タイトルの上に配置
with st.expander("API設定", expanded=False):
    st.markdown("💡 **APIキーはブラウザに保存されます**（次回以降自動入力）")

    col1, col2 = st.columns(2)
    with col1:
        gladia_api_key = st.text_input(
            "Gladia API Key",
            value=st.session_state.gladia_api_key,
            type="password",
            key="gladia_input"
        )
        st.markdown('<a href="https://www.gladia.io/" target="_blank" style="color: #00f2ea; font-size: 12px;">Gladia APIキーを取得</a>', unsafe_allow_html=True)
    with col2:
        gemini_api_key = st.text_input(
            "Gemini API Key",
            value=st.session_state.gemini_api_key,
            type="password",
            key="gemini_input"
        )
        st.markdown('<a href="https://aistudio.google.com/apikey" target="_blank" style="color: #00f2ea; font-size: 12px;">Gemini APIキーを取得</a>', unsafe_allow_html=True)

    # APIキーをブラウザに保存するボタン
    if st.button("APIキーを保存", key="save_api_keys"):
        st.session_state.gladia_api_key = gladia_api_key
        st.session_state.gemini_api_key = gemini_api_key

        # localStorageに保存するJavaScript
        save_js = f"""
        <script>
            localStorage.setItem('tiktok_reeditor_gladia_key', '{gladia_api_key}');
            localStorage.setItem('tiktok_reeditor_gemini_key', '{gemini_api_key}');
        </script>
        """
        components.html(save_js, height=0)
        st.success("✅ APIキーをブラウザに保存しました（次回以降自動入力されます）")

    st.markdown('テキストファイルから生成する場合、Gladia APIは不要です')

    # localStorageから読み込み（初回のみ）
    if not st.session_state.gladia_api_key and not st.session_state.gemini_api_key:
        components.html("""
        <script>
            const gladiaKey = localStorage.getItem('tiktok_reeditor_gladia_key') || '';
            const geminiKey = localStorage.getItem('tiktok_reeditor_gemini_key') || '';
            if (gladiaKey || geminiKey) {
                // URLパラメータで渡す（リロード時に読み込まれる）
                const url = new URL(window.parent.location);
                if (gladiaKey) url.searchParams.set('gk', gladiaKey);
                if (geminiKey) url.searchParams.set('mk', geminiKey);
                if (url.toString() !== window.parent.location.toString()) {
                    window.parent.location = url.toString();
                }
            }
        </script>
        """, height=0)

# URLパラメータからAPIキーを取得（localStorage経由）
query_params = st.query_params
if 'gk' in query_params and not st.session_state.gladia_api_key:
    st.session_state.gladia_api_key = query_params['gk']
    gladia_api_key = query_params['gk']
if 'mk' in query_params and not st.session_state.gemini_api_key:
    st.session_state.gemini_api_key = query_params['mk']
    gemini_api_key = query_params['mk']

# VOICEVOX URLはデフォルト値を使用（UIから削除）
voicevox_url = "http://localhost:50021"

# タイトル
st.markdown('<h1 translate="no">TikTok Re-Editor v3</h1>', unsafe_allow_html=True)
st.markdown("文字起こし → 整形 → 音声アップロード → **透過動画生成**")

# APIクライアントの初期化
gladia = GladiaAPI(gladia_api_key) if gladia_api_key else None
gemini = GeminiFormatter(gemini_api_key) if gemini_api_key else None
voicevox = VoiceVoxAPI(voicevox_url)

# ===========================================
# セクション1: 入力ソース選択
# ===========================================
st.header("1. 入力ソース選択")

tab1, tab2, tab3, tab4 = st.tabs(["動画から生成", "ファイルから生成", "テキスト入力", "🎵 音声アップロード"])

with tab1:
    st.subheader("動画アップロード")

    uploaded_file = st.file_uploader(
        "動画ファイルを選択してください",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        key="video_uploader"
    )

    if uploaded_file is not None:
        # ファイルポインタを先頭にリセットしてから読み込む
        uploaded_file.seek(0)
        file_data = uploaded_file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(file_data)
            tmp_file_path = tmp_file.name

        st.info(f"アップロードされたファイル: {uploaded_file.name}")

        if st.button("START", key="transcribe_btn"):
            if not gladia_api_key or not gemini_api_key:
                st.error("サイドバーでGladia APIキーとGemini APIキーを入力してください")
                st.stop()

            try:
                progress_bar = st.progress(0)

                progress_bar.progress(10)
                audio_url = gladia.upload_file(tmp_file_path)

                if audio_url:
                    progress_bar.progress(30)
                    transcribed = gladia.transcribe(audio_url, language="ja")

                    if transcribed:
                        st.session_state.transcribed_text = transcribed
                        st.info(f"文字起こし完了: {len(transcribed)}文字")
                        progress_bar.progress(60)

                        try:
                            formatted = gemini.format_text(transcribed)
                        except Exception as e:
                            error_str = str(e)
                            if "429" in error_str or "quota" in error_str.lower():
                                st.error("⚠️ Gemini APIのクォータ（利用制限）を超過しました")
                                st.warning("30秒後に再試行するか、新しいAPIキーを取得してください: https://aistudio.google.com/apikey")
                            else:
                                st.error(f"テキスト整形エラー: {type(e).__name__}: {e}")
                            formatted = None

                        if formatted:
                            st.session_state.formatted_text = formatted
                            progress_bar.progress(80)
                            filename = gemini.generate_filename(formatted)
                            st.session_state.filename = filename or "output"
                            progress_bar.progress(100)
                            st.success("Complete!")
                        else:
                            st.error("テキスト整形に失敗しました")
                            # 文字起こしテキストをそのまま使用するオプション
                            st.warning("文字起こしテキストをそのまま使用します（手動で整形してください）")
                            st.session_state.formatted_text = transcribed
                            st.session_state.filename = "output"
                    else:
                        st.error("文字起こしに失敗しました")
                else:
                    st.error("ファイルアップロードに失敗しました")
            finally:
                # 処理完了後に一時ファイルを削除
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)

with tab2:
    st.subheader("テキストファイルアップロード")

    text_file = st.file_uploader(
        "テキストファイルを選択してください (.txt)",
        type=["txt"],
        key="text_file_uploader"
    )

    if text_file is not None:
        st.info(f"アップロードされたファイル: {text_file.name}")

        if st.button("START", key="text_process_btn"):
            try:
                progress_bar = st.progress(0)

                progress_bar.progress(20)
                raw_text = text_file.read().decode('utf-8', errors='replace')

                if raw_text.strip():
                    st.session_state.transcribed_text = raw_text
                    progress_bar.progress(50)

                    # テキスト整形：改行ごとに句読点を追加
                    lines = raw_text.strip().split('\n')
                    formatted_lines = []
                    punctuation = ('。', '、', '！', '？', '!', '?', '．', '，')

                    for i, line in enumerate(lines):
                        line = line.strip()
                        if not line:
                            continue
                        # 既に句読点で終わっている場合はそのまま
                        if line.endswith(punctuation):
                            formatted_lines.append(line)
                        else:
                            # 最後の行は「。」、それ以外は「、」
                            if i == len(lines) - 1:
                                formatted_lines.append(line + '。')
                            else:
                                formatted_lines.append(line + '、')

                    formatted_text = '\n'.join(formatted_lines)
                    st.session_state.formatted_text = formatted_text
                    progress_bar.progress(80)

                    filename = os.path.splitext(text_file.name)[0]
                    st.session_state.filename = filename
                    progress_bar.progress(100)
                    st.success("Complete!")
                else:
                    st.error("テキストファイルが空です")
            except Exception as e:
                st.error(f"テキスト読み込みエラー: {str(e)}")

with tab3:
    st.subheader("テキストを直接入力")

    direct_text = st.text_area(
        "テキストを貼り付けてください（自動整形されます）",
        height=250,
        placeholder="ここにテキストを貼り付け...\n\n例：\nこれもちょっとした誤解で\n落とし穴がいっぱいあるのです",
        key="direct_text_input"
    )

    if st.button("START", key="direct_text_btn"):
        if direct_text.strip():
            progress_bar = st.progress(0)
            progress_bar.progress(20)

            # テキスト整形：改行ごとに句読点を追加
            lines = direct_text.strip().split('\n')
            formatted_lines = []
            punctuation = ('。', '、', '！', '？', '!', '?', '．', '，')

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                if line.endswith(punctuation):
                    formatted_lines.append(line)
                else:
                    if i == len(lines) - 1:
                        formatted_lines.append(line + '。')
                    else:
                        formatted_lines.append(line + '、')

            formatted_text = '\n'.join(formatted_lines)
            st.session_state.formatted_text = formatted_text
            st.session_state.transcribed_text = direct_text
            progress_bar.progress(50)

            # ファイル名生成
            if gemini:
                # Gemini APIでファイル名を生成
                filename = gemini.generate_filename(formatted_text)
                st.session_state.filename = filename or "output"
            else:
                # テキストの最初の行から自動生成（句読点除去、最大20文字）
                first_line = formatted_lines[0] if formatted_lines else "output"
                clean_name = first_line.replace('、', '').replace('。', '').replace('！', '').replace('？', '')
                st.session_state.filename = clean_name[:20] if len(clean_name) > 20 else clean_name

            progress_bar.progress(100)
            st.success("Complete!")
        else:
            st.error("テキストを入力してください")

with tab4:
    st.subheader("音声アップロード")
    st.info("外部TTSで生成した音声をアップロード → 自動で文字起こし＆整形 → 動画生成（動画から生成と同じフロー）")

    # 1. 音声アップロード → 自動で文字起こし＆整形
    st.markdown("### 1. 音声ファイルをアップロード")
    uploaded_audio = st.file_uploader(
        "音声ファイルを選択（アップロード後、自動で文字起こし＆整形）",
        type=["wav", "mp3", "m4a", "aac", "ogg"],
        accept_multiple_files=False,
        key="audio_uploader"
    )

    if uploaded_audio and not st.session_state.get('audio_upload_mode'):
        # 新しい音声がアップロードされたら自動で処理開始
        st.success(f"アップロード: {uploaded_audio.name}")
        st.audio(uploaded_audio, format=f"audio/{uploaded_audio.name.split('.')[-1]}")

        audio_filename = os.path.splitext(uploaded_audio.name)[0]

        if not gladia_api_key:
            st.error("API設定でGladia APIキーを入力してください")
        elif not gemini_api_key:
            st.error("API設定でGemini APIキーを入力してください（テキスト整形に必要）")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_audio.read())
                tmp_audio_path = tmp_file.name
            uploaded_audio.seek(0)

            try:
                # Step 1: Gladia文字起こし
                status_text.text("音声を文字起こし中（Gladia API）...")
                progress_bar.progress(10)

                result = gladia.transcribe_from_file_with_timestamps(tmp_audio_path, language="ja")

                if result and result.get("segments"):
                    gladia_segments = result["segments"]
                    gladia_words = result.get("words", [])  # 単語レベルのタイムスタンプ
                    raw_text = ' '.join([seg['text'] for seg in gladia_segments])
                    progress_bar.progress(40)
                    status_text.text(f"文字起こし完了: {len(gladia_segments)} セグメント, {len(gladia_words)} 単語")

                    # Step 2: Geminiで整形（動画から生成と同じ）
                    status_text.text("テキストを整形中（Gemini API）...")
                    progress_bar.progress(50)

                    formatted_text = gemini.format_text(raw_text)

                    if formatted_text:
                        progress_bar.progress(70)

                        # ファイル名生成
                        status_text.text("ファイル名を生成中...")
                        generated_filename = gemini.generate_filename(formatted_text)
                        if generated_filename:
                            audio_filename = generated_filename

                        progress_bar.progress(100)
                        status_text.text("Complete!")

                        # セッションに保存（単語リストも保存）
                        st.session_state.timestamped_segments = gladia_segments
                        st.session_state.gladia_words = gladia_words  # 単語レベルのタイムスタンプ
                        st.session_state.audio_file_data = uploaded_audio.read()
                        uploaded_audio.seek(0)
                        st.session_state.filename = audio_filename
                        st.session_state.audio_upload_mode = True
                        st.session_state.audio_text_editor = formatted_text

                        st.success(f"Complete! 整形済みテキスト生成完了（{len(gladia_words)}単語のタイムスタンプ取得）")
                        st.rerun()
                    else:
                        st.error("テキスト整形に失敗しました")
                else:
                    st.error("文字起こしに失敗しました")

                if os.path.exists(tmp_audio_path):
                    os.unlink(tmp_audio_path)

            except Exception as e:
                st.error(f"エラー: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
                if os.path.exists(tmp_audio_path):
                    os.unlink(tmp_audio_path)

    # 2. テキスト編集（動画から生成と同じUI）
    if st.session_state.get('audio_text_editor') and st.session_state.get('audio_upload_mode'):
        st.markdown("---")
        st.markdown("### 2. テキストを確認・編集")

        edited_text = st.text_area(
            "整形済みテキスト（1行14文字以内、句読点で終わる）",
            value=st.session_state.audio_text_editor,
            height=300,
            key="audio_text_area"
        )
        st.session_state.audio_text_editor = edited_text

        # 行数カウント
        lines = [line.strip() for line in edited_text.strip().split('\n') if line.strip()]
        word_count = len(st.session_state.gladia_words) if st.session_state.get('gladia_words') else 0

        st.success(f"**{len(lines)}行** / {word_count}単語のタイムスタンプで同期")

        # 3. 動画生成
        st.markdown("---")
        st.markdown("### 3. 動画を生成")

        if st.button("GENERATE VIDEO", key="generate_audio_upload_video_btn"):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("タイムスタンプを計算中...")
                progress_bar.progress(5)

                # テキストを行に分割
                lines = [line.strip() for line in edited_text.strip().split('\n') if line.strip()]
                gladia_words = st.session_state.get('gladia_words', [])

                # 単語レベルのタイムスタンプを使って各行のタイミングを計算
                def calculate_line_timestamps(lines, words):
                    """各行に含まれる単語を特定し、タイムスタンプを計算"""
                    import re

                    # 句読点を除去する関数
                    def normalize(text):
                        return re.sub(r'[、。,.\s　]', '', text)

                    # 全単語を結合した文字列
                    all_words_text = ''.join([w['word'] for w in words])
                    all_words_text_normalized = normalize(all_words_text)

                    # 各行のテキスト（句読点除去）
                    lines_normalized = [normalize(line) for line in lines]

                    segments = []
                    word_index = 0
                    current_pos = 0  # 単語リスト内での文字位置

                    for line_idx, line in enumerate(lines):
                        line_norm = lines_normalized[line_idx]
                        if not line_norm:
                            # 空行の場合はスキップ
                            continue

                        # この行の最初の単語を見つける
                        start_word_idx = word_index
                        chars_matched = 0

                        # 行の文字数分の単語を消費
                        while word_index < len(words) and chars_matched < len(line_norm):
                            word = words[word_index]['word']
                            word_norm = normalize(word)
                            chars_matched += len(word_norm)
                            word_index += 1

                        end_word_idx = word_index - 1 if word_index > start_word_idx else start_word_idx

                        # この行のタイムスタンプを設定
                        if start_word_idx < len(words) and end_word_idx < len(words):
                            start_time = words[start_word_idx]['start']
                            end_time = words[end_word_idx]['end']
                        else:
                            # フォールバック: 均等分割
                            total_duration = words[-1]['end'] if words else 1
                            segment_duration = total_duration / len(lines)
                            start_time = line_idx * segment_duration
                            end_time = (line_idx + 1) * segment_duration

                        segments.append({
                            "start": start_time,
                            "end": end_time,
                            "text": line
                        })

                    return segments

                if gladia_words:
                    # 単語レベルのタイムスタンプを使用
                    segments = calculate_line_timestamps(lines, gladia_words)
                    status_text.text(f"単語レベルのタイムスタンプで同期: {len(segments)}行")
                else:
                    # フォールバック: 均等分割
                    gladia_segments = st.session_state.timestamped_segments
                    total_start = gladia_segments[0]['start']
                    total_end = gladia_segments[-1]['end']
                    total_duration = total_end - total_start
                    segment_duration = total_duration / len(lines) if len(lines) > 0 else 1

                    segments = []
                    for i, text in enumerate(lines):
                        start_time = total_start + (i * segment_duration)
                        end_time = total_start + ((i + 1) * segment_duration)
                        segments.append({
                            "start": start_time,
                            "end": end_time,
                            "text": text
                        })

                progress_bar.progress(10)

                # 一時ファイルに音声を保存
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(st.session_state.audio_file_data)
                    tmp_audio_path = tmp_file.name

                def update_progress(current, total, message):
                    progress = int(10 + (current / total) * 85)
                    progress_bar.progress(progress)

                video_gen = VideoGeneratorFFmpeg(
                    background_color=(0, 255, 0),
                    voicevox_url=voicevox_url
                )

                video_transparent, video_preview = video_gen.create_video_from_timestamped_segments(
                    audio_path=tmp_audio_path,
                    segments=segments,
                    width=1080,
                    height=1920,
                    transparent=True,
                    progress_callback=update_progress
                )

                os.unlink(tmp_audio_path)

                if video_transparent:
                    st.session_state.generated_video = video_transparent
                    st.session_state.preview_video = video_preview
                    progress_bar.progress(100)
                    status_text.text("動画生成完了！")
                    st.rerun()

            except Exception as e:
                st.error(f"動画生成エラー: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

    # プレビューとダウンロード
    if st.session_state.get('generated_video') and st.session_state.get('preview_video') and st.session_state.get('audio_upload_mode'):
        st.markdown("---")
        st.subheader("プレビュー")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            video_base64 = base64.b64encode(st.session_state.preview_video).decode()
            st.markdown(f'''
            <div class="iphone-frame">
                <div class="iphone-device">
                    <div class="iphone-dynamic-island"></div>
                    <div class="iphone-screen">
                        <video controls playsinline>
                            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                        </video>
                    </div>
                    <div class="iphone-home-indicator"></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        st.info("プレビューはチェッカー背景で表示。ダウンロードは透過動画（MOV）です。")

        st.download_button(
            label="DOWNLOAD VIDEO (.mov)",
            data=st.session_state.generated_video,
            file_name=f"{st.session_state.filename}.mov",
            mime="video/quicktime",
            key="download_audio_upload_video"
        )

        # SNSコンテンツ生成
        st.markdown("---")
        st.subheader("タイトル・紹介文・ハッシュタグ生成")

        if st.button("GENERATE SNS", key="generate_sns_audio_upload_btn"):
            if not gemini_api_key:
                st.error("API設定でGemini APIキーを入力してください")
            elif not st.session_state.audio_text_editor:
                st.error("テキストが見つかりません")
            else:
                progress_bar = st.progress(0)
                progress_bar.progress(30)
                sns_content = gemini.generate_metadata(st.session_state.audio_text_editor)
                progress_bar.progress(90)
                if sns_content:
                    st.session_state.audio_upload_sns_content = sns_content
                    progress_bar.progress(100)
                    st.rerun()

        if st.session_state.get('audio_upload_sns_content'):
            st.markdown("**生成されたコンテンツ（編集可能）**")
            sns_editor = st.text_area(
                "タイトル・紹介文・ハッシュタグ",
                value=st.session_state.audio_upload_sns_content,
                height=300,
                key="audio_upload_sns_editor"
            )

            # 全テキストをまとめてダウンロード
            full_text = "【整形テキスト】\n" + st.session_state.audio_text_editor
            full_text += "\n\n" + sns_editor

            st.download_button(
                label="DOWNLOAD ALL TEXT",
                data=full_text,
                file_name=f"{st.session_state.filename}_full.txt",
                mime="text/plain",
                key="download_audio_upload_full_text"
            )

# セクション2: 整形済みテキスト表示
if st.session_state.formatted_text:
    st.header("2. テキスト編集")

    if "text_editor" not in st.session_state:
        st.session_state.text_editor = st.session_state.formatted_text

    if "filename" not in st.session_state or not st.session_state.filename:
        st.session_state.filename = "output"

    # テキストダウンロード用のフォーマット関数
    def format_text_for_download(text: str, target_length: int = 14) -> str:
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            chunks = []
            current_chunk = ""
            for char in line:
                if char in ['。', '、']:
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = ""
                else:
                    current_chunk += char
            if current_chunk:
                chunks.append(current_chunk)

            current_line = ""
            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue
                if not current_line:
                    current_line = chunk
                    continue
                combined_len = len(current_line + chunk)
                if combined_len > target_length + 4:
                    new_lines.append(current_line)
                    current_line = chunk
                elif abs(target_length - combined_len) <= abs(target_length - len(current_line)):
                    current_line += chunk
                else:
                    new_lines.append(current_line)
                    current_line = chunk
            if current_line:
                new_lines.append(current_line)
        return '\n'.join(new_lines)

    # 2カラムレイアウト：整形テキスト（左）とひらがな（右）
    col_text, col_hiragana = st.columns(2)

    with col_text:
        st.subheader("整形済みテキスト（動画表示用）")
        # text_areaの値を明示的に取得して保存
        current_text = st.text_area(
            "整形されたテキスト",
            value=st.session_state.get("text_editor", st.session_state.formatted_text),
            height=400,
            key="text_editor_widget"
        )
        # 編集されたテキストをセッションに保存
        st.session_state.text_editor = current_text

        formatted_main_text = format_text_for_download(current_text)
        st.download_button(
            label="DOWNLOAD TEXT",
            data=formatted_main_text,
            file_name=f"{st.session_state.filename}.txt",
            mime="text/plain",
            key="download_text"
        )

    with col_hiragana:
        st.subheader("ひらがな（音声生成用）")

        # ひらがなテキストを表示
        if st.session_state.hiragana_text:
            if "hiragana_editor" not in st.session_state:
                st.session_state.hiragana_editor = st.session_state.hiragana_text

            st.text_area("ひらがなテキスト（編集可能）", height=400, key="hiragana_editor")

            if st.button("再変換", key="convert_hiragana_btn"):
                if not gemini_api_key:
                    st.error("Gemini APIキーを入力してください")
                else:
                    with st.spinner("変換中..."):
                        hiragana_result = gemini.convert_to_hiragana(st.session_state.text_editor)
                        if hiragana_result:
                            st.session_state.hiragana_text = hiragana_result
                            st.session_state.hiragana_editor = hiragana_result
                            st.rerun()
                        else:
                            st.error("変換失敗")
        else:
            st.text_area("ひらがなテキスト", value="", height=400, disabled=True, key="hiragana_placeholder")

            if st.button("ひらがなに変換", key="convert_hiragana_btn_init"):
                if not gemini_api_key:
                    st.error("Gemini APIキーを入力してください")
                else:
                    with st.spinner("変換中..."):
                        hiragana_result = gemini.convert_to_hiragana(st.session_state.text_editor)
                        if hiragana_result:
                            st.session_state.hiragana_text = hiragana_result
                            st.session_state.hiragana_editor = hiragana_result
                            st.rerun()
                        else:
                            st.error("ひらがな変換に失敗しました")

    # ファイル名入力
    final_filename = st.text_input("ファイル名（編集可能）", value=st.session_state.filename, key="filename_input")

    # セクション3: 音声アップロード＆動画生成
    st.header("3. 音声アップロード＆動画生成")
    st.info("外部TTSで生成した音声をアップロードして動画を生成します")

    # 音声アップロード
    uploaded_audio_sec3 = st.file_uploader(
        "音声ファイルを選択",
        type=["wav", "mp3", "m4a", "aac", "ogg"],
        key="audio_uploader_sec3"
    )

    if uploaded_audio_sec3:
        st.audio(uploaded_audio_sec3, format=f"audio/{uploaded_audio_sec3.name.split('.')[-1]}")

        if st.button("GENERATE VIDEO", key="generate_video_sec3_btn"):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("音声ファイルを処理中...")
                progress_bar.progress(10)

                # 音声ファイルを一時保存
                uploaded_audio_sec3.seek(0)
                audio_data = uploaded_audio_sec3.read()

                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio_sec3.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_audio_path = tmp_file.name

                # テキストを行に分割
                display_text = st.session_state.text_editor
                lines = [line.strip() for line in display_text.strip().split('\n') if line.strip()]

                status_text.text("文字起こし中（タイムスタンプ取得）...")
                progress_bar.progress(20)

                # Gladiaで音声のタイムスタンプを取得
                if gladia_api_key:
                    result = gladia.transcribe_from_file_with_timestamps(tmp_audio_path, language="ja")
                    if result and result.get("words"):
                        gladia_words = result["words"]

                        # 単語レベルのタイムスタンプを使って各行のタイミングを計算
                        import re
                        def normalize(text):
                            return re.sub(r'[、。,.\s　]', '', text)

                        segments = []
                        word_index = 0

                        for line_idx, line in enumerate(lines):
                            line_norm = normalize(line)
                            if not line_norm:
                                continue

                            start_word_idx = word_index
                            chars_matched = 0

                            while word_index < len(gladia_words) and chars_matched < len(line_norm):
                                word = gladia_words[word_index]['word']
                                word_norm = normalize(word)
                                chars_matched += len(word_norm)
                                word_index += 1

                            end_word_idx = word_index - 1 if word_index > start_word_idx else start_word_idx

                            if start_word_idx < len(gladia_words) and end_word_idx < len(gladia_words):
                                start_time = gladia_words[start_word_idx]['start']
                                end_time = gladia_words[end_word_idx]['end']
                                # end_timeがstart_time以下の場合は修正
                                if end_time <= start_time:
                                    end_time = start_time + 0.5
                            else:
                                total_duration = gladia_words[-1]['end'] if gladia_words else 1
                                segment_duration = total_duration / len(lines)
                                start_time = line_idx * segment_duration
                                end_time = (line_idx + 1) * segment_duration

                            # 最小持続時間を保証（0.1秒以上）
                            if end_time - start_time < 0.1:
                                end_time = start_time + 0.5

                            segments.append({
                                "start": start_time,
                                "end": end_time,
                                "text": line
                            })

                        status_text.text(f"タイムスタンプ取得完了: {len(segments)}行")
                    else:
                        st.error("タイムスタンプの取得に失敗しました")
                        os.unlink(tmp_audio_path)
                        st.stop()
                else:
                    st.error("Gladia APIキーを設定してください")
                    os.unlink(tmp_audio_path)
                    st.stop()

                progress_bar.progress(40)
                status_text.text("動画を生成中...")

                def update_progress(current, total, message):
                    progress = int(40 + (current / total) * 50)
                    progress_bar.progress(progress)

                video_gen = VideoGeneratorFFmpeg(
                    background_color=(0, 255, 0),
                    voicevox_url=voicevox_url
                )

                video_transparent, video_preview = video_gen.create_video_from_timestamped_segments(
                    audio_path=tmp_audio_path,
                    segments=segments,
                    width=1080,
                    height=1920,
                    transparent=True,
                    progress_callback=update_progress
                )

                os.unlink(tmp_audio_path)

                if video_transparent:
                    st.session_state.generated_video = video_transparent
                    st.session_state.preview_video = video_preview
                    progress_bar.progress(100)
                    status_text.text("動画生成完了！")
                    st.rerun()

            except Exception as e:
                st.error(f"動画生成エラー: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

    # 動画プレビューとダウンロード
    if st.session_state.get('generated_video') and st.session_state.get('preview_video'):
        st.subheader("プレビュー")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            video_base64 = base64.b64encode(st.session_state.preview_video).decode()
            st.markdown(f'''
            <div class="iphone-frame">
                <div class="iphone-device">
                    <div class="iphone-dynamic-island"></div>
                    <div class="iphone-screen">
                        <video controls playsinline>
                            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                        </video>
                    </div>
                    <div class="iphone-home-indicator"></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        st.info("プレビューはチェッカー背景で表示。ダウンロードは透過動画（MOV）です。")

        st.download_button(
            label="DOWNLOAD VIDEO (.mov)",
            data=st.session_state.generated_video,
            file_name=f"{final_filename}.mov",
            mime="video/quicktime",
            key="download_video_sec3"
        )

    # セクション4: SNSコンテンツ生成
    st.header("4. タイトル・紹介文・ハッシュタグ生成")

    if st.button("GENERATE SNS", key="generate_sns_content_btn"):
        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを入力してください")
        elif not st.session_state.text_editor:
            st.error("テキストが見つかりません")
        else:
            progress_bar = st.progress(0)
            progress_bar.progress(30)
            sns_content = gemini.generate_metadata(st.session_state.text_editor)
            progress_bar.progress(90)
            if sns_content:
                st.session_state.generated_sns_content = sns_content
                progress_bar.progress(100)

    if st.session_state.generated_sns_content:
        st.subheader("生成されたコンテンツ（編集可能）")
        if "sns_content_editor" not in st.session_state:
            st.session_state.sns_content_editor = st.session_state.generated_sns_content
        st.text_area("タイトル・紹介文・ハッシュタグ", height=400, key="sns_content_editor")

        # 全テキストをまとめてダウンロード
        full_text = "【整形テキスト】\n" + formatted_main_text

        # 言い換えテキストがあれば追加
        if st.session_state.rephrased_result:
            full_text += "\n\n【言い換えテキスト】\n" + st.session_state.rephrased_result

        full_text += "\n\n" + st.session_state.sns_content_editor

        st.download_button(
            label="DOWNLOAD ALL TEXT",
            data=full_text,
            file_name=f"{final_filename}_full.txt",
            mime="text/plain",
            key="download_full_text"
        )

# フッター
st.markdown("---")
st.markdown("Made with Streamlit, Gladia API, Gemini API, and FFmpeg | **v3**")
