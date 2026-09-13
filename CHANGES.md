# CHANGES — Bitácora de cambios

Formato: fecha · resumen · referencias (overleaf-caso de uso si aplica).

---

## 2026-09-13 — CU-06 Catálogo / CU-07 Detalle de producto

- **Backend:** `GET /catalog/categories`; filtros por búsqueda, categoría y sucursal en
  `GET /catalog`; detalle con variantes (talla/color) e inventario. `min_price` e `in_stock`
  en la lectura de catálogo. `get` de catálogo con 404 propio.
- Fix `product_service`: validación de `Collection` (antes `Category`) y variantes requieren
  talla y color (evita NULL en columnas NOT NULL).
- **Tests:** 7 nuevas pruebas de catálogo (listado, detalle, 404, categorías, búsqueda,
  filtros por categoría y sucursal). Suites: 18 pruebas en total.
- **Frontend:** catálogo con imágenes, categoría, precio mínimo, estado de stock, buscador y
  filtro por categoría; vista `/catalog/:id` con selector de talla/color y "Agregar al carrito".
- **UML + tabla CU:** `docs/uml/ciclo1/CU-06/{sequence,communication}.puml`, `CU-07/…`.
- Referencias: overleaf CU-06, CU-07.

## 2026-09-13 — CU-01 Gestión de usuarios / CU-02 Roles y empleados

- **Backend:** `POST /users/{id}/employee` para vincular empleados a sucursal; `GET /users/roles`;
  validación de roles existentes al crear/editar; `GET /users` restringido a ADMIN.
- Emails demo migrados de `@fashionstore.test` (TLD reservado rechazado por email-validator) a
  `@fashionstore.dev` (seed, config, frontend, BD Neon actualizada).
- **Tests:** pytest configurado (`tests/`); 11 pruebas de autenticación, usuarios y roles.
- **Frontend:** panel `/admin` funcional (listado de usuarios, roles, creación de usuarios y
  vinculación de empleados); acceso "Admin" en navbar.
- **UML + tabla CU:** `docs/uml/ciclo1/CU-01/{sequence,communication}.puml`, `CU-02/…` y tablas.
- Referencias: overleaf CU-01, CU-02.

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

- Ciclo 1: CU-04, 12, 13, 14, 15, 17 (+ UML + tabla de CU).
- Despliegue a nubes (Render/Vercel/Firebase) cuando el dueño lo solicite.