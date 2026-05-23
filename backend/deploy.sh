#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  Coders War — Production Deploy Script
#  Ishlatish: bash deploy.sh [--first-run]
# ═══════════════════════════════════════════════════════════════
set -e

FIRST_RUN=false
if [[ "$1" == "--first-run" ]]; then
    FIRST_RUN=true
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║      Coders War — Deploy Script          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Tekshiruvlar ─────────────────────────────────────────────
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production fayli topilmadi!"
    echo "   cp .env.production.example .env.production"
    echo "   va kerakli qiymatlarni to'ldiring."
    exit 1
fi

if [ ! -f "nginx/ssl/fullchain.pem" ] || [ ! -f "nginx/ssl/privkey.pem" ]; then
    echo "⚠️  SSL sertifikat topilmadi (nginx/ssl/)"
    echo "   HTTP rejimida ishlamoqda (nginx.conf da 443 ni o'chiring)"
fi

# ── Birinchi ishga tushirish ──────────────────────────────────
if [ "$FIRST_RUN" = true ]; then
    echo "🔧 Birinchi sozlash..."

    # Docker + Docker Compose tekshirish
    command -v docker >/dev/null 2>&1 || { echo "❌ Docker o'rnatilmagan!"; exit 1; }
    command -v docker compose >/dev/null 2>&1 || { echo "❌ Docker Compose o'rnatilmagan!"; exit 1; }

    echo "📦 Imagellar build qilinmoqda (--no-cache)..."
    docker compose --env-file .env.production build --no-cache

    echo "🚀 Konteynerlar ishga tushirilmoqda..."
    docker compose --env-file .env.production up -d

    echo "⏳ Web server tayyor bo'lishini kutmoqda..."
    sleep 10

    echo "🌱 Fixture ma'lumotlari yuklanmoqda..."
    docker compose exec web python manage.py loaddata apps/courses/fixtures/initial_data.json
    docker compose exec web python manage.py loaddata apps/courses/fixtures/plans_and_tests.json
    docker compose exec web python manage.py loaddata apps/gamification/fixtures/badges.json
    docker compose exec web python manage.py loaddata apps/gamification/fixtures/equipment.json

    echo ""
    echo "👤 Superuser yarating:"
    docker compose exec web python manage.py createsuperuser

    echo ""
    echo "✅ Birinchi sozlash tugadi!"

# ── Yangilash (normal deploy) ─────────────────────────────────
else
    echo "⬇️  So'nggi o'zgarishlar yuklanmoqda..."
    git pull origin master

    echo "🏗️  Yangi image build qilinmoqda..."
    docker compose --env-file .env.production build

    echo "🔄 Konteynerlar qayta ishga tushirilmoqda..."
    docker compose --env-file .env.production up -d --no-deps web celery beat

    echo "⏳ Web server tayyor bo'lishini kutmoqda..."
    sleep 5

    echo "✅ Deploy muvaffaqiyatli yakunlandi!"
fi

echo ""
echo "📊 Konteyner holati:"
docker compose ps

echo ""
echo "📋 Web server loglari (oxirgi 20 qator):"
docker compose logs --tail=20 web
