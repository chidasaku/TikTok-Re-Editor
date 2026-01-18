#!/bin/bash

# TikTok Re-Editor インストールスクリプト (Mac用)
# ダブルクリックで実行してください

cd "$(dirname "$0")"

echo "=========================================="
echo "  TikTok Re-Editor インストーラー"
echo "=========================================="
echo ""

# 色の定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Homebrewのチェック・インストール
echo "----------------------------------------"
echo "[1/4] Homebrewをチェック中..."
echo "----------------------------------------"

if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}Homebrewがインストールされていません。インストールします...${NC}"
    echo "（パスワードを求められたら、Macのログインパスワードを入力してください）"
    echo ""
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # M1/M2 Macの場合、パスを設定
    if [[ $(uname -m) == 'arm64' ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi

    echo -e "${GREEN}✅ Homebrewをインストールしました${NC}"
else
    echo -e "${GREEN}✅ Homebrewは既にインストールされています${NC}"
fi

echo ""

# 2. Pythonのチェック・インストール
echo "----------------------------------------"
echo "[2/4] Pythonをチェック中..."
echo "----------------------------------------"

if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Pythonがインストールされていません。インストールします...${NC}"
    brew install python
    echo -e "${GREEN}✅ Pythonをインストールしました${NC}"
else
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅ $PYTHON_VERSION がインストールされています${NC}"
fi

echo ""

# 3. FFmpegのチェック・インストール
echo "----------------------------------------"
echo "[3/4] FFmpegをチェック中..."
echo "----------------------------------------"

if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}FFmpegがインストールされていません。インストールします...${NC}"
    brew install ffmpeg
    echo -e "${GREEN}✅ FFmpegをインストールしました${NC}"
else
    echo -e "${GREEN}✅ FFmpegは既にインストールされています${NC}"
fi

echo ""

# 4. Pythonパッケージのインストール
echo "----------------------------------------"
echo "[4/4] 必要なパッケージをインストール中..."
echo "----------------------------------------"

pip3 install -r requirements.txt

echo -e "${GREEN}✅ パッケージをインストールしました${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}  インストール完了！${NC}"
echo "=========================================="
echo ""
echo "【次のステップ】"
echo ""
echo "1. VOICEVOXをインストール（まだの場合）"
echo "   https://voicevox.hiroshiba.jp/"
echo ""
echo "2. VOICEVOXを起動"
echo ""
echo "3.「起動.command」をダブルクリックしてアプリを起動"
echo ""
echo "=========================================="
echo ""

read -p "Enterキーを押して終了..."
