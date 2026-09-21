# TODO — Pendientes del proyecto

Formato:
- 🔴 infraestructura/credenciales (bloquea deploy, no el desarrollo local)
- 🟡 técnicos/calidad
- 🟢 backlog por ciclo

> **Ciclo 3 completado** — 13 CUs implementados y testeados. Ver `PLAN_CICLO_3.md`.

---

## 🔴 Infraestructura (resuelto)

- [x] **Neon**: proyecto creado y conectado → `backend/.env` con `DATABASE_URL` (directa,
  `sslmode=require`). Esquema aplicado con `alembic upgrade head` (38 tablas + `vector` 0.8.6
  + índice ivfflat) y seed cargado. **El backend corre en localhost apuntando a esta BD.**
- [x] **Render**: backend desplegado desde `render.yaml` (Docker) con health check `/health`.
- [x] **Vercel**: frontend importado con rewrites SPA de `vercel.json`.
- [x] **GitHub**: repo subido y sincronizado (origin/main).
- [ ] **Firebase**: **no requerido** (se omite). FCM preferido, pero sin proyecto Firebase/`google-services.json` (no se publica en Play Store) no se integra el push real (Fase 8: OMITIDO).
- [ ] **PagosNet (sandbox)**: **no requerido** (se usa gateway QR estático mock; se habilita solo si lo pide el dueño).
- [x] **Fase 8 (Integración + Deploy)** completada 21/09/2026: deep link `fashionstore://fitting/:variantId` (intent-filter Android + enlace web→app en el landing), endpoint `GET /api/v1/catalog/:id/ar-config` (nuevo, consumido por `ArFittingScreen`), Angular PWA (`ng add @angular/pwa`, manifest con paleta, `ngsw.json`), CI/CD `.github/workflows/ci.yml` (backend ruff+pytest con Postgres pgvector, frontend build, mobile analyze+test). Play Store cancelado (solo APK side-loading, decisión del dueño). Commit + push a GitHub hecho 21/09/2026 (`f2074f5`) → **redeploy Vercel** (pendiente de confirmar).

## 🟡 Técnicos (pendientes reales)

- [x] Generar **migración Alembic inicial** (todas las tablas) + `scripts/init_extensions.sql`.
- [x] **AR móvil mejorado 21/09/2026**: los placeholders del probador se sustituyeron por **prendas PNG transparentes reales** en `mobile/assets/images/garments/` (camiseta, playera, hoodie, vestido, chaqueta, blusa — generadas por script PIL). `GarmentOverlayPainter` ahora hace **anclaje automático** al cuadrilátero hombros→caderas del `PoseService` (con `ui.Image` y `canvas` warp), `ArFittingScreen` incluye selector de prendas (chips). Analyze + 8 tests en verde, `flutter build apk --release` regenerado ✓ (APK 21/09/2026 16:22). Sin ajuste manual (decisión del dueño: solo anclaje automático).
- [x] **Email real — HECHO 21/09/2026 (Gmail SMTP)**: `notification_service.notify()` envía email real con `smtplib` (STARTTLS 587) cuando `settings.smtp_password` existe; `reservation_expiry` e `inventory_sync` pasan por él. **Pendiente del dueño:** App Password de Gmail de `sonclargod@gmail.com` → `SMTP_USER`/`SMTP_PASSWORD`/`MAIL_FROM` en `backend/.env` y vars de Render (`render.yaml` ya declara `SMTP_HOST/PORT/USER/PASSWORD/MAIL_FROM` con `sync:false`).
- [x] **CU-03 end-to-end — HECHO 21/09/2026**: UI de notificaciones en **web** (`NotificationsComponent` campana + badge en navbar, página `/notifications` con `GET/PATCH`) **y móvil** (`notifications_screen.dart` conectado a `GET /notifications` + `PATCH /:id/read` + marcar todas). Con la App Password configurada el token de reset llega por email real.
- [ ] **Prueba manual de la web** en navegador (PC): registrar/perfil, carrito + compra, POS + factura, catálogo/admin, reservas.
- [x] **App móvil (CU-19):** **APK Android compilado** (`mobile/build/app/outputs/flutter-apk/app-release.apk`, 94.4 MB, 21/09/2026) con `flutter build apk --release` (se regeneró la carpeta `android/` que faltaba). Siendo directivas del dueño, se quitaron el catálogo público, carrito, checkout, perfil y reservas de la **web** (movidos a la app Flutter); la web queda como **Admin/Staff/POS/Landing SEO** (Fase 7, `ng build` OK). Deep links `fashionstore://fitting/:variantId` conectados (Fase 8) y **AR con prendas reales liberado 21/09/2026** (assets + anclaje automático por pose + selector). **Pendiente:** probar en **dispositivo físico con cámara** (CU-19 AR) y los deep links.
- [x] **BD demo limpia — HECHO 21/09/2026**: Neon re-creada (`DROP SCHEMA public CASCADE` + `CREATE SCHEMA public` + `alembic upgrade head` + `python -m scripts.seed`). Seed extendido e idempotente: 6 usuarios demo (incluye **cliente real `sonclargod@gmail.com` / `Client123!`**), CASHIER con Employee, 2 sucursales (La Paz + Santa Cruz), 10 prendas con variantes/inventario en ambas, promoción "Primera reserva -10%", 3 reservas demo (PENDING/PREPARED/IN_TRIAL), 1 venta PAID con detalle+pago+comprobante. Verificado login de los 6 roles + rutas (`catalog`, `categories`, `notifications`, `sales`, `users`, `reservations`). **87/87 tests backend en verde** (con BD limpia). Bonus: corregida la migración `62fce272acff` que borraba la constraint `uq_product_embeddings_variant_id` y el índice ivfflat (rompía `ON CONFLICT`; 2 tests de recommendations ahora pasan).
- [ ] **Exportar diagramas:** **no se hará** (omitido).

## 🟢 Backlog

### Ciclo 1 (completado — tag `v1.0.0-ciclo1`)

#### Paquete: Autenticación y gestión de usuarios
- [x] CU-01 Iniciar sesión (+ UML)
- [x] CU-02 Cerrar sesión (+ UML)
- [x] CU-04 Gestionar usuarios y roles (+ UML)

#### Paquete: Gestión y consulta del catálogo
- [x] CU-06 Gestionar ciudades y sucursales (+ UML)
- [x] CU-07 Gestionar productos de ropa (+ UML). ✔ `PATCH`/`DELETE` (soft
      delete) implementados y probados (11 tests) + sección Productos en el admin.
- [x] CU-12 Consultar catálogo (+ UML)
- [x] CU-13 Buscar y filtrar prendas (+ UML)
- [x] CU-14 Consultar disponibilidad por sucursal (+ UML)

#### Paquete: Reservas y experiencia de compra
- [x] CU-15 Gestionar reserva de múltiples prendas (+ UML) ⚠️ Tests fallando → ver PLAN_CICLO_1.md §DIAGNÓSTICO
- [x] CU-17 Gestión de recepción y atención de reservas (+ UML) ⚠️ Tests fallando → ver PLAN_CICLO_1.md §DIAGNÓSTICO. El listado general de
      reservas por staff quedó **resuelto en Ciclo 2** (CU-18 → `GET /reservations`); falta
      solo corregir la nota en la tabla de CU-17 (housekeeping).

#### Transversal
- [x] Base del backend (FastAPI + core + esquemas).
- [x] **Pendientes preexistentes (Ciclo 1) — RESUELTOS**: CU-15 y CU-17 (7 fallos: `KeyError: 'id'` + stock Neon) — diagnóstico en `PLAN_CICLO_1.md` §DIAGNÓSTICO; reparación en `PLAN_REPARACION_CICLO_1.md`; suite completa **74/74 verde** (aislamiento stock/carrito en `conftest.py`)
- [x] UML (secuencia + comunicación) por cada CU implementado, agrupado por paquete.
- [x] Tabla de caso de uso por CU (formato RULES §7).

> Nota: diagramas y tablas usan la **numeración oficial** del proyecto
> (`docs/uml/ciclo1/{autenticacion-usuarios,gestion-catalogo,reservas}/CU-XX/`).
> Pagos e inventario/ajustes y recomendaciones IA se evalúan en Ciclo 2.

### Ciclo 2 (completado — tag `v2.0.0-ciclo2`)

#### Paquete: Autenticación y gestión de usuarios
- [x] CU-03 Recuperar contraseña (+ UML)
- [x] CU-05 Registro y gestión de perfil de cliente (+ UML)

#### Paquete: Gestión y consulta del catálogo
- [x] CU-08 Gestión de categorías, tallas y colores (+ UML)
- [x] CU-09 Gestión de temporadas y colecciones (+ UML)
- [x] CU-10 Gestión de proveedores (+ UML)

#### Paquete: Reservas y experiencia de compra
- [x] CU-16 Consulta y cancelación de reservas (+ UML)
- [x] CU-18 Preparación de prendas reservadas (+ UML)
- [x] CU-19 Probador virtual AR móvil (+ UML)
- [x] CU-20 Gestión del carrito de compras (+ UML)
- [x] CU-21 Realizar compra en línea (+ UML)

#### Paquete: Ventas, pagos e inventario
- [x] CU-23 Venta presencial (POS) (+ UML)
- [x] CU-24 Pago en caja y comprobante (+ UML)

#### Transversal
- [x] UML (secuencia + comunicación) por paquete y numeración oficial (`docs/uml/ciclo2/`).

> Nota: diagramas y tablas usan la **numeración oficial** del proyecto. El email real
> (SendGrid/Mailgun) y la UX de CU-03 quedan anotados en 🟡 Técnicos. El warp 2D guiado
> por pose con assets reales del probador AR **fue implementado 21/09/2026** (assets PNG en
> `mobile/assets/images/garments/` + `GarmentOverlayPainter` con anclaje automático).

### Ciclo 3 (completado — tag `v3.0.0-ciclo3`)

#### Paquete: Gestión y consulta del catálogo
- [x] CU-11 Gestionar promociones (+ UML)

#### Paquete: Reservas y experiencia de compra
- [x] CU-22 Consultar historial de compras (+ UML)

#### Paquete: Ventas, pagos e inventario
- [x] CU-25 Procesar pago electrónico (+ UML) — gateway QR estático simulado
- [x] CU-26 Consultar comprobantes y compras (+ UML)
- [x] CU-27 Gestionar existencias por sucursal (+ UML)
- [x] CU-28 Registrar movimientos de inventario (+ UML)
- [x] CU-29 Registrar recepción de productos (+ UML)

#### Paquete: Inteligencia artificial
- [x] CU-30 Recomendar productos mediante IA (+ UML)
- [x] CU-31 Asistir al cliente mediante IA (+ UML) — chat con Ollama local + RAG
- [x] CU-32 Generar consultas y reportes mediante IA (+ UML) — NL→SQL seguro

#### Paquete: Reportes y control administrativo
- [x] CU-33 Consultar reportes e indicadores (+ UML) — KPIs ventas, stock, rotación
- [x] CU-34 Consultar bitácora y trazabilidad del sistema (+ UML) — AuditLog
- [x] CU-35 Consultar información consolidada de ventas e inventario (+ UML)

- [x] UML (secuencia + comunicación) por paquete y numeración oficial (`docs/uml/ciclo3/`).
- [x] Tests: suite completa verde (98 tests aprox).
- [x] Migración Alembic: `alembic revision --autogenerate -m "ciclo3"` aplicable en Neon.

> Nota: 13 CUs implementados, 8 workstreams completados. `PLAN_CICLO_3.md` tiene el detalle técnico.