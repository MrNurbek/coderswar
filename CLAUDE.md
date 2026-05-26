# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Coders War** — C# o'rganish uchun gamified platforma. Algori-Game metodologiyasi asosida qurilgan: RPG elementlari (character, level, clan, duel) + 45 ta mavzu × 3 daraja × 100 ball tizimi.

## Commands

```bash
# Setup
make install          # pip install -r requirements.txt
make migrate          # makemigrations + migrate
make seed             # fixture: initial_data + plans_and_tests + badges
make seed-content     # fixture: initial_data + plans_and_tests (badges excluded)
make setup            # install + migrate + seed + createsuperuser

# Development
make run              # runserver 0.0.0.0:8000  (WSGI)
make run-asgi         # daphne -b 0.0.0.0 -p 8000 config.asgi:application  (WebSocket uchun)
make worker           # celery -A config worker --loglevel=info
make beat             # celery -A config beat --loglevel=info

# Other
make test             # python manage.py test
make collectstatic    # --noinput
make superuser        # createsuperuser
```

Working directory: `backend/`

## Architecture

### Django Apps

| App | Purpose |
|-----|---------|
| `apps/users` | Custom User model, StudentProfile (RPG levels), TeacherProfile |
| `apps/courses` | Modules, Topics, 3-level content, tests, tasks, submissions |
| `apps/gamification` | Duel, Clan, Badge/UserBadge, XP tizimi |
| `apps/social` | Peer Review, Leaderboard, Notification |

### Scoring System (100 ball/mavzu)

4 ta mezon — jami 100 ball (bir mavzu uchun):

```
MO (15) = Motivatsion — hammasi avtomatik:
            +5   Login streak / mavzu bo'yicha faollik
            +3   Kontent o'qish: video+matn (har daraja +1, jami 3 daraja)
            +3   Topshiriqlarni muddatda bajarish
            +4   Bonus: duel, qo'shimcha mashqlar

KO (35) = Kognitiv — hammasi avtomatik:
            +10  Boshlang'ich daraja testi (10 savol, ≥7 to'g'ri o'tish)
            +10  O'rta daraja testi
            +10  Yuqori daraja testi
            +5   O'sish bonusi (barcha 3 daraja tugatilganda qo'shimcha)

FA (30) = Faoliyatli — ikki qism:
            Avtomatik (+20): Side Quest mashqlari
              Boshlang'ich 10 topshiriq → max 6 ball
              O'rta        10 topshiriq → max 7 ball
              Yuqori       10 topshiriq → max 7 ball
              (har bir passed exercise +1, jami cap 20)
            O'qituvchi (+10): 3 ta loyihani baholash (fa_project_score, 0–10)

RE (20) = Refleksiv-baholovchi — ikki qism:
            Avtomatik (+10): refleksiya jurnali yozilganda (bir marta)
            O'qituvchi (+10): peer-review sifatini baholash (re_peer_score, 0–10)
```

`TopicScore` dagi field'lar:
- `mo_score` (max 15) — avtomatik
- `ko_score` (max 35) — avtomatik (test o'tish + growth bonus)
- `fa_score` (max 20) — avtomatik (exercise submissions)
- `fa_project_score` (max 10) — o'qituvchi beradi
- `re_score` (max 10) — avtomatik (refleksiya jurnali)
- `re_peer_score` (max 10) — o'qituvchi beradi

`TopicScore.save()` avtomatik `total_score` hisoblaydi va `StudentProfile.recalculate()` chaqiradi.

### 3-Level Topic Structure

Har bir `Topic` (45 ta, 3 semestr × 15 mavzu, modul = semestr):
- **TopicLevelContent** — video_url + lecture_text + resources (3 ta, unique_together: topic+level)
- **LevelTest** — 10 savollik test (3 ta, unique_together: topic+level)
- **Task** — 10 exercise + 1 project har daraja (31 task/topic)

Level locking:
- `intermediate` testi: `beginner_test_passed = True` bo'lishi kerak
- `advanced` testi: `intermediate_test_passed = True` bo'lishi kerak
- Topic completed: barcha 3 test o'tilganda `TopicScore.is_completed = True`

### API Routes

```
/api/auth/                    — JWT login/register/OTP (apps.users.urls)
/api/auth/token/refresh/      — JWT refresh
/api/courses/modules/         — Module list
/api/courses/topics/          — Topic list/detail
/api/courses/topics/{id}/contents/         — TopicLevelContent (nested)
/api/courses/topics/{id}/tests/            — LevelTest + submit (nested)
/api/courses/topics/{id}/my-progress/      — StudentLevelProgress (GET/PATCH)
/api/courses/tasks/           — Task filterset: topic, level, task_category, task_type
/api/courses/submissions/     — Code submission → Judge0
/api/courses/scores/          — TopicScore
/api/courses/reflections/     — ReflectionJournal
/api/courses/diagnostic/      — Diagnostik test
/api/game/                    — Duel, Clan, Badge (apps.gamification.urls)
/api/social/                  — Leaderboard, Notification (apps.social.urls)
```

Nested routers: `drf-nested-routers` (`topics/{topic_pk}/contents/`, `topics/{topic_pk}/tests/`)

### Code Evaluation (Judge0)

`Submission` model → `JUDGE0_CSHARP_ID = 51` (C# language_id).  
Celery async task (`apps/courses/tasks.py`) kodni Judge0 ga yuboradi, natijani qaytarib `Submission.status` ni yangilaydi va `TopicScore.award_task_score()` chaqiradi.

### WebSocket (Django Channels)

`ws/duel/{room_id}/` — real-time duel. `config/asgi.py` da URL routing. Production uchun `make run-asgi` (daphne).

### User Levels (StudentProfile)

```python
LEVEL_THRESHOLDS = {
    'recruit':  (0, 300),
    'warden':   (301, 750),
    'knight':   (751, 1300),
    'hero':     (1301, 1900),
    'legend':   (1901, 2600),
    'lord':     (2601, 3350),
    'deity':    (3351, 4050),
    'titan':    (4051, 4500),
}
```

`StudentProfile.rating_score` — barcha `TopicScore.total_score` yig'indisi.

## Environment Variables (.env)

```
SECRET_KEY=...
DEBUG=True
DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
JUDGE0_URL=https://judge0-ce.p.rapidapi.com
JUDGE0_API_KEY=...
OPENAI_API_KEY=...
```

Config: `python-decouple` — `config('KEY', default=...)` pattern.

## Project Structure

```
coderswar/                     ← repo root
├── frontend/                  ← Barcha HTML sahifalar (Nginx tomonidan serve qilinadi)
│   ├── index.html             ← Bosh sahifa
│   ├── login.html / register.html / diagnostic.html
│   ├── dashboard.html         ← Student bosh paneli
│   ├── mainquest.html         ← Topic list + 3-level kontent
│   ├── sidequest.html         ← Code editor + 30 task
│   ├── profile.html / character.html / trajectory.html
│   ├── duel.html / clan.html / leaderboard.html / peer-review.html
│   ├── teacher-dashboard.html / admin-dashboard.html
│   └── static/
│       ├── css/               ← Global stillar
│       ├── js/                ← Global skriptlar
│       └── img/               ← Rasmlar, ikonkalar
├── backend/                   ← Django REST API
│   ├── config/                ← settings, urls, asgi, wsgi, celery
│   ├── apps/
│   │   ├── users/
│   │   ├── courses/
│   │   ├── gamification/
│   │   └── social/
│   ├── nginx/
│   │   ├── nginx.conf         ← /api/ → Daphne, / → frontend/
│   │   └── ssl/               ← SSL sertifikatlar (gitignore'd)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── entrypoint.sh
│   ├── deploy.sh
│   └── requirements.txt
└── CLAUDE.md
```

## Frontend (Static HTML)

`frontend/` papkasi Django tomonidan serve qilinmaydi — Nginx to'g'ridan-to'g'ri fayl sifatida beradi.

URL → fayl mapping:
- `https://coderswar.uz/` → `frontend/index.html`
- `https://coderswar.uz/mainquest.html` → `frontend/mainquest.html`
- `https://coderswar.uz/static/frontend/css/main.css` → `frontend/static/css/main.css`

Asosiy fayllar:
- `mainquest.html`: `lvProgress: {beginner:{vid,txt,adDone}, intermediate:{...}, advanced:{...}}`
- `sidequest.html`: `LEVEL_TASKS` — `beginner/intermediate/advanced` arrays + `*_project` keys; `switchLevel(level)` funksiyasi

## Key Model Relationships

```
Module → Topic (1:N)
Topic → TopicLevelContent (1:3, unique topic+level)
Topic → LevelTest (1:3, unique topic+level)
Topic → Task (1:31, 10 exercise + 1 project per level)
Topic → TopicScore (1:N per student)

User → StudentProfile (1:1)
User → TopicScore (1:N)
User → StudentLevelProgress (1:N)
User → Submission (1:N)
```

## Fixtures

`apps/courses/fixtures/`:
- `initial_data.json` — Modules (9) + Topics (45)
- `plans_and_tests.json` — TopicLevelContent + LevelTest + LevelTestQuestion (sample: topics 1-2)
- `apps/gamification/fixtures/badges.json` — Badge definitions
