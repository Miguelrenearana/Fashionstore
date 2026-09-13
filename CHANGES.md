# CHANGES — Bitácora de cambios

Formato: fecha · resumen · referencias (overleaf-caso de uso si aplica).

---

## 2026-09-13 — Monorepo (línea base)

- Se vació el repositorio para reestructurar como monorepo (`0d67b1e`).
- Estructura monorepo creada: `backend/`, `frontend/`, `mobile/`, `docs/`, `scripts/`.
- Documentación de trabajo: `RULES.md`, `CHANGES.md`, `TODO.md`.
- Arquitectura de pagos: **Mock Gateway** para desarrollo + **PagosNet** (Red Enlace) como adapter
  de sandbox real (sin Libélula).
- Decisiones registradas en `docs/adr/001-mock-payment-gateway.md`.
- Commit inicial `fe72512` (156 archivos).

## 2026-09-13 — Verificación local + conexión a Neon

- Backend verificado: `import app.main`, 33 endpoints en OpenAPI, `/health` 200.
- Ruff limpio (F/E/W/UP/B); se reemplazaron `Depends()` en defaults por `Annotated`.
- Se pinó `bcrypt==4.0.1` (compatibilidad passlib 1.7.4, límite de 72 bytes).
- Corregido `Recommendation.suggested_variant` (FK ambigua) y joins cargados por
  atributos de clase (SQLAlchemy 2). Seed idempotente (Supplier sin FK a usuario).
- **BD Neon:**
  - Conexión directa configurada en `backend/.env` (`DATABASE_URL` + `?sslmode=require`).
  - Esquema recreado limpio vía `alembic upgrade head` (38 tablas, extensión `vector` 0.8.6,
    índice ivfflat `ix_product_embeddings_vector`).
  - Seed cargado (usuarios demo + catálogo).
  - Smoke test OK: login admin/client, catálogo, `/payments/config` (mock).

## Pendiente de registrar

- Ciclo 1: implementación por caso de uso (CU-01 → CU-17) + UML + tabla de CU.
- Despliegue a nubes (Render/Vercel/Firebase) cuando el dueño lo solicite.