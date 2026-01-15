#!/bin/bash
cd "$(dirname "$0")"
echo "🎬 TikTok Re-Editor を起動しています..."
echo ""
echo "※ VOICEVOXが起動していることを確認してください"
echo ""
python3 -m streamlit run app.py &
sleep 3
open http://localhost:8501
wait
