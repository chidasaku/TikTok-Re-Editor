# CLAUDE.md - TikTok Re-Editor v3

## プロジェクト概要
TikTok動画を自動再編集するStreamlitアプリ。音声からテロップ付き縦動画を生成する。

## 技術スタック
- **言語**: Python 3.x
- **フレームワーク**: Streamlit
- **動画処理**: FFmpeg（外部バイナリ）
- **音声文字起こし**: Gladia API
- **テキスト整形**: Gemini API
- **音声合成**: VOICEVOX（オプション）
- **認証**: Google OAuth + Lark Base ユーザー管理
- **デプロイ**: Streamlit Cloud / ConoHa VPS

## ディレクトリ構成
```
app.py                  # メインアプリ（エントリーポイント）
auth/                   # Google OAuth認証 + Lark Baseユーザー管理
admin/                  # 管理者パネル
utils/
  transcription.py      # Gladia API 音声文字起こし
  text_formatter.py     # Gemini API テキスト整形
  video_generator_ffmpeg.py  # FFmpeg動画生成（縦書きテキスト処理）
  voicevox.py           # VOICEVOX音声合成
fonts/                  # CJKフォントバンドル
install.bat / .command  # Windows/Mac インストーラー
start.bat / .command    # Windows/Mac 起動スクリプト
```

## コーディング規約
- コメント・UIテキストは日本語
- ファイル名はASCII（日本語ファイル名は文字化けするため禁止）
- batファイルは `chcp 65001`（UTF-8）で統一
- Streamlit session_stateで状態管理

## 注意事項
- 縦書きテキスト描画: `utils/video_generator_ffmpeg.py` の回転文字処理（ー、=、+等）は慎重に変更すること
- フォント: `fonts/` ディレクトリのCJKフォントを使用。パスはOS判定で切り替え
- Windows対応: ファイルパス、エンコーディング（BOM付きUTF-8等）に注意

## テスト方法
```bash
# ローカル起動
streamlit run app.py

# 必要な環境変数（.envまたはStreamlit secrets）
# GLADIA_API_KEY, GEMINI_API_KEY
# GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET（認証用）
# LARK_APP_ID, LARK_APP_SECRET（ユーザー管理用）
```

## GitHub Actions
- `claude-fix` ラベル付きIssue → Claude Codeが自動修正してPR作成
- Issue/PRコメントで `@claude` メンション → Claude Codeが応答
