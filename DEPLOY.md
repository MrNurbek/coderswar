# Coders War — Server Deployment Guide

## Talablar

- Ubuntu 20.04+ / Debian 11+ server
- Docker 24+ va Docker Compose v2
- Git
- Domain: `coderswar.uz` → server IP ga DNS yo'naltirilgan

---

## 1. Serverga ulanish va tayyorgarlik

```bash
# SSH bilan ulanish
ssh root@YOUR_SERVER_IP

# Docker o'rnatish (agar yo'q bo'lsa)
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Git o'rnatish
apt install git -y
```

---

## 2. Loyihani serverga yuklash

```bash
# /var/www papkasiga o'tish
cd /var/www

# Loyihani klonlash
git clone https://github.com/YOUR_USERNAME/coderswar.git
cd coderswar
```

---

## 3. `.env.production` faylini to'ldirish

```bash
cd backend
cp .env.production.example .env.production
nano .env.production
```

**To'ldiriladigan qiymatlar:**

```bash
# 1. SECRET_KEY — yangi kalit yaratish:
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
# Chiqgan natijani SECRET_KEY= ga qo'ying

# 2. DB_PASSWORD — kuchli parol tanlang (masalan):
# DB_PASSWORD=Cw@2025#SecurePass!

# 3. ALLOWED_HOSTS
# ALLOWED_HOSTS=coderswar.uz,www.coderswar.uz,YOUR_SERVER_IP

# 4. EMAIL — Gmail App Password:
# https://myaccount.google.com/apppasswords (2FA yoqilgan bo'lishi kerak)

# 5. JUDGE0_API_KEY — RapidAPI dan:
# https://rapidapi.com/judge0-official/api/judge0-ce

# 6. OPENAI_API_KEY — ixtiyoriy (AI ko'mak uchun)
```

**Tayyor `.env.production` ko'rinishi:**
```
SECRET_KEY=your_generated_50_char_secret_key_here
DEBUG=False
ALLOWED_HOSTS=coderswar.uz,www.coderswar.uz,YOUR_SERVER_IP

DB_NAME=coderswar
DB_USER=coderswar_user
DB_PASSWORD=YourStrongPassword123!
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0

CORS_ALLOWED_ORIGINS=https://coderswar.uz,https://www.coderswar.uz

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=yourbot@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx

JUDGE0_URL=https://judge0-ce.p.rapidapi.com
JUDGE0_API_KEY=your_rapidapi_key

OPENAI_API_KEY=sk-...
```

---

## 4. Birinchi marta ishga tushirish

```bash
# backend/ papkasida turib:
cd /var/www/coderswar/backend

# Build + ishga tushirish + fixture + superuser
bash deploy.sh --first-run
```

Bu buyruq:
1. Docker imagellarni build qiladi (5-10 daqiqa)
2. Barcha 6 konteynerni ishga tushiradi
3. Migratsiyalar avtomatik bajariladi (entrypoint.sh orqali)
4. Fixture'larni yuklaydi (45 mavzu, 9 modul, nishonlar, 24 qurol)
5. Superuser yaratishni so'raydi

---

## 5. Konteyner holatini tekshirish

```bash
docker compose ps
```

**Barcha konteynerlar `Up` bo'lishi kerak:**
```
NAME                 STATUS
coderswar_db         Up (healthy)
coderswar_redis      Up (healthy)
coderswar_web        Up
coderswar_celery     Up
coderswar_beat       Up
coderswar_nginx      Up
```

**Agar muammo bo'lsa — loglarni ko'rish:**
```bash
docker compose logs web      # Django/Daphne loglari
docker compose logs nginx    # Nginx loglari
docker compose logs celery   # Celery worker loglari
docker compose logs db       # PostgreSQL loglari
```

---

## 6. Saytni tekshirish

Brauzerda:
```
http://YOUR_SERVER_IP         → Bosh sahifa
http://YOUR_SERVER_IP/admin/  → Django admin (superuser bilan kiring)
http://YOUR_SERVER_IP/api/    → API root
```

---

## 7. SSL sertifikat (HTTPS) — Let's Encrypt

> **Avval HTTP ishlashiga ishonch hosil qiling!**

```bash
# Certbot o'rnatish
apt install certbot -y

# Nginx vaqtincha to'xtatish
docker compose stop nginx

# Sertifikat olish
certbot certonly --standalone \
  -d coderswar.uz \
  -d www.coderswar.uz \
  --email your@email.com \
  --agree-tos \
  --non-interactive

# Sertifikatlarni nginx/ssl/ papkasiga nusxalash
cp /etc/letsencrypt/live/coderswar.uz/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/coderswar.uz/privkey.pem nginx/ssl/

# nginx.conf da HTTPS ni yoqish (quyidagi bo'limni o'qing)
# ...

# Nginx qayta ishga tushirish
docker compose up -d nginx
```

### HTTPS uchun `nginx/nginx.conf` yangilash

`nginx/nginx.conf` faylini quyidagicha almashtiring:

```nginx
upstream daphne {
    server web:8000;
}

# HTTP → HTTPS yo'naltirish
server {
    listen 80;
    server_name coderswar.uz www.coderswar.uz;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name coderswar.uz www.coderswar.uz;

    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;
    keepalive_timeout 65;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000" always;

    root /app/frontend;
    index index.html;

    location /static/frontend/ {
        alias /app/frontend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
    }

    location /ws/ {
        proxy_pass http://daphne;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 86400;
    }

    location /api/ {
        proxy_pass http://daphne;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /admin/ {
        proxy_pass http://daphne;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }

    location ~* \.html$ {
        try_files $uri =404;
        expires -1;
        add_header Cache-Control "no-store, no-cache";
    }

    location / {
        try_files $uri $uri/ $uri.html =404;
    }
}
```

**HTTPS ga o'tgandan keyin `.env.production` ni yangilang:**
```
CORS_ALLOWED_ORIGINS=https://coderswar.uz,https://www.coderswar.uz
```

Va konteynerlarni qayta ishga tushiring:
```bash
docker compose --env-file .env.production up -d
```

---

## 8. Sertifikatni avtomatik yangilash (cron)

```bash
# Crontab ga qo'shish
crontab -e

# Quyidagi qatorni qo'shing (har 3 oyda bir yangilanadi):
0 3 * * 1 certbot renew --quiet && \
  cp /etc/letsencrypt/live/coderswar.uz/fullchain.pem /var/www/coderswar/backend/nginx/ssl/ && \
  cp /etc/letsencrypt/live/coderswar.uz/privkey.pem /var/www/coderswar/backend/nginx/ssl/ && \
  docker compose -f /var/www/coderswar/backend/docker-compose.yml exec nginx nginx -s reload
```

---

## 9. Yangilanish (update deploy)

Kodni yangilaganingizdan so'ng:

```bash
cd /var/www/coderswar/backend
bash deploy.sh
```

Bu buyruq:
1. `git pull origin main`
2. Yangi Docker image build qiladi
3. Faqat `web`, `celery`, `beat` konteynerlarini qayta ishga tushiradi (DB va nginx ta'sirlanmaydi)

---

## 10. Foydali buyruqlar

```bash
# Barcha loglarni kuzatish (real-time)
docker compose logs -f

# Faqat web server loglari
docker compose logs -f web

# Django shell (ma'lumotlar bilan ishlash)
docker compose exec web python manage.py shell

# Database shell
docker compose exec web python manage.py dbshell

# Yangi superuser yaratish
docker compose exec web python manage.py createsuperuser

# Fixture qayta yuklash (allaqachon bor ma'lumotlar o'zgarmaydi)
make dc-seed

# Konteynerlarni to'xtatish
docker compose down

# To'liq tozalash (ma'lumotlar o'chadi!)
docker compose down -v
```

---

## 11. Muammo va yechimlar

### Nginx 502 Bad Gateway
```bash
# Web server ishlayaptimi?
docker compose logs web
# Ko'pincha entrypoint.sh da migration xatosi bo'ladi
```

### "relation does not exist" xatosi
```bash
# Migratsiya bajarilmagan
docker compose exec web python manage.py migrate
```

### Email jo'natilmaydi
```bash
# Gmail App Password to'g'riligini tekshiring
# 2FA yoqilmagan bo'lsa App Password yaratib bo'lmaydi
# https://myaccount.google.com/apppasswords
```

### Judge0 ishlamaydi
```bash
# RapidAPI API key tekshiring
# Bepul plan: 50 so'rov/kun — test uchun yetarli
# Pullik plan kerak bo'lsa: https://rapidapi.com/judge0-official/api/judge0-ce
```

### WebSocket ulanmaydi
```bash
# Nginx /ws/ location to'g'ri sozlanganini tekshiring
# Daphne ASGI server ishlab turganini tekshiring
docker compose logs web | grep daphne
```

---

## Texnik ma'lumotlar

| Komponent | Port | Texnologiya |
|-----------|------|-------------|
| Web server | 8000 (ichki) | Django 4.2 + Daphne ASGI |
| Database | 5432 (ichki) | PostgreSQL 15 |
| Cache/Queue | 6379 (ichki) | Redis 7 |
| Async tasks | — | Celery 5 |
| Proxy | 80/443 | Nginx 1.25 |
| Frontend | — | Static HTML/CSS/JS |
