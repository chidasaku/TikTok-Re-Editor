@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo   TikTok Re-Editor v3 セットアップ
echo ============================================
echo.

REM ============================================
REM 1. Python Embedded のダウンロードとセットアップ
REM ============================================
if exist "python_embedded\python.exe" (
    echo [OK] Python Embedded は既にセットアップ済みです
) else (
    echo [1/3] Python をダウンロードしています...
    echo       （少々お待ちください）
    echo.

    mkdir python_embedded 2>nul

    REM Python 3.11.9 Embeddable をダウンロード
    powershell -ExecutionPolicy Bypass -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python_embedded\python.zip'}"

    if not exist "python_embedded\python.zip" (
        echo [エラー] Python のダウンロードに失敗しました
        echo インターネット接続を確認してください
        pause
        exit /b 1
    )

    echo       解凍しています...
    powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path 'python_embedded\python.zip' -DestinationPath 'python_embedded' -Force"
    del "python_embedded\python.zip"

    REM pip を有効化（python311._pth を編集）
    powershell -ExecutionPolicy Bypass -Command "(Get-Content 'python_embedded\python311._pth') -replace '#import site','import site' | Set-Content 'python_embedded\python311._pth'"

    REM get-pip.py をダウンロードして実行
    echo       pip をインストールしています...
    powershell -ExecutionPolicy Bypass -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python_embedded\get-pip.py'}"
    python_embedded\python.exe python_embedded\get-pip.py --no-warn-script-location
    del "python_embedded\get-pip.py"

    echo [OK] Python のセットアップが完了しました
    echo.
)

REM ============================================
REM 2. FFmpeg のダウンロードとセットアップ
REM ============================================
if exist "ffmpeg\ffmpeg.exe" (
    echo [OK] FFmpeg は既にセットアップ済みです
) else (
    echo [2/3] FFmpeg をダウンロードしています...
    echo       （ファイルサイズが大きいため、数分かかる場合があります）
    echo.

    mkdir ffmpeg 2>nul

    REM FFmpeg をダウンロード
    powershell -ExecutionPolicy Bypass -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg\ffmpeg.zip'}"

    if not exist "ffmpeg\ffmpeg.zip" (
        echo [エラー] FFmpeg のダウンロードに失敗しました
        echo インターネット接続を確認してください
        pause
        exit /b 1
    )

    echo       解凍しています...
    powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path 'ffmpeg\ffmpeg.zip' -DestinationPath 'ffmpeg\temp' -Force"

    REM ffmpeg.exe, ffprobe.exe をコピー
    for /d %%D in (ffmpeg\temp\ffmpeg-*) do (
        copy "%%D\bin\ffmpeg.exe" "ffmpeg\ffmpeg.exe" >nul
        copy "%%D\bin\ffprobe.exe" "ffmpeg\ffprobe.exe" >nul
    )

    REM 一時ファイルを削除
    rmdir /s /q "ffmpeg\temp" 2>nul
    del "ffmpeg\ffmpeg.zip" 2>nul

    echo [OK] FFmpeg のセットアップが完了しました
    echo.
)

REM ============================================
REM 3. Python パッケージのインストール
REM ============================================
echo [3/3] 必要なパッケージをインストールしています...
echo       （少々お待ちください）
echo.
python_embedded\python.exe -m pip install -r requirements.txt --no-warn-script-location

echo.
echo [OK] パッケージのインストールが完了しました
echo.

REM ============================================
REM 完了
REM ============================================
echo.
echo ============================================
echo   セットアップ完了！
echo ============================================
echo.
echo   次のステップ:
echo   「起動.bat」をダブルクリックして起動
echo.
echo ============================================
echo.
pause
