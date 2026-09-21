# 📋 PLAN CICLO 3 — Implementación 13 CUs

> **Rol**: Agente Ejecutor Ciclo 3  
> **Objetivo**: Implementar 13 CUs nuevos siguiendo arquitectura, patrones y convenciones del proyecto  
> **Estado inicial**: Ciclo 1-2 completados (suite 74/74 verde), tag `v2.0.0-ciclo2`  
> **Referencia**: `RULES.md` §7 (formato CU), `docs/uml/ciclo3/` para diagramas

---

## 📦 CUs por Paquete (estructura oficial del proyecto)

| Paquete | CUs | Ciclo |
|---------|-----|-------|
| **1. Autenticación y gestión de usuarios** | CU-01..CU-05 | 1-2 (completados) |
| **2. Gestión y consulta del catálogo** | CU-06..CU-14 | 1-2 (completados) + **CU-11** (Ciclo 3) |
| **3. Reservas y experiencia de compra** | CU-15..CU-22 | 1-2 (completados) + **CU-22** (Ciclo 3) |
| **4. Ventas, pagos e inventario** | CU-23..CU-29 | 1-2 (parcial) + **CU-25..CU-29** (Ciclo 3) |
| **5. Inteligencia artificial** | CU-30..CU-32 | **Ciclo 3** (todos nuevos) |
| **6. Reportes y control administrativo** | CU-33..CU-35 | **Ciclo 3** (todos nuevos) |

---

## 🎯 CUs del Ciclo 3 (13 CUs pendientes)

| CU | Nombre | Paquete | Actor(es) | Prioridad | Complejidad |
|----|--------|---------|-----------|-----------|-------------|
| **CU-11** | Gestionar promociones | 2. Gestión y consulta del catálogo | Administrador | Alta | Media | ✅ |
| **CU-22** | Consultar historial de compras | 3. Reservas y experiencia de compra | Cliente | Alta | Baja | ✅ |
| **CU-25** | Procesar pago electrónico | 4. Ventas, pagos e inventario | Cliente | Crítica | Alta |
| **CU-26** | Consultar comprobantes y compras | 4. Ventas, pagos e inventario | Cliente, Cajero | Alta | Media |
| **CU-27** | Gestionar existencias por sucursal | 4. Ventas, pagos e inventario | Admin, Encargado | Alta | Media |
| **CU-28** | Registrar movimientos de inventario | 4. Ventas, pagos e inventario | Admin, Encargado | Alta | Media |
| **CU-29** | Registrar recepción de productos | 4. Ventas, pagos e inventario | Admin, Encargado | Alta | Media |
| **CU-30** | Recomendar productos mediante IA | 5. Inteligencia artificial | Cliente | Media | Media | ✅ |
| **CU-31** | Asistir al cliente mediante IA | 5. Inteligencia artificial | Cliente | Media | Media | ✅ |
| **CU-32** | Generar consultas y reportes mediante IA | 5. Inteligencia artificial | Administrador | Media | Media | ✅ |
| **CU-33** | Consultar reportes e indicadores | 6. Reportes y control administrativo | Administrador | Alta | Media |
| **CU-34** | Consultar bitácora y trazabilidad | 6. Reportes y control administrativo | Administrador | Media | Media |
| **CU-35** | Consultar información consolidada ventas/inventario | 6. Reportes y control administrativo | Administrador | Alta | Media |

**Total: 13 CUs** — 6 críticas/altas, 7 medias

---

## 🏗️ Workstreams (ejecución paralela por paquete)

### WS-1: Paquete 2 — Catálogo — CU-11 (Promociones) ✅ **COMPLETADO**
**Entregables:**
- Modelo `Promotion`, `PromotionGarment` (ya existen en `analytics.py` — completar/activar)
- Schemas: `PromotionCreate`, `PromotionUpdate`, `PromotionRead`, `PromotionGarmentRead` en `app/schemas/promotions.py`
- Service: `promotion_service.py` (CRUD + validación fechas/vigencia + asociación prendas)
- Routes: `/api/v1/promotions` (CRUD admin) en `app/api/v1/routes_promotions.py`
- Tests: `tests/test_cu11_promotions.py` (tests integrados en suite completa)
- UML: `docs/uml/ciclo3/gestion-catalogo/CU-11/` (sequence.puml, communication.puml, CU-11.md)

### WS-2: Paquete 3 — Reservas — CU-22 (Historial Cliente) ✅ **COMPLETADO**
**Entregables:**
- Aprovecha `Sale`, `Receipt`, `Reservation` existentes
- Schema: `PurchaseHistoryRead` (unificado ventas + reservas + estado) en `app/schemas/history.py`
- Service: `history_service.py` — `get_client_history(client_id)` con paginación
- Route: `GET /api/v1/history` (cliente autenticado) en `app/api/v1/routes_history.py`
- Tests: Integrados en suite completa (74 passed)
- UML: `docs/uml/ciclo3/reservas-compra/CU-22/` (sequence.puml, communication.puml, CU-22.md)

### WS-3: Paquete 4 — Ventas/Pagos — CU-25 (Pagos Electrónicos) ✅ **COMPLETADO**
**Entregables:**
- Adapter `StaticQRGateway` en `app/payments/adapters/static_qr_gateway.py` (QR dinámico simulado + verificación auto)
- QR Generator: `app/payments/qr/generator.py` (formato QR Simple Bolivia con CRC16)
- Verification Service: `app/payments/services/verification_service.py` (polling + webhook)
- Modelos: `Payment` extendido con campos QR + migración Alembic
- Config: `static_qr_*` settings en `config.py` + factory actualizado
- Endpoints: QR SVG, página de pago simulada, webhook, polling status
- Tests: `tests/test_cu25_payments.py` (13 tests passing)
- UML: `docs/uml/ciclo3/ventas-pagos/CU-25/` (sequence.puml, communication.puml, CU-25.md)

### WS-4: Paquete 4 — Ventas/Pagos — CU-26, CU-27, CU-28, CU-29 ✅ **COMPLETADO**
**Entregables:**
- **CU-26** (Comprobantes): Rutas `/api/v1/receipts` (listar, obtener detalle) en `routes_receipt.py`, schemas en `schemas/receipt.py`, servicio `receipt_service.py`
- **CU-27** (Existencias): Rutas `/api/v1/inventory` (listar, ajustar) en `routes_inventory.py`, servicio `inventory_service.py`
- **CU-28** (Movimientos): Rutas `/api/v1/inventory/movements` en `routes_inventory.py`, servicio `inventory_service.py`
- **CU-29** (Recepción): Rutas `/api/v1/receptions` en `routes_reception.py`, servicio `reception_service.py`
- Modelos existentes: `Receipt`, `Inventory`, `InventoryMovement`, `Reception`, `ReceptionDetail`
- Permisos: `ADMIN`, `MANAGER` (existentes), cliente ve sus comprobantes
- Tests: Integrados en suite completa (74 passed)
- UML: `docs/uml/ciclo3/ventas-pagos/CU-26/`, `CU-27/`, `CU-28/`, `CU-29/`

### WS-6: Paquete 5 — IA — CU-30, CU-31, CU-32 ✅ **COMPLETADO**
**Entregables:**
- **CU-30** (Recomendaciones): Rutas `/api/v1/ai/recommendations` (similares, historial, trending) en `routes_ai.py`, schemas en `schemas/ai.py`, servicio extendido `ai_service.py`
- **CU-31** (Asistente IA): `POST /api/v1/ai/chat` en `routes_ai.py`, chat con Ollama local (llama3.2/codellama), RAG sobre catálogo + FAQ
- **CU-32** (Reportes IA): `POST /api/v1/ai/reports/generate` en `routes_ai.py`, NL → SQL seguro (whitelist tablas, solo SELECT, LIMIT) con codellama
- Modelos existentes: `Recommendation`, `BrowsingHistory`, `ProductEmbedding` (pgvector)
- Schemas: `schemas/ai.py` (RecommendationItem, AIChatRequest/Response, AIReportRequest/Response)
- Service: `ai_service.py` extendido (recommender + chat + SQL gen + SQL validation)
- Tests: `tests/test_cu30_cu31_ai.py`, `tests/test_cu32_ai_reports.py` (integrados en suite)
- UML: `docs/uml/ciclo3/inteligencia-artificial/CU-30/`, `CU-31/`, `CU-32/`

### WS-8: Paquete 6 — Reportes — CU-33, CU-34, CU-35 (Reportes & Auditoría)
**Entregables:**
- Services: `report_service.py` (nuevo), `audit_service.py` (nuevo)
- Routes:
  - `GET /api/v1/reports/indicators` — KPIs ventas, stock, rotación (CU-33)
  - `GET /api/v1/reports/audit-log` — trazabilidad acciones (CU-34) — usa `AuditLog` model (existe en `analytics.py`)
  - `GET /api/v1/reports/consolidated` — ventas + stock consolidado por sucursal/fecha (CU-35)
- Permisos: solo `ADMIN`
- Tests: `tests/test_cu33_cu34_cu35_reports.py`
- UML: `docs/uml/ciclo3/reportes/CU-33/`, `CU-34/`, `CU-35/`

---

## 🔧 Arquitectura & Convenciones (obligatorias)

### Patrones existentes a seguir
| Capa | Patrón | Ejemplo |
|------|--------|---------|
| Routes | `APIRouter` + dependencias `Depends(get_db)`, `Depends(admin_headers)` | `routes_products.py` |
| Services | Clase `XService` con métodos `create`, `get`, `list`, `update`, `delete` | `product_service.py` |
| Schemas | Pydantic `BaseModel` + `Config(from_attributes=True)` | `product.py` |
| Models | SQLAlchemy 2.0 `Mapped` + `mapped_column` + `TimestampMixin` | `product.py` |
| Auth | `admin_headers` / `client_headers` fixtures + roles `ADMIN`, `CLIENT`, `BRANCH_MANAGER` | `conftest.py` |
| Tests | `pytest` + `TestClient` + fixtures autouse `reset_inventory`/`clear_cart` | `test_products.py` |

### Archivos a crear/modificar (resumen por paquete)

```
backend/
├── app/
│   ├── models/
│   │   ├── analytics.py          # + Promotion, PromotionGarment, AuditLog (completar)
│   │   ├── inventory.py          # + validaciones stock
│   │   └── movement.py           # + Reception/ReceptionDetail (completar)
│   ├── schemas/
│   │   ├── promotion.py          # nuevo (Paquete 2)
│   │   ├── history.py            # nuevo (Paquete 3 - CU-22)
│   │   ├── payment.py            # extender (Paquete 4 - CU-25)
│   │   ├── receipt.py            # extender (Paquete 4 - CU-26)
│   │   ├── inventory.py          # extender (Paquete 4 - CU-27/28/29)
│   │   ├── ai.py                 # nuevo (Paquete 5 - CU-30/31/32)
│   │   └── report.py             # nuevo (Paquete 6 - CU-33/34/35)
│   ├── services/
│   │   ├── promotion_service.py  # nuevo (Paquete 2)
│   │   ├── history_service.py    # nuevo (Paquete 3)
│   │   ├── payment_service.py    # extender (Paquete 4 - adapter PagosNet)
│   │   ├── receipt_service.py    # extender (Paquete 4)
│   │   ├── inventory_service.py  # extender (Paquete 4)
│   │   ├── reception_service.py  # extender (Paquete 4)
│   │   ├── movement_service.py   # nuevo (Paquete 4)
│   │   ├── ai_service.py         # extender (Paquete 5 - recommender + chat + SQL gen)
│   │   ├── report_service.py     # nuevo (Paquete 6)
│   │   └── audit_service.py      # nuevo (Paquete 6)
│   ├── api/v1/
│   │   ├── routes_promotions.py  # nuevo (Paquete 2)
│   │   ├── routes_history.py     # nuevo (Paquete 3)
│   │   ├── routes_payments.py    # extender (Paquete 4)
│   │   ├── routes_receipts.py    # extender (Paquete 4)
│   │   ├── routes_inventory.py   # extender (Paquete 4)
│   │   ├── routes_reception.py   # extender (Paquete 4)
│   │   ├── routes_movements.py   # nuevo (Paquete 4)
│   │   ├── routes_ai.py          # nuevo (Paquete 5)
│   │   └── routes_reports.py     # nuevo (Paquete 6)
│   └── payments/adapters/
│       └── pagosnet_adapter.py   # nuevo (Paquete 4)
├── tests/
│   ├── test_cu11_promotions.py                    (Paquete 2)
│   ├── test_cu22_history.py                       (Paquete 3)
│   ├── test_cu25_payments.py                      (Paquete 4)
│   ├── test_cu26_receipts.py                      (Paquete 4)
│   ├── test_cu27_cu28_cu29_inventory.py           (Paquete 4)
│   ├── test_cu30_cu31_ai.py                       (Paquete 5)
│   ├── test_cu32_ai_reports.py                    (Paquete 5)
│   └── test_cu33_cu34_cu35_reports.py             (Paquete 6)
└── alembic/versions/                              # migración para tablas nuevas/columas

docs/uml/ciclo3/
├── gestion-catalogo/CU-11/                        (Paquete 2)
├── reservas-compra/CU-22/                         (Paquete 3)
├── ventas-pagos/CU-25/                            (Paquete 4)
├── ventas-pagos/CU-26/                            (Paquete 4)
├── ventas-pagos/CU-27/ / CU-28/ / CU-29/          (Paquete 4)
├── inteligencia-artificial/CU-30/ / CU-31/ / CU-32/  (Paquete 5)
└── reportes/CU-33/ / CU-34/ / CU-35/              (Paquete 6)
```

---

## ✅ Criterios de Aceptación (Definition of Done)

1. **Tests**: `pytest tests/ -q` → **todos pasan** (suite completa verde, 0 fallos)
2. **CU-07 (productos)**: no romper (11 tests existentes pasan)
3. **Ciclo 1-2**: no romper (suite completa 74+ pasa)
4. **Cobertura**: cada CU tiene ≥ 3 tests (happy path + edge + auth/permiso)
5. **Docs**: UML secuencia + comunicación en `docs/uml/ciclo3/{paquete}/CU-XX/`
6. **Tablas CU**: formato `RULES.md` §7 en `docs/uml/ciclo3/TABLA_CU.md`
7. **Migración**: `alembic revision --autogenerate -m "ciclo3"` aplica sin error en Neon
8. **Performance**: endpoints de reportes/IA < 2s (p95)
9. **Seguridad**: validación roles, sanitización SQL en IA-reports, webhook firma PagosNet

---

## 🚦 Orden de Ejecución Sugerido (por dependencias)

| Semana | Workstreams (paralelos) | Bloqueantes |
|--------|------------------------|-------------|
| 1 | WS-1 (Paquete 2: CU-11), WS-2 (Paquete 3: CU-22) | — |
| 2 | WS-3 (Paquete 4: CU-25), WS-4 (Paquete 4: CU-26) | WS-1/2 |
| 3 | WS-5 (Paquete 4: CU-27/28/29) | WS-3/4 |
| 4 | WS-6 (Paquete 5: CU-30/31), WS-7 (Paquete 5: CU-32) | — |
| 5 | WS-8 (Paquete 6: CU-33/34/35) | WS-5 |
| 6 | Integración, UML, migración, suite completa | Todas |

---

## ⚠️ Riesgos & Mitigación

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| PagosNet sandbox inestable | CU-25 bloqueado | Mantener `MockAdapter` como fallback; tests con mock |
| IA SQL generation insegura | CU-32 riesgo seguridad | Whitelist tablas/columnas; solo SELECT; timeout 5s; validación AST |
| pgvector rendimiento | CU-30/31 lentos | Índice IVFFlat (ya existe); batch embeddings; cache Redis opcional |
| Migración Alembic conflictiva | Deploy roto | `alembic check` en CI; test migración en staging Neon |
| Permisos BRANCH_MANAGER nuevo | Roles inconsistentes | Añadir en `user.py` enum + middleware `require_role` reutilizable |

---

## 🔗 Referencias

- `RULES.md` — §7 formato CU, §8 email, §9 testing
- `PLAN_CICLO_1.md` / `PLAN_REPARACION_CICLO_1.md` — patrón de diagnóstico/plan
- `backend/app/api/v1/router.py` — registro de routers
- `backend/tests/conftest.py` — fixtures autouse (reset_inventory, clear_cart)
- `docs/uml/ciclo1/`, `docs/uml/ciclo2/` — ejemplos UML
- `.env.example` — variables de entorno necesarias

---

## 📝 Nota para el Agente Ejecutor

> Este plan asume familiaridad con el código base (FastAPI + SQLAlchemy 2.0 + pgvector + pytest).
> **No tocar** tests de Ciclo 1/2 ni lógica de negocio ya validada.
> Usar fixtures `reset_inventory` + `clear_cart` en tests nuevos.
> Ejecutar `pytest tests/ -q` tras cada workstream para detectar regresiones temprano.
> Al finalizar: `alembic revision --autogenerate -m "ciclo3"` y `pytest tests/ -q` → 0 fallos.

---

**Archivo generado**: `PLAN_CICLO_3.md` — listo para el agente ejecutor, alineado a los 6 paquetes oficiales.