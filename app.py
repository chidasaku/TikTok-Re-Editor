import streamlit as st
import streamlit.components.v1 as components
import os
import tempfile
import base64
import json
from dotenv import load_dotenv
from utils.transcription import GladiaAPI
from utils.text_formatter import GeminiFormatter
from utils.voicevox import VoiceVoxAPI
from utils.video_generator_ffmpeg import VideoGeneratorFFmpeg

# 環境変数を読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="TikTok Re-Editor",
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

    /* ファイルアップローダー内のテキストを左詰め */
    [data-testid="stFileUploader"] section > div {
        text-align: left !important;
        align-items: flex-start !important;
    }

    [data-testid="stFileUploader"] small {
        color: rgba(255, 255, 255, 0.7) !important;
        text-align: left !important;
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

    /* サイドバー */
    .stSidebar {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }

    .stSidebar *,
    .stSidebar h1, .stSidebar h2, .stSidebar h3,
    .stSidebar p, .stSidebar span, .stSidebar div,
    .stSidebar label, .stSidebar strong {
        color: #000000 !important;
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
if 'video_transparent' not in st.session_state:
    st.session_state.video_transparent = False
if 'audio_text' not in st.session_state:
    st.session_state.audio_text = None  # 音声生成時のテキストを保存
if 'rephrased_result' not in st.session_state:
    st.session_state.rephrased_result = None  # AI再編集結果
if 'hiragana_text' not in st.session_state:
    st.session_state.hiragana_text = None  # ひらがな変換テキスト（音声生成用）

# API設定（折りたたみ式）- タイトルの上に配置
with st.expander("⚙️ API設定", expanded=False):
    # Streamlit Cloud secrets または 環境変数 または 手動入力
    def get_secret(key, default=""):
        # 1. Streamlit secrets (Cloud)
        try:
            if key in st.secrets:
                return st.secrets[key]
        except:
            pass
        # 2. 環境変数
        val = os.getenv(key, default)
        if val == "ここに貼り付け":
            val = ""
        return val

    env_gladia = get_secret("GLADIA_API_KEY", "")
    env_gemini = get_secret("GEMINI_API_KEY", "")
    env_voicevox = get_secret("VOICEVOX_API_URL", "http://localhost:50021")

    col1, col2 = st.columns(2)
    with col1:
        gladia_api_key = st.text_input("🎤 Gladia API Key", value=env_gladia, type="password")
        st.markdown('<a href="https://www.gladia.io/" target="_blank" style="color: #00f2ea; font-size: 12px;">→ Gladia APIキーを取得</a>', unsafe_allow_html=True)
    with col2:
        gemini_api_key = st.text_input("✨ Gemini API Key", value=env_gemini, type="password")
        st.markdown('<a href="https://aistudio.google.com/apikey" target="_blank" style="color: #00f2ea; font-size: 12px;">→ Gemini APIキーを取得</a>', unsafe_allow_html=True)

    voicevox_url = st.text_input(
        "🎙️ VOICEVOX URL",
        value=env_voicevox,
        help="ローカル: http://localhost:50021 / ngrok使用時: https://xxxx.ngrok.io"
    )

    st.markdown("""
    💡 **ヒント**
    - テキストファイルから生成する場合、Gladia APIは不要です
    - VoiceVoxは各自のPCで起動してください（ブラウザから直接接続します）
    """)

    # Web版でのVOICEVOX使用方法の詳細説明
    with st.expander("🌐 Web版でVOICEVOXを使う方法", expanded=False):
        st.markdown("""
        **Web版（Streamlit Cloud）でVOICEVOXを使う方法：**

        ### 新しい方式（ngrok不要！）
        このアプリは、**ブラウザから直接あなたのPCのVOICEVOXに接続**します。
        ngrokやCloudflare Tunnelは不要です。

        ### 設定手順

        **Step 1: VOICEVOXをインストール**
        - https://voicevox.hiroshiba.jp/ からダウンロード
        - インストールして起動

        **Step 2: このアプリを開く**
        - ブラウザでこのページを開く
        - 音声合成セクションで「VOICEVOXに接続しました」と表示されればOK

        ### 仕組み
        - ブラウザのJavaScriptがあなたのPC上のVOICEVOX（localhost:50021）に直接接続
        - 音声データはあなたのPC内で処理されます
        - サーバーを経由しないので、他の誰かのPCに依存しません

        ### 注意事項
        - VOICEVOXは使用中は起動したままにしてください
        - 動画生成機能はWeb版では利用できません（ローカル版をご利用ください）
        """)

# タイトル
st.markdown('<h1 translate="no">🎬 TikTok Re-Editor</h1>', unsafe_allow_html=True)
st.markdown("動画をアップロードして、文字起こし → 整形 → 音声合成 → **透過動画生成**を自動実行")

# APIクライアントの初期化
gladia = GladiaAPI(gladia_api_key) if gladia_api_key else None
gemini = GeminiFormatter(gemini_api_key) if gemini_api_key else None
voicevox = VoiceVoxAPI(voicevox_url)

# セクション1: 入力ソース選択
st.header("📥 1. 入力ソース選択")

tab1, tab2, tab3 = st.tabs(["📹 動画から生成", "📄 ファイルから生成", "✏️ テキスト入力"])

with tab1:
    st.subheader("動画アップロード")

    uploaded_file = st.file_uploader(
        "動画ファイルを選択してください",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        key="video_uploader"
    )

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        st.info(f"📁 アップロードされたファイル: {uploaded_file.name}")

        if st.button("START", key="transcribe_btn"):
            if not gladia_api_key or not gemini_api_key:
                st.error("⚠️ サイドバーでGladia APIキーとGemini APIキーを入力してください")
                st.stop()

            progress_bar = st.progress(0)

            progress_bar.progress(10)
            audio_url = gladia.upload_file(tmp_file_path)

            if audio_url:
                progress_bar.progress(30)
                transcribed = gladia.transcribe(audio_url, language="ja")

                if transcribed:
                    st.session_state.transcribed_text = transcribed
                    progress_bar.progress(60)
                    formatted = gemini.format_text(transcribed)

                    if formatted:
                        st.session_state.formatted_text = formatted
                        progress_bar.progress(80)
                        filename = gemini.generate_filename(formatted)
                        st.session_state.filename = filename or "output"
                        progress_bar.progress(100)
                        st.success("✅ Complete!")

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
        st.info(f"📁 アップロードされたファイル: {text_file.name}")

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
                    st.success("✅ Complete!")
                else:
                    st.error("⚠️ テキストファイルが空です")
            except Exception as e:
                st.error(f"❌ テキスト読み込みエラー: {str(e)}")

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
            st.success("✅ Complete!")
        else:
            st.error("⚠️ テキストを入力してください")

# セクション2: 整形済みテキスト表示
if st.session_state.formatted_text:
    st.header("📝 2. テキスト編集")

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
        st.subheader("📄 整形済みテキスト（動画表示用）")
        st.text_area("整形されたテキスト", height=400, key="text_editor")

        formatted_main_text = format_text_for_download(st.session_state.text_editor)
        st.download_button(
            label="DOWNLOAD TEXT",
            data=formatted_main_text,
            file_name=f"{st.session_state.filename}.txt",
            mime="text/plain",
            key="download_text"
        )

    with col_hiragana:
        st.subheader("🔤 ひらがな（音声生成用）")

        # ひらがなテキストを表示
        if st.session_state.hiragana_text:
            if "hiragana_editor" not in st.session_state:
                st.session_state.hiragana_editor = st.session_state.hiragana_text

            st.text_area("ひらがなテキスト（編集可能）", height=400, key="hiragana_editor")

            if st.button("再変換", key="convert_hiragana_btn"):
                if not gemini_api_key:
                    st.error("⚠️ Gemini APIキーを入力してください")
                else:
                    with st.spinner("変換中..."):
                        hiragana_result = gemini.convert_to_hiragana(st.session_state.text_editor)
                        if hiragana_result:
                            st.session_state.hiragana_text = hiragana_result
                            st.session_state.hiragana_editor = hiragana_result
                            st.rerun()
                        else:
                            st.error("❌ 変換失敗")
        else:
            st.text_area("ひらがなテキスト", value="", height=400, disabled=True, key="hiragana_placeholder")

            if st.button("ひらがなに変換", key="convert_hiragana_btn_init"):
                if not gemini_api_key:
                    st.error("⚠️ Gemini APIキーを入力してください")
                else:
                    with st.spinner("変換中..."):
                        hiragana_result = gemini.convert_to_hiragana(st.session_state.text_editor)
                        if hiragana_result:
                            st.session_state.hiragana_text = hiragana_result
                            st.session_state.hiragana_editor = hiragana_result
                            st.rerun()
                        else:
                            st.error("❌ ひらがな変換に失敗しました")

    # ファイル名入力
    final_filename = st.text_input("ファイル名（編集可能）", value=st.session_state.filename, key="filename_input")

    # セクション3: VOICEVOX設定（クライアントサイド対応）
    st.header("🎙️ 3. 音声合成")

    st.info("💡 **各自のPCでVOICEVOXを起動してください。** ブラウザから直接あなたのPCのVOICEVOXに接続します。")

    # 音声生成用テキストを準備
    if st.session_state.hiragana_text and "hiragana_editor" in st.session_state:
        voice_text = st.session_state.hiragana_editor
        st.success("🔤 音声生成にはひらがなテキストを使用します")
    else:
        voice_text = st.session_state.text_editor
        st.warning("⚠️ ひらがな変換されていません。整形テキストをそのまま使用します")

    total_lines = len([line.strip() for line in voice_text.strip().split('\n') if line.strip()])
    st.info(f"📊 生成される音声行数: **{total_lines}行**")

    # クライアントサイドVOICEVOX JavaScript コンポーネント
    voicevox_js = """
    <style>
        .voicevox-container {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            background: #1a1a1a;
            border-radius: 10px;
            border: 2px solid #00f2ea;
        }
        .voicevox-row {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .voicevox-select {
            flex: 1;
            min-width: 200px;
        }
        .voicevox-select label {
            display: block;
            color: #fff;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .voicevox-select select {
            width: 100%;
            padding: 10px;
            background: #000;
            color: #fff;
            border: 2px solid #00f2ea;
            border-radius: 8px;
            font-size: 14px;
        }
        .voicevox-btn {
            background: #000;
            color: #fff;
            border: 2px solid #00f2ea;
            border-radius: 10px;
            padding: 12px 30px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.3s;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .voicevox-btn:hover:not(:disabled) {
            background: #1a1a1a;
            box-shadow: 0 0 20px rgba(0, 242, 234, 0.8);
        }
        .voicevox-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .voicevox-btn.generating {
            background: #00f2ea;
            color: #000;
        }
        .voicevox-status {
            color: #fff;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .voicevox-status.error {
            background: rgba(254, 44, 85, 0.3);
            border: 1px solid #fe2c55;
        }
        .voicevox-status.success {
            background: rgba(0, 242, 234, 0.3);
            border: 1px solid #00f2ea;
        }
        .voicevox-status.info {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid #666;
        }
        .voicevox-progress {
            width: 100%;
            height: 20px;
            background: #333;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .voicevox-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #00f2ea, #fe2c55);
            transition: width 0.3s;
        }
        .voicevox-audio {
            width: 100%;
            margin: 15px 0;
        }
        .voicevox-slider {
            width: 100%;
        }
        .voicevox-slider input[type="range"] {
            width: 100%;
            accent-color: #00f2ea;
        }
    </style>

    <div class="voicevox-container">
        <div id="voicevox-status" class="voicevox-status info">
            🔄 VOICEVOXに接続中...
        </div>

        <div class="voicevox-row">
            <div class="voicevox-select">
                <label>🎭 キャラクター</label>
                <select id="speaker-select" disabled>
                    <option>読み込み中...</option>
                </select>
            </div>
            <div class="voicevox-select">
                <label>🎨 スタイル</label>
                <select id="style-select" disabled>
                    <option>-</option>
                </select>
            </div>
        </div>

        <div class="voicevox-row">
            <div class="voicevox-select voicevox-slider">
                <label>⚡ 話速: <span id="speed-value">1.0</span>x</label>
                <input type="range" id="speed-slider" min="0.5" max="2.0" step="0.1" value="1.0">
            </div>
            <div class="voicevox-select voicevox-slider">
                <label>⏸️ 間の長さ: <span id="pause-value">1.0</span></label>
                <input type="range" id="pause-slider" min="0.0" max="2.0" step="0.1" value="1.0">
            </div>
        </div>

        <div>
            <button class="voicevox-btn" id="preview-btn" disabled>PREVIEW</button>
            <button class="voicevox-btn" id="generate-btn" disabled>GENERATE AUDIO</button>
        </div>

        <div id="progress-container" style="display:none;">
            <div class="voicevox-progress">
                <div class="voicevox-progress-bar" id="progress-bar" style="width: 0%"></div>
            </div>
            <div id="progress-text" style="color: #fff; text-align: center;"></div>
        </div>

        <div id="audio-container" style="display:none;">
            <audio id="audio-player" class="voicevox-audio" controls></audio>
            <button class="voicevox-btn" id="download-btn">DOWNLOAD AUDIO</button>
        </div>
    </div>

    <script>
    (function() {
        const VOICEVOX_URL = 'http://localhost:50021';
        const TEXT_TO_SPEAK = `""" + voice_text.replace('`', '\\`').replace('\n', '\\n') + """`;
        const FILENAME = '""" + final_filename + """';

        let speakers = [];
        let currentSpeakerId = null;
        let generatedAudioBlob = null;

        const statusDiv = document.getElementById('voicevox-status');
        const speakerSelect = document.getElementById('speaker-select');
        const styleSelect = document.getElementById('style-select');
        const speedSlider = document.getElementById('speed-slider');
        const pauseSlider = document.getElementById('pause-slider');
        const speedValue = document.getElementById('speed-value');
        const pauseValue = document.getElementById('pause-value');
        const previewBtn = document.getElementById('preview-btn');
        const generateBtn = document.getElementById('generate-btn');
        const progressContainer = document.getElementById('progress-container');
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const audioContainer = document.getElementById('audio-container');
        const audioPlayer = document.getElementById('audio-player');
        const downloadBtn = document.getElementById('download-btn');

        // スライダーの値更新
        speedSlider.addEventListener('input', () => {
            speedValue.textContent = speedSlider.value;
        });
        pauseSlider.addEventListener('input', () => {
            pauseValue.textContent = pauseSlider.value;
        });

        // VOICEVOXに接続してスピーカー一覧を取得
        async function loadSpeakers() {
            try {
                const response = await fetch(VOICEVOX_URL + '/speakers');
                if (!response.ok) throw new Error('接続失敗');
                speakers = await response.json();

                speakerSelect.innerHTML = '';
                speakers.forEach((speaker, idx) => {
                    const option = document.createElement('option');
                    option.value = idx;
                    option.textContent = speaker.name;
                    if (speaker.name === '青山龍星') option.selected = true;
                    speakerSelect.appendChild(option);
                });

                speakerSelect.disabled = false;
                updateStyles();

                statusDiv.className = 'voicevox-status success';
                statusDiv.innerHTML = '✅ VOICEVOXに接続しました（あなたのPCで動作中）';

                previewBtn.disabled = false;
                generateBtn.disabled = false;

            } catch (error) {
                statusDiv.className = 'voicevox-status error';
                statusDiv.innerHTML = `❌ VOICEVOXに接続できません<br><br>
                    <strong>確認してください：</strong><br>
                    1. あなたのPCでVOICEVOXを起動していますか？<br>
                    2. VOICEVOXをダウンロード: <a href="https://voicevox.hiroshiba.jp/" target="_blank" style="color:#00f2ea;">https://voicevox.hiroshiba.jp/</a>`;
            }
        }

        // スタイル一覧を更新
        function updateStyles() {
            const speakerIdx = speakerSelect.value;
            const speaker = speakers[speakerIdx];
            if (!speaker) return;

            styleSelect.innerHTML = '';
            speaker.styles.forEach(style => {
                const option = document.createElement('option');
                option.value = style.id;
                option.textContent = style.name;
                styleSelect.appendChild(option);
            });
            styleSelect.disabled = false;
            currentSpeakerId = parseInt(styleSelect.value);
        }

        speakerSelect.addEventListener('change', updateStyles);
        styleSelect.addEventListener('change', () => {
            currentSpeakerId = parseInt(styleSelect.value);
        });

        // プレビュー音声生成
        previewBtn.addEventListener('click', async () => {
            previewBtn.disabled = true;
            previewBtn.textContent = '生成中...';

            try {
                const audio = await generateVoice('こんにちは、VOICEVOXです。', currentSpeakerId, 1.0, 1.0);
                if (audio) {
                    const url = URL.createObjectURL(audio);
                    const previewAudio = new Audio(url);
                    previewAudio.play();
                }
            } catch (e) {
                alert('プレビュー生成に失敗しました');
            }

            previewBtn.disabled = false;
            previewBtn.textContent = 'PREVIEW';
        });

        // 音声生成
        async function generateVoice(text, speakerId, speed, pauseLength) {
            // audio_query
            const queryRes = await fetch(VOICEVOX_URL + '/audio_query?text=' + encodeURIComponent(text) + '&speaker=' + speakerId, {
                method: 'POST'
            });
            if (!queryRes.ok) throw new Error('audio_query failed');
            const query = await queryRes.json();

            query.speedScale = speed;
            query.pauseLengthScale = pauseLength;

            // synthesis
            const synthRes = await fetch(VOICEVOX_URL + '/synthesis?speaker=' + speakerId, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(query)
            });
            if (!synthRes.ok) throw new Error('synthesis failed');

            return await synthRes.blob();
        }

        // WAVファイルを結合
        async function concatenateWavBlobs(blobs) {
            if (blobs.length === 0) return null;
            if (blobs.length === 1) return blobs[0];

            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const audioBuffers = [];

            for (const blob of blobs) {
                const arrayBuffer = await blob.arrayBuffer();
                const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                audioBuffers.push(audioBuffer);
            }

            // 合計の長さを計算
            const totalLength = audioBuffers.reduce((sum, buf) => sum + buf.length, 0);
            const sampleRate = audioBuffers[0].sampleRate;
            const numberOfChannels = audioBuffers[0].numberOfChannels;

            // 新しいバッファを作成
            const outputBuffer = audioContext.createBuffer(numberOfChannels, totalLength, sampleRate);

            let offset = 0;
            for (const buffer of audioBuffers) {
                for (let channel = 0; channel < numberOfChannels; channel++) {
                    outputBuffer.getChannelData(channel).set(buffer.getChannelData(channel), offset);
                }
                offset += buffer.length;
            }

            // WAVに変換
            return audioBufferToWavBlob(outputBuffer);
        }

        function audioBufferToWavBlob(buffer) {
            const numChannels = buffer.numberOfChannels;
            const sampleRate = buffer.sampleRate;
            const format = 1; // PCM
            const bitDepth = 16;

            const bytesPerSample = bitDepth / 8;
            const blockAlign = numChannels * bytesPerSample;
            const dataLength = buffer.length * blockAlign;
            const bufferLength = 44 + dataLength;

            const arrayBuffer = new ArrayBuffer(bufferLength);
            const view = new DataView(arrayBuffer);

            // WAV header
            writeString(view, 0, 'RIFF');
            view.setUint32(4, bufferLength - 8, true);
            writeString(view, 8, 'WAVE');
            writeString(view, 12, 'fmt ');
            view.setUint32(16, 16, true);
            view.setUint16(20, format, true);
            view.setUint16(22, numChannels, true);
            view.setUint32(24, sampleRate, true);
            view.setUint32(28, sampleRate * blockAlign, true);
            view.setUint16(32, blockAlign, true);
            view.setUint16(34, bitDepth, true);
            writeString(view, 36, 'data');
            view.setUint32(40, dataLength, true);

            // Write audio data
            let offset = 44;
            for (let i = 0; i < buffer.length; i++) {
                for (let channel = 0; channel < numChannels; channel++) {
                    const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]));
                    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
                    offset += 2;
                }
            }

            return new Blob([arrayBuffer], { type: 'audio/wav' });
        }

        function writeString(view, offset, string) {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        }

        // メイン音声生成
        generateBtn.addEventListener('click', async () => {
            const lines = TEXT_TO_SPEAK.split('\\n').filter(line => line.trim());
            if (lines.length === 0) {
                alert('テキストがありません');
                return;
            }

            generateBtn.disabled = true;
            generateBtn.classList.add('generating');
            generateBtn.textContent = '生成中...';
            progressContainer.style.display = 'block';
            audioContainer.style.display = 'none';

            const speed = parseFloat(speedSlider.value);
            const pauseLength = parseFloat(pauseSlider.value);
            const audioBlobs = [];

            try {
                for (let i = 0; i < lines.length; i++) {
                    const progress = ((i + 1) / lines.length) * 100;
                    progressBar.style.width = progress + '%';
                    progressText.textContent = `🎙️ 行 ${i + 1}/${lines.length} を生成中...`;

                    const blob = await generateVoice(lines[i], currentSpeakerId, speed, pauseLength);
                    if (blob) {
                        audioBlobs.push(blob);
                    }
                }

                progressText.textContent = '🔗 音声を結合中...';

                // 結合
                generatedAudioBlob = await concatenateWavBlobs(audioBlobs);

                if (generatedAudioBlob) {
                    const url = URL.createObjectURL(generatedAudioBlob);
                    audioPlayer.src = url;
                    audioContainer.style.display = 'block';
                    progressText.textContent = '✅ 音声生成完了！';
                }

            } catch (error) {
                progressText.textContent = '❌ 音声生成に失敗しました: ' + error.message;
            }

            generateBtn.disabled = false;
            generateBtn.classList.remove('generating');
            generateBtn.textContent = 'GENERATE AUDIO';
        });

        // ダウンロード
        downloadBtn.addEventListener('click', () => {
            if (!generatedAudioBlob) return;

            const url = URL.createObjectURL(generatedAudioBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = FILENAME + '.wav';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });

        // 初期化
        loadSpeakers();
    })();
    </script>
    """

    components.html(voicevox_js, height=500)

    st.markdown("---")
    st.markdown("""
    **💡 この音声合成は、各自のPCで動作します：**
    - VOICEVOXをインストール・起動してください
    - ブラウザから直接あなたのPCの `localhost:50021` に接続します
    - 他の人のPCに依存しません
    """)

    # セクション4: 動画生成（Web版では制限あり）
    st.header("🎬 4. 動画生成")

    st.warning("""
    ⚠️ **動画生成はローカル環境でのみ利用可能です**

    Web版（Streamlit Cloud）では、動画生成機能は利用できません。
    動画を生成したい場合は、配布パッケージをダウンロードしてローカルで実行してください。

    **Web版でできること：**
    - 文字起こし・テキスト整形 ✅
    - 音声合成（各自のPCのVOICEVOX使用） ✅
    - SNSコンテンツ生成 ✅

    **ローカル版が必要：**
    - 透過動画生成
    """)

    # ローカル実行時のみ動画生成を表示
    if st.session_state.generated_audio:

        # クリップ数を表示
        video_gen = VideoGeneratorFFmpeg(
            background_color=(0, 255, 0),
            voicevox_url=voicevox_url
        )
        total_clips = video_gen.count_clips(st.session_state.text_editor)
        st.info(f"📊 生成されるクリップ数: **{total_clips}クリップ**")

        if st.button("GENERATE VIDEO", key="generate_video_btn"):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                clip_status = st.empty()

                status_text.text("動画生成を準備中...")

                # 進捗コールバック関数
                def update_progress(current, total, message):
                    # クリップ進捗（10%〜90%の範囲で表示）
                    progress = int(10 + (current / total) * 80)
                    progress_bar.progress(progress)
                    clip_status.text(f"📹 {message}")

                progress_bar.progress(5)

                # 音声用テキスト（保存されていれば使用、なければ現在のテキスト）
                audio_text = st.session_state.audio_text or st.session_state.text_editor
                # 表示用テキスト（現在のテキストエディタの内容）
                display_text = st.session_state.text_editor

                # 常に透過動画を生成（プレビュー用チェッカー動画も同時生成）
                video_transparent, video_preview = video_gen.create_green_screen_video(
                    audio_text=audio_text,
                    display_text=display_text,
                    speaker_id=st.session_state.speaker_id,
                    speed=st.session_state.speed,
                    width=1080,
                    height=1920,
                    transparent=True,
                    progress_callback=update_progress
                )

                progress_bar.progress(95)
                clip_status.text("🔗 クリップを結合中...")

                if video_transparent:
                    st.session_state.generated_video = video_transparent
                    st.session_state.preview_video = video_preview
                    progress_bar.progress(100)
                    status_text.text("✅ 動画生成完了！")
                    clip_status.text(f"✅ 全 {total_clips} クリップの生成が完了しました")
            except Exception as e:
                st.error(f"動画生成エラー: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

        if st.session_state.generated_video and st.session_state.preview_video:
            st.subheader("🎥 プレビュー")

            # iPhone風フレームでプレビュー表示（カラムで中央配置）
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

            st.info("💡 プレビューはチェッカー背景で表示。ダウンロードは透過動画（MOV）です。")

            st.download_button(
                label="DOWNLOAD VIDEO (.mov)",
                data=st.session_state.generated_video,
                file_name=f"{final_filename}.mov",
                mime="video/quicktime",
                key="download_video"
            )

    # セクション5: SNSコンテンツ生成
    st.header("📋 5. タイトル・紹介文・ハッシュタグ生成")

    if st.button("GENERATE SNS", key="generate_sns_content_btn"):
        if not gemini_api_key:
            st.error("⚠️ サイドバーでGemini APIキーを入力してください")
        elif not st.session_state.text_editor:
            st.error("⚠️ テキストが見つかりません")
        else:
            progress_bar = st.progress(0)
            progress_bar.progress(30)
            sns_content = gemini.generate_metadata(st.session_state.text_editor)
            progress_bar.progress(90)
            if sns_content:
                st.session_state.generated_sns_content = sns_content
                progress_bar.progress(100)

    if st.session_state.generated_sns_content:
        st.subheader("📝 生成されたコンテンツ（編集可能）")
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
st.markdown("Made with Streamlit, Gladia API, Gemini API, VOICEVOX, and FFmpeg")
