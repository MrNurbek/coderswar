# Coders War Backend — tez buyruqlar

.PHONY: install migrate seed seed-content run worker ws test

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

seed:
	python manage.py loaddata apps/courses/fixtures/initial_data.json
	python manage.py loaddata apps/courses/fixtures/plans_and_tests.json
	python manage.py loaddata apps/gamification/fixtures/badges.json
	python manage.py loaddata apps/gamification/fixtures/equipment.json

seed-content:
	python manage.py loaddata apps/courses/fixtures/initial_data.json
	python manage.py loaddata apps/courses/fixtures/plans_and_tests.json

superuser:
	python manage.py createsuperuser

run:
	python manage.py runserver 0.0.0.0:8000

run-asgi:
	daphne -b 0.0.0.0 -p 8000 config.asgi:application

worker:
	celery -A config worker --loglevel=info

beat:
	celery -A config beat --loglevel=info

test:
	python manage.py test

collectstatic:
	python manage.py collectstatic --noinput

setup: install migrate seed superuser
	@echo "✅ Loyiha tayyor! 'make run' bilan ishga tushiring."

# ── Docker ──────────────────────────────────────────────────────

build:
	docker compose --env-file .env.production build

up:
	docker compose --env-file .env.production up -d

down:
	docker compose down

logs:
	docker compose logs -f web

ps:
	docker compose ps

shell:
	docker compose exec web python manage.py shell

dbshell:
	docker compose exec web python manage.py dbshell

dc-migrate:
	docker compose exec web python manage.py migrate

dc-seed:
	docker compose exec web python manage.py loaddata apps/courses/fixtures/initial_data.json
	docker compose exec web python manage.py loaddata apps/courses/fixtures/plans_and_tests.json
	docker compose exec web python manage.py loaddata apps/gamification/fixtures/badges.json
	docker compose exec web python manage.py loaddata apps/gamification/fixtures/equipment.json

dc-superuser:
	docker compose exec web python manage.py createsuperuser

deploy:
	bash deploy.sh

first-deploy:
	bash deploy.sh --first-run
