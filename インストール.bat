@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ==========================================
echo   TikTok Re-Editor インストーラー
echo ==========================================
echo.

cd /d "%~dp0"

REM 1. Pythonのチェック
echo ------------------------------------------
echo [1/3] Pythonをチェック中...
echo ------------------------------------------

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Pythonがインストールされていません。
    echo.
    echo 以下のURLからPythonをダウンロードしてインストールしてください：
    echo https://www.python.org/downloads/
    echo.
    echo 【重要】インストール時に「Add Python to PATH」にチェックを入れてください
    echo.
    start https://www.python.org/downloads/
    echo Pythonをインストール後、このスクリプトを再度実行してください。
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ !PYTHON_VERSION! がインストールされています
)

echo.

REM 2. FFmpegのチェック
echo ------------------------------------------
echo [2/3] FFmpegをチェック中...
echo ------------------------------------------

ffmpeg -version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo FFmpegがインストールされていません。
    echo.

    REM FFmpegをダウンロード
    echo FFmpegをダウンロードしています...

    if not exist "ffmpeg" mkdir ffmpeg

    REM PowerShellでダウンロード
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'}"

    if exist "ffmpeg.zip" (
        echo 解凍しています...
        powershell -Command "& {Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'ffmpeg_temp' -Force}"

        REM 解凍したフォルダからbinをコピー
        for /d %%i in (ffmpeg_temp\ffmpeg-*) do (
            xcopy "%%i\bin\*" "ffmpeg\" /Y /Q
        )

        REM クリーンアップ
        del ffmpeg.zip
        rmdir /s /q ffmpeg_temp

        echo.
        echo ✅ FFmpegをダウンロードしました（ffmpegフォルダ内）

        REM 環境変数に追加（現在のセッションのみ）
        set "PATH=%cd%\ffmpeg;%PATH%"

        echo.
        echo 【重要】FFmpegを永続的に使えるようにするには：
        echo 1. 「%cd%\ffmpeg」をシステム環境変数のPATHに追加してください
        echo 2. または、ffmpegフォルダを C:\ffmpeg に移動し、C:\ffmpeg をPATHに追加してください
        echo.
    ) else (
        echo FFmpegのダウンロードに失敗しました。
        echo 手動でダウンロードしてください：
        echo https://github.com/BtbN/FFmpeg-Builds/releases
        echo.
    )
) else (
    echo ✅ FFmpegは既にインストールされています
)

echo.

REM 3. Pythonパッケージのインストール
echo ------------------------------------------
echo [3/3] 必要なパッケージをインストール中...
echo ------------------------------------------

pip install -r requirements.txt

echo.
echo ✅ パッケージをインストールしました

echo.
echo ==========================================
echo   インストール完了！
echo ==========================================
echo.
echo 【次のステップ】
echo.
echo 1. VOICEVOXをインストール（まだの場合）
echo    https://voicevox.hiroshiba.jp/
echo.
echo 2. VOICEVOXを起動
echo.
echo 3.「起動.bat」をダブルクリックしてアプリを起動
echo.
echo ==========================================
echo.

pause
