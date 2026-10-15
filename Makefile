.PHONY: help install dev test lint migrate migrate-new docker-up docker-down docker-logs frontend-install frontend-dev frontend-build

PYTHON ?= python
MANAGE ?= backend/app/manage.py

help:
	@echo "FinanceFlow - common development tasks"
	@echo ""
	@echo "Backend:"
	@echo "  install            install backend dependencies in a venv"
	@echo "  dev                run backend dev server (uvicorn)"
	@echo "  test               run backend pytest suite"
	@echo "  lint               run flake8 over the backend"
	@echo "  migrate            apply alembic migrations"
	@echo "  migrate-new m=...  create a new alembic revision"
	@echo ""
	@echo "Frontend:"
	@echo "  frontend-install   install frontend dependencies"
	@echo "  frontend-dev        run the Vite dev server"
	@echo "  frontend-build     build the frontend for production"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up          build & start all services"
	@echo "  docker-down        stop & remove containers"
	@echo "  docker-logs        tail compose logs"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r backend/requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend

test:
	$(PYTHON) -m pytest backend/tests -q

lint:
	$(PYTHON) -m flake8 backend/app backend/tests

migrate:
	alembic -c backend/alembic.ini upgrade head

migrate-new:
	@test -n "$(m)" || (echo "Usage: make migrate-new m=\"message\"" && exit 1)
	alembic -c backend/alembic.ini revision --autogenerate -m "$(m)"

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
