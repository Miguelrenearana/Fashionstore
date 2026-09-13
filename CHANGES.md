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

## Pendiente de registrar

- Backend base (FastAPI + SQLAlchemy + core).
- Modelos/DDL (22+1 tablas, pgvector).
- Ciclo 1: implementación por caso de uso (CU-01 → CU-17) + UML + tabla de CU.