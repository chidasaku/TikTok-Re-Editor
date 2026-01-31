#!/bin/bash
# ===========================================
# デプロイスクリプト（ローカルPCから実行）
# ===========================================

# 設定（ここを変更してください）
SERVER_IP="YOUR_SERVER_IP"
SERVER_USER="root"

echo "=========================================="
echo "  TikTok Re-Editor デプロイ"
echo "=========================================="

# 確認
read -p "サーバーIP [$SERVER_IP]: " input_ip
SERVER_IP=${input_ip:-$SERVER_IP}

echo ""
echo "デプロイ先: $SERVER_USER@$SERVER_IP"
echo ""

# ファイルをアップロード
echo "[1/4] ファイルをアップロード中..."
scp -r app.py requirements.txt packages.txt utils/ .streamlit/ .env.example \
    setup-conoha.sh tiktok-reeditor.service nginx-tiktok-reeditor.conf \
    $SERVER_USER@$SERVER_IP:/var/www/tiktok-reeditor/

# セットアップスクリプトを実行
echo "[2/4] 依存関係をインストール中..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
cd /var/www/tiktok-reeditor
chown -R appuser:appuser /var/www/tiktok-reeditor
su - appuser -c "cd /var/www/tiktok-reeditor && source venv/bin/activate && pip install -r requirements.txt"
EOF

# systemdサービスを設定
echo "[3/4] サービスを設定中..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
cp /var/www/tiktok-reeditor/tiktok-reeditor.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable tiktok-reeditor
systemctl restart tiktok-reeditor
EOF

# nginxを設定
echo "[4/4] Nginxを設定中..."
ssh $SERVER_USER@$SERVER_IP << EOF
cp /var/www/tiktok-reeditor/nginx-tiktok-reeditor.conf /etc/nginx/sites-available/tiktok-reeditor
ln -sf /etc/nginx/sites-available/tiktok-reeditor /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
EOF

echo ""
echo "=========================================="
echo "  デプロイ完了！"
echo "=========================================="
echo ""
echo "アクセスURL: http://$SERVER_IP"
echo ""
echo "HTTPSを有効にするには:"
echo "  ssh $SERVER_USER@$SERVER_IP"
echo "  certbot --nginx -d yourdomain.com"
echo ""
