@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ======================================
echo   TikTok Re-Editor v3 を起動中...
echo ======================================
echo.
echo ※ VOICEVOXアプリを起動しておいてください
echo.

REM Pythonの確認
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo エラー: Pythonが見つかりません
    echo Pythonをインストールしてください: https://www.python.org/
    echo.
    pause
    exit /b 1
)

python --version
echo.

REM Streamlitを実行（ブラウザを自動で開く）
python -m streamlit run app.py --server.headless=false

REM エラーが発生した場合
if %errorlevel% neq 0 (
    echo.
    echo ======================================
    echo   エラーが発生しました
    echo ======================================
    echo.
    echo 以下を確認してください:
    echo 1. pip install -r requirements.txt を実行しましたか？
    echo 2. VOICEVOXは起動していますか？
    echo.
)

pause
