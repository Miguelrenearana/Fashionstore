.PHONY: help docker-up docker-down dev db-migrate db-migrate-make db-seed frontend test lint format

help:
	@echo "FashionStore targets:"
	@echo "  docker-up / docker-down  Iniciar/detener BD (PostgreSQL + pgvector)"
	@echo "  dev                      Levantar backend (uvicorn, recarga)"
	@echo "  db-migrate               Aplicar migraciones Alembic"
	@echo "  db-migrate-make          Generar nueva migración alembic (MESSAGE=...) "
	@echo "  db-seed                  Poblar datos iniciales"
	@echo "  frontend                 Levantar frontend Angular"
	@echo "  lint / format            Ruff (bloqueante) + isort + black"
	@echo "  test                     Ejecutar tests backend"

docker-up:
	docker compose up -d db

docker-down:
	docker compose down

dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db-migrate:
	cd backend && alembic upgrade head

db-migrate-make:
	cd backend && alembic revision --autogenerate -m "$(MESSAGE)"

db-seed:
	cd backend && python -m scripts.seed

frontend:
	cd frontend && npm run start

lint:
	cd backend && ruff check app scripts && isort --check-only app scripts

format:
	cd backend && isort app scripts && black app scripts

test:
	cd backend && pytest -q