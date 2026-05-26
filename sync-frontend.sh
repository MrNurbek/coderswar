#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  Coders War — Frontend Sync Script
#  LOCAL mashinadan serverga frontend fayllarini yuklaydi.
#
#  Ishlatish:
#    bash sync-frontend.sh user@SERVER_IP
#    bash sync-frontend.sh root@203.0.113.10
#
#  Birinchi ishlatishdan oldin SSH kalitingiz serverda bo'lishi kerak:
#    ssh-copy-id user@SERVER_IP
# ═══════════════════════════════════════════════════════════════

SERVER="${1}"

if [ -z "$SERVER" ]; then
    echo "❌ Server manzili ko'rsatilmadi!"
    echo "   Ishlatish: bash sync-frontend.sh user@SERVER_IP"
    exit 1
fi

REMOTE_DIR="/srv/coderswar/frontend"
LOCAL_DIR="./frontend/"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║    Coders War — Frontend Sync            ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Manba  : $LOCAL_DIR"
echo "  Server : $SERVER:$REMOTE_DIR"
echo ""

# Remote papkani yaratish (agar yo'q bo'lsa)
ssh "$SERVER" "mkdir -p $REMOTE_DIR"

# Rsync: faqat o'zgargan fayllarni yuboradi
rsync -avz --delete \
    --exclude='.DS_Store' \
    --exclude='*.pyc' \
    --exclude='.git' \
    "$LOCAL_DIR" \
    "$SERVER:$REMOTE_DIR"

echo ""
echo "✅ Frontend muvaffaqiyatli yuklandi!"
echo "   Nginx avtomatik yangi fayllarni ko'radi — rebuild shart emas."
echo ""
