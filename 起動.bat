@echo off
cd /d "%~dp0"
echo 🎬 TikTok Re-Editor を起動しています...
echo.
echo ※ VOICEVOXが起動していることを確認してください
echo.
streamlit run app.py
pause
