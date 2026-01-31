@echo off
chcp 65001 > nul
echo ============================================
echo TikTok Re-Editor v3 インストール
echo ============================================
echo.

cd /d "%~dp0"

REM Pythonの確認
python --version > nul 2>&1
if errorlevel 1 (
    echo [エラー] Pythonがインストールされていません
    echo https://www.python.org/downloads/ からダウンロードしてください
    echo インストール時に「Add Python to PATH」にチェックを入れてください
    pause
    exit /b 1
)

REM FFmpegの確認
ffmpeg -version > nul 2>&1
if errorlevel 1 (
    echo [警告] FFmpegがインストールされていません
    echo https://ffmpeg.org/download.html からダウンロードしてください
    echo.
)

REM 必要なパッケージのインストール
echo.
echo Pythonパッケージをインストールしています...
pip install -r requirements.txt

REM .envファイルの作成
if not exist .env (
    echo.
    echo .envファイルを作成しています...
    copy .env.example .env
)

echo.
echo ============================================
echo インストール完了！
echo ============================================
echo.
echo 次のステップ:
echo 1. VOICEVOXをインストール: https://voicevox.hiroshiba.jp/
echo 2. .envファイルにAPIキーを設定（任意）
echo 3. 「起動.bat」をダブルクリックして起動
echo.
pause
