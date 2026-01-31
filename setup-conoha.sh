#!/bin/bash
# ===========================================
# ConoHa VPS セットアップスクリプト
# TikTok Re-Editor v3
# ===========================================

set -e

echo "=========================================="
echo "  TikTok Re-Editor セットアップ開始"
echo "=========================================="

# 1. システム更新
echo "[1/7] システムを更新中..."
apt update && apt upgrade -y

# 2. 必要なパッケージをインストール
echo "[2/7] 必要なパッケージをインストール中..."
apt install -y python3 python3-pip python3-venv ffmpeg git nginx certbot python3-certbot-nginx ufw

# 3. ファイアウォール設定
echo "[3/7] ファイアウォールを設定中..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# 4. アプリ用ユーザー作成
echo "[4/7] アプリ用ユーザーを作成中..."
if ! id "appuser" &>/dev/null; then
    useradd -m -s /bin/bash appuser
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/appuser
fi

# 5. アプリディレクトリ作成
echo "[5/7] アプリディレクトリを作成中..."
mkdir -p /var/www/tiktok-reeditor
chown appuser:appuser /var/www/tiktok-reeditor

echo "[6/7] Python仮想環境を準備中..."
su - appuser << 'EOF'
cd /var/www/tiktok-reeditor
python3 -m venv venv
EOF

echo "[7/7] セットアップ完了！"
echo ""
echo "=========================================="
echo "  次のステップ"
echo "=========================================="
echo ""
echo "1. アプリファイルをアップロード:"
echo "   scp -r /path/to/TikTok-Re-Editor-FFmpeg-v3-Audio-Upload/* root@YOUR_IP:/var/www/tiktok-reeditor/"
echo ""
echo "2. 依存関係をインストール:"
echo "   su - appuser"
echo "   cd /var/www/tiktok-reeditor"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "3. systemdサービスを設定:"
echo "   sudo cp tiktok-reeditor.service /etc/systemd/system/"
echo "   sudo systemctl enable tiktok-reeditor"
echo "   sudo systemctl start tiktok-reeditor"
echo ""
