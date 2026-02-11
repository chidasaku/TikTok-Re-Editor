@echo off
chcp 932 > nul
cd /d "%~dp0"

echo ======================================
echo   TikTok Re-Editor v3 を起動中...
echo ======================================
echo.
echo ※ VOICEVOXアプリを起動しておいてください
echo.

REM FFmpegのパスを追加（アプリフォルダ内）
if exist "ffmpeg\ffmpeg.exe" (
    set "PATH=%~dp0ffmpeg;%PATH%"
)

REM ローカルPythonを優先
if exist "python_embedded\python.exe" (
    echo Python: ローカル版を使用
    python_embedded\python.exe --version
    echo.
    python_embedded\python.exe -m streamlit run app.py --server.headless=false
) else (
    REM システムPythonにフォールバック
    python --version > nul 2>&1
    if %errorlevel% neq 0 (
        echo エラー: Pythonが見つかりません
        echo 「インストール.bat」を先に実行してください
        echo.
        pause
        exit /b 1
    )
    python --version
    echo.
    python -m streamlit run app.py --server.headless=false
)

REM エラーが発生した場合
if %errorlevel% neq 0 (
    echo.
    echo ======================================
    echo   エラーが発生しました
    echo ======================================
    echo.
    echo 以下を確認してください:
    echo 1. 「インストール.bat」を実行しましたか？
    echo 2. VOICEVOXは起動していますか？
    echo.
)

pause
