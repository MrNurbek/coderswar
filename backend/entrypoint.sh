#!/bin/bash
set -e

echo "⏳ PostgreSQL tayyor bo'lishini kutmoqda..."
until python -c "
import os, psycopg2
try:
    psycopg2.connect(
        dbname=os.environ.get('DB_NAME','coderswar'),
        user=os.environ.get('DB_USER','postgres'),
        password=os.environ.get('DB_PASSWORD',''),
        host=os.environ.get('DB_HOST','db'),
        port=os.environ.get('DB_PORT','5432'),
    )
    print('OK')
except:
    exit(1)
"; do
    echo "  PostgreSQL hali tayyor emas, 2 soniya kutilmoqda..."
    sleep 2
done
echo "✅ PostgreSQL tayyor!"

echo "🔄 Migratsiyalar amalga oshirilmoqda..."
python manage.py migrate --noinput

echo "📦 Statik fayllar yig'ilmoqda..."
python manage.py collectstatic --noinput

echo "🚀 Daphne (ASGI) ishga tushirilmoqda..."
exec daphne -b 0.0.0.0 -p 8000 config.asgi:application
