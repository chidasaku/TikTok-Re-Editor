#!/bin/bash
echo "============================================"
echo "TikTok Re-Editor v3 インストール"
echo "============================================"
echo ""

cd "$(dirname "$0")"

# Homebrewの確認とインストール
if ! command -v brew &> /dev/null; then
    echo "Homebrewをインストールしています..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Pythonの確認とインストール
if ! command -v python3 &> /dev/null; then
    echo "Python3をインストールしています..."
    brew install python
fi

# FFmpegの確認とインストール
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpegをインストールしています..."
    brew install ffmpeg
fi

# 必要なパッケージのインストール
echo ""
echo "Pythonパッケージをインストールしています..."
pip3 install -r requirements.txt

# .envファイルの作成
if [ ! -f .env ]; then
    echo ""
    echo ".envファイルを作成しています..."
    cp .env.example .env
fi

echo ""
echo "============================================"
echo "インストール完了！"
echo "============================================"
echo ""
echo "次のステップ:"
echo "1. .envファイルにAPIキーを設定（任意）"
echo "2. 「start.command」をダブルクリックして起動"
echo ""
read -p "Enterキーで終了..."
