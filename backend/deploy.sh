#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  Coders War — Backend Deploy Script
#  Ishlatish:
#    bash deploy.sh              → yangilash (git pull + rebuild)
#    bash deploy.sh --first-run  → birinchi marta (build + seed + superuser)
# ═══════════════════════════════════════════════════════════════
set -e

FIRST_RUN=false
[[ "$1" == "--first-run" ]] && FIRST_RUN=true

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      Coders War — Deploy Script          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Tekshiruvlar ─────────────────────────────────────────────────
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production fayli topilmadi!"
    echo "   cp .env.production.example .env.production"
    echo "   va kerakli qiymatlarni to'ldiring."
    exit 1
fi

command -v docker >/dev/null 2>&1 || { echo "❌ Docker o'rnatilmagan!"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "❌ Docker Compose o'rnatilmagan!"; exit 1; }

# ── Frontend papkasini tayyorlash ────────────────────────────────
FRONTEND_DIR="/srv/coderswar/frontend"
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "📁 Frontend papkasi yaratilmoqda: $FRONTEND_DIR"
    mkdir -p "$FRONTEND_DIR"
fi

# ── Birinchi ishga tushirish ──────────────────────────────────────
if [ "$FIRST_RUN" = true ]; then
    echo "🔧 Birinchi sozlash boshlandi..."

    echo "📦 Docker imagellar build qilinmoqda..."
    docker compose --env-file .env.production build --no-cache

    echo "🚀 Konteynerlar ishga tushirilmoqda..."
    docker compose --env-file .env.production up -d

    echo "⏳ Web server tayyor bo'lishini kutmoqda (30 sek)..."
    sleep 30

    echo "🌱 Fixture ma'lumotlari yuklanmoqda..."
    docker compose exec web python manage.py loaddata apps/courses/fixtures/initial_data.json
    docker compose exec web python manage.py loaddata apps/courses/fixtures/plans_and_tests.json
    docker compose exec web python manage.py loaddata apps/gamification/fixtures/badges.json
    docker compose exec web python manage.py loaddata apps/gamification/fixtures/equipment.json 2>/dev/null || true

    echo ""
    echo "👤 Superuser yarating:"
    docker compose exec web python manage.py createsuperuser

    echo ""
    echo "✅ Birinchi sozlash tugadi!"
    echo ""
    echo "⚠️  Frontend fayllarini yuklash uchun:"
    echo "   LOCAL mashinangizda:  bash sync-frontend.sh USER@SERVER_IP"

# ── Yangilash (normal deploy) ─────────────────────────────────────
else
    echo "⬇️  So'nggi o'zgarishlar yuklanmoqda..."
    git pull origin master 2>/dev/null || git pull origin main

    echo "🏗️  Yangi image build qilinmoqda..."
    docker compose --env-file .env.production build web

    echo "🔄 Web konteyner qayta ishga tushirilmoqda..."
    docker compose --env-file .env.production up -d --no-deps web

    echo "⏳ Tayyor bo'lishini kutmoqda..."
    sleep 8

    echo "✅ Backend yangilandi!"
fi

echo ""
echo "📊 Konteynerlar holati:"
docker compose ps

echo ""
echo "📋 Web server (oxirgi 15 qator):"
docker compose logs --tail=15 web
