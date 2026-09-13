# FashionStore — Plataforma inteligente de tienda de ropa

Monorepo del sistema para la materia. Plataforma omnicanal (web, móvil y punto de venta)
para una tienda de ropa con **reservas con probador virtual**, **recomendaciones con IA**
(embeddings + pgvector) y **pagos con pasarela** (Mock en desarrollo; PagosNet en sandbox).

## Stack

| Capa       | Tecnología                                    |
|------------|-----------------------------------------------|
| Backend    | Python 3.11 · FastAPI · SQLAlchemy 2.0        |
| Base datos | PostgreSQL 16 + **pgvector** (Neon)           |
| Frontend   | Angular 18+ · Standalone · Signals · Tailwind |
| Mobile     | Flutter 3.22+ · Riverpod · Clean Architecture |
| IA         | sentence-transformers (all-MiniLM-L6-v2)      |
| AR         | MediaPipe Pose + transformación 2D (warp)     |
| Pagos      | **Mock Gateway** (dev) + **PagosNet** (sandbox) |

## Estructura

```
backend/   API REST (FastAPI) + IA + motor de pagos + tareas programadas
frontend/  Web app (Angular)
mobile/    App móvil (Flutter) con probador virtual AR
docs/      ADR y diagramas UML (secuencia + comunicación)
scripts/   Utilidades (generate-api.sh)
```

## Inicio rápido

```bash
cp .env.example .env            # ajustar credenciales
make docker-up                  # levanta BD PostgreSQL + pgvector
make db-migrate                 # aplica migraciones Alembic
make db-seed                    # datos iniciales (roles, empleados, cliente demo)
make dev                        # backend en http://localhost:8000/docs
make frontend                   # frontend en http://localhost:4200
```

## Documentación

- `RULES.md` — reglas de desarrollo del equipo.
- `CHANGES.md` — bitácora de cambios por fase/entrega.
- `TODO.md` — pendientes (infra, técnicos y backlog por ciclo).