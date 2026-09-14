# CHANGES — Bitácora de cambios

Formato: fecha · resumen · referencias (overleaf-caso de uso si aplica).

---

## 2026-09-13 — Ciclo 2 (autenticación, catálogo, reservas, ventas y pagos)

- **CU-03 Recuperar contraseña / CU-05 Registro y perfil de cliente:**
  - Backend: modelo `PasswordReset` (tabla `password_reset`, hash del token + expiración 30 min)
    y migración `0002_ci2_extra`; `POST /auth/register`, `POST /auth/forgot-password`,
    `POST /auth/reset-password` (email mock vía notificaciones); `GET/PATCH /clients/me`.
    `register_client` crea `User` (CLIENT) + `Client` y devuelve JWT (sesión automática).
  - Frontend: componentes `register`, `forgot-password`, `reset-password`; perfil reescrito
    contra `/clients/me` con formulario de edición; `storeToken` en `auth.service`.
  - Tests: `test_cu03_cu05.py` (8). `conftest` limpia ahora Notification/PasswordReset/
    BrowsingHistory/Employee/Client antes de borrar el usuario.
- **CU-08 Categorías/tallas/colores · CU-09 Temporadas/colecciones · CU-10 Proveedores:**
  - Backend: `catalog_config_service` y `supplier_service`; rutas `GET /catalog/options/…`
    (públicas) y `POST/PATCH` (ADMIN/MANAGER); `GET/POST/PATCH /suppliers` (mutaciones
    ADMIN/MANAGER).
  - Frontend: sección "Gestión de catálogo" en `/admin` (tallas, colores, temporadas,
    categorías, colecciones y proveedores con formularios de creación y listas).
  - Tests: `test_cu08_cu09_cu10.py` (8).
- **CU-16 Consulta/cancelación de reservas · CU-18 Preparación de prendas:**
  - `GET /reservations` (staff, con filtro `?status=`; staff = rol ADMIN/MANAGER/CASHIER o
    empleado) añadido; la consulta propia y la cancelación por el cliente ya existían del
    Ciclo 1. Tests: `test_cu16_cu18.py` (5).
- **CU-19 Probador virtual (AR móvil):**
  - `ar_fitting_screen.dart` reescrito: preview real de cámara (`camera`), detección de pose
    por frame (`google_mlkit_pose_detection`) dibujando hombros/caderas, overlay de prenda
    arrastrable/escalable y controles (mostrar prenda, detectar pose, reajustar, capturar).
    Painter extendido con offset/escala/landmarks; `google_mlkit_commons` añadido al pubspec.
    `flutter analyze` limpio.
- **CU-20 Carrito de compras · CU-21 Compra en línea:**
  - Backend: `PATCH/DELETE /cart/items/{variant_id}` y `POST /cart/purchase` (crea la venta
    desde el carrito, inicia el pago, desactiva el carrito y responde `{sale, payment}`).
  - Frontend: carrito reescrito con ±cantidad, quitar y "Comprar ahora".
  - Tests: `test_cu20_cu21.py` (4).
- **CU-23 Venta presencial · CU-24 Pago en caja y comprobante:**
  - Backend: `receipt_service` (factura `CUF-…`/nota de crédito `NC-…` por tipo, dedup por
    venta); `payments.confirm` COMPLETED genera factura y REFUNDED genera nota de crédito;
    `GET /sales/{id}/receipt`.
  - Frontend: POS reescrito (registrar venta → cobrar → confirmar → mostrar/descargar
    comprobante).
  - Tests: `test_cu23_cu24.py` (2).
- **UML Ciclo 2:** `docs/uml/ciclo2/` organizado por paquete y numeración oficial
  (12 CU × {sequence,communication,CU-XX.md}; `README.md` actualizado).
- **Calidad:** suite backend completa: **63 tests** (1 warning) contra BD Neon; `ruff
  check app alembic tests scripts` limpio; `npm run build` OK; `flutter analyze` OK.
- Referencias: overleaf CU-03, CU-05, CU-08, CU-09, CU-10, CU-16, CU-18, CU-19, CU-20,
  CU-21, CU-23, CU-24.

---

- **Docs:** `docs/uml/ciclo1/` reorganizado por **paquete** con la **numeración oficial** del
  proyecto (cada CU del examen es un caso de uso aparte):
  - `autenticacion-usuarios/`: CU-01 Iniciar sesión · CU-02 Cerrar sesión · CU-04 Gestionar usuarios y roles.
  - `gestion-catalogo/`: CU-06 Ciudades y sucursales · CU-07 Productos de ropa · CU-12 Consultar
    catálogo · CU-13 Buscar y filtrar prendas · CU-14 Disponibilidad por sucursal.
  - `reservas/`: CU-15 Reserva de múltiples prendas · CU-17 Recepción y atención de reservas.
- Se eliminan las carpetas planas anteriores con la numeración interna (CU-01…CU-17).
- **Cuadre con la implementación:** los diagramas reflejan los endpoints reales del backend;
  el listado general de reservas por staff y cobro/pago quedan como pendientes (pagos → Ciclo 2;
  la consulta de reservas recibidas se documenta como pendiente en la tabla CU-17).
- Referencias: listado oficial de casos de uso entregado por el dueño del proyecto.

---

## 2026-09-13 — CU-17 Recomendaciones IA (pgvector)

- **Backend ML:** backfill `recompute_embeddings` codifica nombre+categoría+descripción por variante
  con `all-MiniLM-L6-v2` (384d) e inserta en `product_embeddings` (constraint única
  `uq_product_embeddings_variant_id` añadida a la migración). `GET /recommendations`
  recomienda por similitud coseno (`embedding <=> CAST(:vec AS vector)`, índice ivfflat)
  excluyendo la variante origen o usando el historial de navegación; `POST
  /recommendations/view/{variant_id}` registra vistas; el score se persiste en `recomendacion`.
- **BD Neon:** embeddings generados + índice consolida; verificado con peticiones reales (variante
  2 recomendada al ver la 1, afinidad 100%).
- **Tests:** 3 nuevas (`tests/test_recommendations.py`): requiere auth, por variante (score>0,
  excluye origen) y por historial. Total: 36.
- **Frontend:** sección "También te puede interesar" en el detalle de producto (afinidad %, enlace
  al catálogo) para clientes autenticados.
- **UML + tabla CU:** `docs/uml/ciclo1/CU-17/{sequence,communication}.puml`.
- Referencias: overleaf CU-17.

## 2026-09-13 — CU-13 Reservas / CU-14 Ventas / CU-15 Pagos

- **Backend CU-13:** `POST /cart/checkout` ahora convierte el carrito en reserva (pickup_code,
  vencimiento 30 min) reservando stock y vaciando el carrito; `GET /reservations/me`, `GET
  /reservations/{id}`; transición de estados solo por staff (PENDING→PREPARED→IN_TRIAL) o el
  dueño cancelando PENDING. Cancelación/vencimiento liberan `reserved_quantity`.
- **Backend CU-14:** `POST /sales` admite `reservation_id` (venta desde reserva: consume stock
  real + reservado, marca la reserva COMPLETED con historial y notifica) o `items` (venta directa,
  solo staff); `GET /sales/{id}` con guardas de propiedad y `GET /sales` (staff: todas; cliente:
  propias). `status` añadido al ORM `Sale` (PENDING/PAID/CANCELLED/REFUNDED, columna ya migrada).
- **Backend CU-15:** `POST /payments/initiate` (auth), `/confirm` marca la venta **PAID** con
  `paid_at` o **CANCELLED** si DECLINED, `/refund` marca la venta **REFUNDED**; gateway Mock con
  escenarios success/declined/timeout por email.
- Fixes: `expires_at`/`paid_at` como `datetime` en schemas; `notification_service.notify` (instancia);
  `cart_service.add_item` elige sucursal con stock cuando el carrito no define branch; factura con
  microsegundos (unicidad).
- **Tests:** 5 nuevas (`tests/test_reservations.py`): checkout→reserva, cancelación con liberación
  de stock, venta desde reserva, venta directa solo staff, flujo pago completo. Total: 33.
- **Frontend:** `/cart` con total y botón "Reservar y check-out" (muestra el código de recogida);
  `/reservations` con estado, vencimiento y cancelación de reservas propias.
- **UML + tabla CU:** `docs/uml/ciclo1/CU-13|14|15/{sequence,communication}.puml` + tablas.
- Referencias: overleaf CU-13, CU-14, CU-15.

## 2026-09-13 — CU-12 Inventario y stock

- **Backend:** `GET /inventory` lista stock por sucursal con detalle de variante (prenda, SKU,
  talla, color, reservado); `GET /inventory/movements` (historial IN/OUT); `PATCH
  /inventory/{branch}/{variant}/adjust` con validación de stock no-negativo y no menor al
  reservado. Rutas protegidas (ADMIN/MANAGER). **Tests:** 5 nuevas (listado, 403, ajuste,
  stock negativo, movimientos). Total: 28.
- **Frontend:** panel de inventario en `/branch` (selector de sucursal, tabla de stock y
  ajuste ±1 con motivo).
- **UML + tabla CU:** `docs/uml/ciclo1/CU-12/{sequence,communication}.puml`.
- Referencias: overleaf CU-12.

## 2026-09-13 — CU-04 Sucursales y ciudades

- **Backend:** `POST /locations/branches` restringido a ADMIN/MANAGER; `list_branches` precarga
  la ciudad. **Tests:** 5 nuevas pruebas de sucursales (listados, permisos, creación, ciudad no
  encontrada). Total: 23.
- **Frontend:** módulo `/branch` funcional (tarjetas de sucursales + formulario de creación con
  selector de ciudad); enlace "Sucursales" en navbar.
- **UML + tabla CU:** `docs/uml/ciclo1/CU-04/{sequence,communication}.puml`.
- Referencias: overleaf CU-04.

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

- Despliegue a nubes (Render/Vercel/Firebase) cuando el dueño lo solicite.