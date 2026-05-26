# Coders War — Server Deploy Qo'llanmasi

**Arxitektura:** PostgreSQL + Django/Daphne + Nginx (Redis/Celery yo'q)

---

## Talablar

- Ubuntu 22.04+ server
- Docker 24+ va Docker Compose v2
- Git
- `rsync` (local mashinada — odatda o'rnatilgan bo'ladi)

---

## 1-qism: Serverga birinchi marta o'rnatish

### 1.1 — Serverga ulaning

```bash
ssh root@YOUR_SERVER_IP
```

### 1.2 — Docker o'rnating

```bash
curl -fsSL https://get.docker.com | sh
apt install git -y
```

### 1.3 — Loyihani klonlang

```bash
mkdir -p /srv/coderswar
cd /srv/coderswar
git clone https://github.com/YOUR_USERNAME/coderswar.git .
```

### 1.4 — `.env.production` to'ldiring

```bash
cd /srv/coderswar/backend
cp .env.production.example .env.production
nano .env.production
```

**Muhim qiymatlar:**

| Kalit | Qiymat |
|-------|--------|
| `DB_ENGINE` | `postgresql` ← **majburiy, o'zgartirmang** |
| `SECRET_KEY` | `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DB_PASSWORD` | Kuchli parol (masalan: `Cw@2025#Secure!`) |
| `ALLOWED_HOSTS` | `coderswar.uz,www.coderswar.uz,SERVER_IP` |
| `EMAIL_HOST_PASSWORD` | [Gmail App Password](https://myaccount.google.com/apppasswords) |
| `JUDGE0_API_KEY` | [RapidAPI](https://rapidapi.com/judge0-official/api/judge0-ce) dan |

### 1.5 — Birinchi deploy

```bash
cd /srv/coderswar/backend
bash deploy.sh --first-run
```

Bu buyruq:
1. Docker image build qiladi (~5 daqiqa)
2. DB + Web + Nginx konteynerlarini ishga tushiradi
3. Migratsiya, `collectstatic` bajaradi
4. Fixture'larni yuklaydi (45 mavzu, nishonlar, qurollar)
5. Superuser yaratishni so'raydi

### 1.6 — Frontend fayllarini yuklang

**LOCAL mashinangizda** (Windows/Mac/Linux):

```bash
# Repo papkasiga o'ting
cd coderswar

# Frontend ni serverga yuklang
bash sync-frontend.sh root@YOUR_SERVER_IP
```

---

## 2-qism: Yangilash (har safar o'zgartish kiritganda)

### Backend yangilash

Serverda:
```bash
cd /srv/coderswar/backend
bash deploy.sh
```

### Frontend yangilash

Local mashinada:
```bash
bash sync-frontend.sh root@YOUR_SERVER_IP
```

> **Tezlik:** Frontend uchun Docker rebuild shart emas —
> `rsync` faqat o'zgargan fayllarni yuboradi (5–30 sekund).

---

## 3-qism: SSL (HTTPS) o'rnatish

```bash
# Serverda
apt install certbot -y

docker compose -f /srv/coderswar/backend/docker-compose.yml stop nginx

certbot certonly --standalone \
  -d coderswar.uz \
  -d www.coderswar.uz \
  --email your@email.com \
  --agree-tos --non-interactive

# Sertifikatni nginx/ssl/ ga nusxalash
mkdir -p /srv/coderswar/backend/nginx/ssl
cp /etc/letsencrypt/live/coderswar.uz/fullchain.pem /srv/coderswar/backend/nginx/ssl/
cp /etc/letsencrypt/live/coderswar.uz/privkey.pem   /srv/coderswar/backend/nginx/ssl/

docker compose -f /srv/coderswar/backend/docker-compose.yml up -d nginx
```

**`nginx/nginx.conf` ni HTTPS uchun almashtiring:**

```nginx
upstream daphne { server web:8000; }

server {
    listen 80;
    server_name coderswar.uz www.coderswar.uz;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl http2;
    server_name coderswar.uz www.coderswar.uz;

    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    client_max_body_size 50M;
    root /app/frontend;
    index index.html;

    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    location /static/frontend/ { alias /app/frontend/static/; expires 30d; }
    location /static/          { alias /app/staticfiles/;      expires 30d; }
    location /media/           { alias /app/media/;            expires 7d;  }

    location /ws/ {
        proxy_pass http://daphne;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    location /api/ {
        proxy_pass http://daphne;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /admin/ {
        proxy_pass http://daphne;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
    }

    location ~* \.html$ { try_files $uri =404; expires -1; }
    location / { try_files $uri $uri/ $uri.html =404; }
}
```

---

## Foydali buyruqlar (serverda)

```bash
# Konteyner holati
docker compose -f /srv/coderswar/backend/docker-compose.yml ps

# Real-time loglar
docker compose -f /srv/coderswar/backend/docker-compose.yml logs -f web

# Django shell
docker compose -f /srv/coderswar/backend/docker-compose.yml exec web python manage.py shell

# Yangi superuser
docker compose -f /srv/coderswar/backend/docker-compose.yml exec web python manage.py createsuperuser

# Konteynerlarni to'xtatish
docker compose -f /srv/coderswar/backend/docker-compose.yml down
```

---

## Muammolar

| Muammo | Yechim |
|--------|--------|
| Nginx 502 | `docker compose logs web` — migration xatosini tekshiring |
| "relation does not exist" | `docker compose exec web python manage.py migrate` |
| Frontend yangilanmadi | `bash sync-frontend.sh root@IP` qayta ishga tushiring |
| Email ketmaydi | Gmail App Password to'g'riligini tekshiring (2FA yoqilgan bo'lishi kerak) |
| Judge0 ishlamaydi | `.env.production` dagi `JUDGE0_API_KEY` ni tekshiring |

---

## Arxitektura

| Konteyner | Texnologiya | Port |
|-----------|-------------|------|
| `coderswar_db` | PostgreSQL 15 | 5432 (ichki) |
| `coderswar_web` | Django 4.2 + Daphne ASGI | 8000 (ichki) |
| `coderswar_nginx` | Nginx 1.25 | 80 / 443 |

**Frontend:** `/srv/coderswar/frontend/` (Nginx to'g'ridan-to'g'ri serve qiladi)
**Async tasks:** Python threading (Redis/Celery kerak emas)
