import streamlit as st
import os
import tempfile
import base64
from utils.transcription import GladiaAPI
from utils.text_formatter import GeminiFormatter
from utils.voicevox import VoiceVoxAPI
from utils.video_generator_ffmpeg import VideoGeneratorFFmpeg

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

# APIキー用セッションステート（入力値をセッション中保持）
if 'gladia_api_key' not in st.session_state:
    st.session_state.gladia_api_key = ""
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""
if 'voicevox_url' not in st.session_state:
    st.session_state.voicevox_url = "http://localhost:50021"

# API設定（折りたたみ式）- タイトルの上に配置
with st.expander("⚙️ API設定（初回は必ず開いて設定してください）", expanded=False):
    st.markdown("### 🔑 あなたのAPIキーを入力してください")
    st.markdown("※ APIキーは入力後、このセッション中のみ保持されます（サーバーには保存されません）")

    col1, col2 = st.columns(2)
    with col1:
        gladia_input = st.text_input(
            "🎤 Gladia API Key（動画文字起こし用）",
            value=st.session_state.gladia_api_key,
            type="password",
            key="gladia_input"
        )
        if gladia_input != st.session_state.gladia_api_key:
            st.session_state.gladia_api_key = gladia_input
        st.markdown('<a href="https://www.gladia.io/" target="_blank" style="color: #00f2ea; font-size: 12px;">→ Gladia APIキーを取得（無料枠あり）</a>', unsafe_allow_html=True)
    with col2:
        gemini_input = st.text_input(
            "✨ Gemini API Key（テキスト整形用）",
            value=st.session_state.gemini_api_key,
            type="password",
            key="gemini_input"
        )
        if gemini_input != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = gemini_input
        st.markdown('<a href="https://aistudio.google.com/apikey" target="_blank" style="color: #00f2ea; font-size: 12px;">→ Gemini APIキーを取得（無料）</a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎙️ VOICEVOX設定（音声合成）")
    st.markdown("""
    **VOICEVOXはあなたのパソコンで動かす必要があります：**
    1. [VOICEVOX公式サイト](https://voicevox.hiroshiba.jp/)からダウンロード・インストール
    2. VOICEVOXアプリを起動（起動するとローカルサーバーが立ち上がります）
    3. 下のURLはそのままでOK（デフォルト: `http://localhost:50021`）
    """)

    voicevox_input = st.text_input(
        "🎙️ VOICEVOX URL",
        value=st.session_state.voicevox_url,
        key="voicevox_input",
        help="VOICEVOXを起動すると http://localhost:50021 で接続できます"
    )
    if voicevox_input != st.session_state.voicevox_url:
        st.session_state.voicevox_url = voicevox_input

    st.markdown("---")
    st.info('💡 **テキスト入力から生成する場合**、Gladia/Gemini APIは不要です。VOICEVOXのみで動作します。')

# セッションステートから値を取得
gladia_api_key = st.session_state.gladia_api_key
gemini_api_key = st.session_state.gemini_api_key
voicevox_url = st.session_state.voicevox_url

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
    st.header("📝 2. 整形済みテキスト（編集可能）")

    if "text_editor" not in st.session_state:
        st.session_state.text_editor = st.session_state.formatted_text

    if "filename" not in st.session_state or not st.session_state.filename:
        st.session_state.filename = "output"

    st.text_area("整形されたテキスト", height=300, key="text_editor")

    # 元のテキストから変更があった場合、変更行を表示
    if st.session_state.formatted_text and st.session_state.formatted_text != st.session_state.text_editor:
        original_lines = [l.strip() for l in st.session_state.formatted_text.strip().split('\n') if l.strip()]
        current_lines = [l.strip() for l in st.session_state.text_editor.strip().split('\n') if l.strip()]
        changed_lines = []
        for i in range(max(len(original_lines), len(current_lines))):
            o = original_lines[i] if i < len(original_lines) else ""
            c = current_lines[i] if i < len(current_lines) else ""
            if o != c:
                changed_lines.append(str(i + 1))
        if changed_lines:
            st.warning(f"⚠️ 変更あり: {', '.join(changed_lines)}行目")

    final_filename = st.text_input("ファイル名（編集可能）", value=st.session_state.filename, key="filename_input")

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

    formatted_main_text = format_text_for_download(st.session_state.text_editor)

    st.download_button(
        label="DOWNLOAD TEXT",
        data=formatted_main_text,
        file_name=f"{final_filename}.txt",
        mime="text/plain",
        key="download_text"
    )

    # セクション3: VOICEVOX設定
    st.header("🎙️ 3. 音声合成")

    speakers = voicevox.get_speakers()

    if speakers:
        speaker_names = [speaker.get("name", "") for speaker in speakers]

        default_index = 0
        if "青山龍星" in speaker_names:
            default_index = speaker_names.index("青山龍星")

        col1, col2 = st.columns(2)

        with col1:
            selected_speaker_name = st.selectbox("🎭 キャラクター選択", speaker_names, index=default_index)

        selected_speaker = next((s for s in speakers if s.get("name") == selected_speaker_name), None)

        if selected_speaker:
            styles = selected_speaker.get("styles", [])
            style_names = [style.get("name", "") for style in styles]

            with col2:
                selected_style_name = st.selectbox("🎨 スタイル選択", style_names, index=0)

            speaker_id = voicevox.find_speaker_id(speakers, selected_speaker_name, selected_style_name)

            if st.button("PREVIEW", key="sample_btn"):
                progress_bar = st.progress(0)
                progress_bar.progress(30)
                sample_audio = voicevox.generate_sample_voice(speaker_id)
                if sample_audio:
                    st.session_state.sample_audio = sample_audio
                    progress_bar.progress(100)

            if st.session_state.sample_audio:
                st.audio(st.session_state.sample_audio, format="audio/wav")

            speed_options = {"0.7x": 0.7, "0.8x": 0.8, "0.9x": 0.9, "1.0x（標準）": 1.0, "1.1x": 1.1, "1.2x": 1.2, "1.3x": 1.3}
            selected_speed = st.selectbox("⚡ 話速", list(speed_options.keys()), index=3)
            speed = speed_options[selected_speed]

            pause_length = st.slider("⏸️ 間の長さ", min_value=0.0, max_value=2.0, value=1.0, step=0.1,
                                     help="句読点での間の長さ（0.0=間なし、1.0=標準、2.0=長い間）")

            # 生成される行数を表示
            voice_text = st.session_state.text_editor
            total_lines = len([line.strip() for line in voice_text.strip().split('\n') if line.strip()])
            st.info(f"📊 生成される音声行数: **{total_lines}行**")

            if st.button("GENERATE AUDIO", key="generate_btn"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                # 進捗コールバック関数
                def audio_progress_callback(current, total, message):
                    progress = int((current / total) * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"🎙️ {message}")

                status_text.text("音声生成を開始...")
                audio_data = voicevox.generate_voice_with_progress(
                    voice_text,
                    speaker_id,
                    speed,
                    pause_length,
                    progress_callback=audio_progress_callback
                )

                if audio_data:
                    st.session_state.generated_audio = audio_data
                    st.session_state.speaker_id = speaker_id
                    st.session_state.speed = speed
                    st.session_state.pause_length = pause_length
                    st.session_state.audio_text = voice_text  # 音声生成時のテキストを保存
                    progress_bar.progress(100)
                    status_text.text(f"✅ 全 {total_lines} 行の音声生成が完了しました")
                else:
                    status_text.text("❌ 音声生成に失敗しました")
                    st.error("音声生成に失敗しました。VOICEVOXが起動しているか確認してください。")

            if st.session_state.generated_audio:
                st.subheader("🎧 生成された音声")
                st.audio(st.session_state.generated_audio, format="audio/wav")

                st.download_button(
                    label="DOWNLOAD AUDIO",
                    data=st.session_state.generated_audio,
                    file_name=f"{final_filename}.wav",
                    mime="audio/wav",
                    key="download_audio"
                )

    else:
        st.error("⚠️ VOICEVOXに接続できません")
        st.warning("VOICEVOXアプリを起動してください: https://voicevox.hiroshiba.jp/")

    # セクション4: 動画生成（音声生成後に表示）
    if st.session_state.generated_audio:
        st.header("🎬 4. 動画生成")

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

        # SNSコンテンツ込みのテキストダウンロード
        full_text = formatted_main_text + "\n\n" + st.session_state.sns_content_editor
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
