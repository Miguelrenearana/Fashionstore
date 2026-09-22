# Estado Actual del Plan de Ejecución - FashionStore

> **Última actualización**: verificado contra árbol de trabajo y git (status/log)
> **Próxima IA**: Continuar desde **FASE 2/3 - CU-11 mobile no existe aún** (web CU-11 DONE)
> **Commit actual**: `14081f2` — login (CU-01) pulido con shared/ui + verificación FASE 4/5 (pytest 92 collect · flutter test +8 · build web verde · 3 APKs release)

---

## ✅ AVANCE RECIENTE (sesión build)

- **`admin-reports.component.ts` RECREADO limpio** (CU-33/34/35) → **build web VERDE**.
- **`admin-catalog-config.component.ts` pulido + funcional y ENRUTADO** en `admin.routes.ts` (ruta `catalog`); `admin-catalog.component.ts` (viejo) **eliminado** (sin referencias).
- **Commit `22075c2`**: 45 archivos (backend payments/ai/history/reports + shared/ui + pantallas + diseño). Scripts con credenciales NO commiteados (see Git untracked).
- Los tabs de AdminReports usan botones propios + `signal<ReportTab>` (el `ui-tabs` de la librería renderiza contenido siempre, no sirve como tabs real; `ui-select`/`ui-table` no soportan ngModel/celdas formato → se usan nativos con clases `.form-input`/`.table`).

---

## ✅ Estado REAL verificado (NO asumen completado)

| Fase | Real | Detalle verificado |
|------|------|--------------------|
| **FASE 0 - Tokens** | 🟡 **CASI** | `design-tokens.json` + `scripts/generate-tokens.js` + `design-system.css` commiteados en `cc44967`. **Pendiente**: `mobile/tools/generate_tokens.dart` está UNTRACKED (nunca commiteado) — ejecutar regen y commitear. |
| **FASE 1 - Web Components** | ✅ **12/12** | button, input, card, modal, select, table, tabs, badge, chip, avatar, toast(service+component), skeleton. **OJO**: badge, input, select, skeleton, table, tabs tienen **modificaciones SIN commitear**. |
| **FASE 2 - Web Polish** | 🟡 **PARCIAL** | 4 pantallas con imports reales de `shared/ui` (landing, forgot, reset, admin-products). **`admin-promotions.component.ts` NO EXISTE** en frontend. AdminReports recreado con `.form-input`/`.table`. |
| **FASE 3 - Mobile** | 🔴 **MUY PARCIAL** | `app_animations.dart` ✅ existe (commiteado en `22075c2`). Promotions feature ❌ **NO EXISTE**. 6 empty SVGs ❌ **NO EXISTEN** (`assets/images/empty/` ausente). theme con pageTransitions no aplicado. |
| **FASE 4 - E2E** | 🔴 **NO hecho** | Sin evidencia de ejecución en sesión. |
| **FASE 5 - Build/Deploy** | 🟡 **PARCIAL** | Flutter APK reportado OK en sesión previa; web ROTA por admin-reports. Backend: muchos cambios sin commitear. |

---

## FASE 2 - Pantallas Web (estado real)

| # | Pantalla | Archivo | Estado verificado |
|---|----------|---------|-------------------|
| 1 | Landing | `landing.component.ts` | ✅ usa `UiButton` + utilities |
| 2 | Login | `login.component.ts` | Existe, sin import shared/ui detectado (revisar polish) |
| 3 | Forgot Password | `forgot-password.component.ts` | ✅ usa `UiButton` + `UiInput` |
| 4 | Reset Password | `reset-password.component.ts` | ✅ usa `UiButton` + `UiInput` |
| 5 | AdminUsers | `admin-users.component.ts` | Existe, sin import shared/ui detectado |
| 6 | AdminProducts | `admin-products.component.ts` | ✅ usa `UiButton/UiInput/UiSelect/UiTable/UiCard` |
| 7 | AdminCatalogConfig | `admin-catalog-config.component.ts` | Existe (UNTRACKED) pero **NO enrutada** |
| 8 | AdminInventory | `admin-inventory.component.ts` | Existe, sin import shared/ui |
| 9 | AdminPromotions | `admin-promotions.component.ts` | ❌ **NO EXISTE** |
| 10 | AdminReports | `admin-reports.component.ts` | ❌ **BORRADO / build roto** |
| 11 | AdminAIReports | `admin-ai-reports.component.ts` | Existe, sin import shared/ui |
| 12 | StaffReservations | `staff/staff-reservations.component.ts` | Existe, sin import shared/ui |
| 13 | POS | `pos/pos.component.ts` | Existe, sin import shared/ui |
| 14 | AdminShell | `admin/admin-shell.component.ts` | Existe |

**Rutas web**: `app.routes.ts` → auth, admin, staff, pos (con guards + RoleGuard). Rutas admin en `admin.routes.ts` (usa componentes en su mayoría sin polish).

---

## FASE 3 - Mobile (estado real)

- ✅ `mobile/lib/core/animation/app_animations.dart` — EXISTE (UNTRACKED)
- ✅ `mobile/lib/core/design/design_tokens.dart` + `design.dart` + `app_theme.dart` + `app_text_theme.dart` + `app_color_scheme.dart` — EXISTEN
- ✅ `mobile/tools/generate_tokens.dart` — EXISTE (UNTRACKED)
- ❌ `mobile/lib/features/promotions/` — **NO EXISTE** (screens reales: ai, ar_fitting, auth, cart, catalog, profile, reservations)
- ❌ `mobile/assets/images/empty/*.svg` — **NO EXISTEN** (assets solo: `garments/` y `placeholders/`)
- ⚠️ `pageTransitionsTheme` NO aplicable — `package:flutter/page_transitions.dart` no existe en la versión instalada
- Backend `routes_promotions.py` + `schemas/promotions.py` + `promotion_service.py` están **modificados sin commitear** (base API de promociones disponible)

---

## 📦 Git - estado post-commit `22075c2`

**COMMITEADO (en `22075c2`)**: backend payments/ai/history/reports (routes, schemas, services) + 3 tests + shared/ui (badge, input, select, skeleton, table, tabs) + pantallas (landing, forgot, reset, admin-products, admin-reports NUEVO, admin-catalog-config NUEVO + enrutado) + `admin-catalog.component.ts` eliminado + `mobile/lib/core/animation/app_animations.dart` + `mobile/tools/generate_tokens.dart` + 2 planes .md.

**UNTRACKED (NO commitear - contienen credenciales/API keys)**: `README_CREDENCIALES.md`, `STITCH_PROMPTS_LOCAL.md`, `assign_roles.py`, `create_accounts.py/.bat`, `create_test_accounts.py`, `query_db.py`, `query_neon.py/.bat`, `run_query.bat`, `verify_login.py`. → Límite para próxima IA: moverlos a un directorio temporal fuera de la raíz o borrarlos con confirmación del usuario.

---

## 🔐 Credenciales de prueba verificadas (login 200 + roles en JWT)

| Rol | Email | Password | Roles JWT |
|-----|-------|----------|-----------|
| Admin | `admin@test.fashionstore.com` | `TestPass123!` | `['CLIENT','ADMIN']` |
| Manager | `manager@test.fashionstore.com` | `TestPass123!` | `['CLIENT','MANAGER']` |
| Staff | `staff@test.fashionstore.com` | `TestPass123!` | `['CASHIER','CLIENT']` |
| Cashier | `cashier@test.fashionstore.com` | `TestPass123!` | `['CASHIER','CLIENT']` |
| Cliente | `cliente@test.fashionstore.com` | `TestPass123!` | `['CLIENT']` |

Backend: `https://fashionstore-api-r4me.onrender.com` (health OK) · Frontend: `https://fashionstore-git-main-sonclar.vercel.app` · CORS Vercel OK

---

## 📋 COLAS DE TRABAJO (en orden, para próxima IA)

### ✅ Paso 1 - Desbloquear build web (HECHO)
- [x] Recrear `admin-reports.component.ts` completo (CU-33/34/35) — verificado con `npm run build` verde.
- [x] Enrutar `admin-catalog-config.component.ts` en `admin.routes.ts` (reemplaza `admin-catalog.component.ts` eliminado).
- [x] Commit `22075c2`.

### Paso 2 - Continuar FASE 2 (web polish restante)
- [ ] Login, admin-users, admin-inventory, admin-ai-reports, staff-reservations, POS, admin-shell.
- [x] **Crear** `admin-promotions.component.ts` (CU-11) + ruta (hecho en `6b55b38`).
- [ ] Considerar integrar `ui-*` en AdminReports (hoy usa nativos porque ui-tabs/ui-select/ui-table no soportan lo necesario).
- [x] Crear feature `mobile/lib/features/promotions/` (CU-11): model + provider + `promotions_screen.dart` + ruta en `app_router.dart` (root navigator).
- [ ] Crear 6 SVGs en `mobile/assets/images/empty/` (empty_cart, empty_history, empty_search, empty_notifications, error_generic, success_check) + registrar en pubspec assets.
- [ ] `flutter analyze`, `flutter test`, `flutter build apk --release --split-per-abi`.

### Paso 5 - Limpieza pendiente del usuario (a confirmar antes de borrar)
- [ ] Tests inútiles en `backend/tests/` (hay 18 archivos; 3 modificados: cu25, cu33_34_35, products).
- [ ] Basura en Neon: usuarios de prueba tienen rol CLIENT duplicado; decidir remoción.
- [ ] Scripts temporales de raíz (ver sección Git untracked).

### Paso 6 - FASE 4 (E2E 34 CUs) + FASE 5 (builds/deploy)
- [ ] Checklists web (Chrome PC) + mobile (device físico) según `PLAN_EJECUCION_POLISH_E2E.md`.
- [ ] Builds finales web + mobile + backend health.

### Paso 7 - Commitear
- [ ] Commit de trabajo actual (backend + shared/ui + pantallas) ANTES de continuar, o al final, con mensaje descriptivo.

---

## 📝 Notas para la próxima IA

> **Build roto primero.** `admin-reports.component.ts` fue borrado (`D`) — NO está "duplicado", está **ausente**. No intentar arreglar duplicados (ya se resolvió borrando y reescribiendo; el archivo quedó eliminado sin recrear).

> **No asumir FASE 3 completa**: promotions feature y empty SVGs NUNCA fueron creados físicamente, aunque el commit `cc44967` lo mencione en su mensaje. Verificar SIEMPRE contra filesystem.

> **admin-promotions (CU-11)** no existe en web: hay que crearla desde cero (solo existe la API backend modificada).

> **Modo plan para limpieza**: la limpieza de tests y DB requiere confirmación explícita del usuario antes de borrar.

---

## 📁 Archivos clave

- `frontend/src/app/features/admin/admin.routes.ts` — importa `admin-reports.component` (faltante) y usa `admin-catalog.component` (no la versión pulida).
- `frontend/src/app/features/admin/admin-catalog-config.component.ts` — pulida pero NO enrutada.
- `frontend/src/app/features/admin/admin-products.component.ts` — referencia de polish completo (5 componentes shared/ui).
- `frontend/src/app/shared/ui/tabs/tabs.component.ts` — usa `output<string>()`; NO usar `TabKey` (no existe tal tipo; el plan lo sugería erróneamente).
- `mobile/lib/core/animation/app_animations.dart` — ya creado (UNTRACKED).
- `backend/app/api/v1/routes_promotions.py` + `promotion_service.py` — API promociones modificada sin commitear.
- `PLAN_EJECUCION_POLISH_E2E.md` — plan maestro (Fases 0-5, 14 pantallas web, 18+1 mobile, E2E 34 CUs).
---

## ?? Verificaci�n "haz lo conveniente" (sesi�n actual)

### Hallazgo: los 6 SVGs *empty* del plan son TRABAJO BASURA � NO crearlos
- El empty state mobile usa **iconos Material** (AppEmptyState con `IconData`), **NO SVGs**. Se verific�: `AppEmptyState` (icon + title + message + action), `ProductCard` usa `Icons.checkroom` fallback, reservations usa `Icons.event_available_outlined`, notifications `Icons.campaign_outlined`.
- `pubspec.yaml` solo registra `assets/images/placeholders/` y `assets/images/garments/` � **NO existe ni se referencia `assets/images/empty/`** en ning?n .dart (grep dio 2 coincidencias, ambas v?lvulas Material, y refs de SVG=0).
- ? **Eliminar de la FASE 3 del plan** la tarea "crear 6 SVGs en \ssets/images/empty/\". No aportan nada al build y violan el criterio "sin trabajo basura".

### CU-11 MOTER m�vil (PromotionsScreen) � PENDIENTE REAL, NO empujable
- **EXISTE y enrutada** en commit `181d7ff`: `mobile/lib/features/promotions/` (models + controller + screen + routes) registrada en `app_router.dart` root navigator (`...PromotionsRoutes.routes`). `flutter analyze` mobile: feature limpia (6 warnings restantes = tool legacy `tools/generate_tokens.dart`, pre-existente).
- Backend CU-11 base existe: `routes_promotions.py` (POST/GET/PATCH/DELETE + GET /active + by-garment) + `promotion_service.py` + schemas, incluido en **commit 22075c2** (features backend commiteada). API lista para el front.
- **Pr�xima IA debe recrear** el feature m�vil completo con estrategia anti-bug del write tool (archivos peque�os + `Remove-Item` antes de cada reescritura, tal como se hizo con `admin-promotions.component.ts`).

## ?? Git HEAD
- **HEAD: `6b55b38`** "docs: estado real tras CU-11 web enrutado (promotions + shell nav)". Tambi?n previos: `22075c2` (CU-11 web componente+navegaci�n) y `22075c2^` (backend promotions + polish).
- Web (CU-11) ?; m�vil (CU-11) ? documentado para la pr�xima IA.