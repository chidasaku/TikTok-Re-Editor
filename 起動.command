#!/bin/bash
cd "$(dirname "$0")"

echo "======================================"
echo "  TikTok Re-Editor v3 を起動中..."
echo "======================================"
echo ""
echo "※ VOICEVOXアプリを起動しておいてください"
echo ""

# Pythonのパスを確認
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "エラー: Pythonが見つかりません"
    echo "Pythonをインストールしてください: https://www.python.org/"
    echo ""
    echo "何かキーを押すと終了します..."
    read -n 1
    exit 1
fi

echo "Python: $($PYTHON_CMD --version)"
echo ""

# Streamlitを実行（ブラウザを自動で開く）
$PYTHON_CMD -m streamlit run app.py --server.headless=false

# エラーが発生した場合は待機
if [ $? -ne 0 ]; then
    echo ""
    echo "======================================"
    echo "  エラーが発生しました"
    echo "======================================"
    echo ""
    echo "以下を確認してください:"
    echo "1. pip install -r requirements.txt を実行しましたか？"
    echo "2. VOICEVOXは起動していますか？"
    echo ""
    echo "何かキーを押すと終了します..."
    read -n 1
fi
