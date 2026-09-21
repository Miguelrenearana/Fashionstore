# Plan Completo: Flutter App Completa + Web Admin (Opción B)

**Estado actual:** Fases 0-8 completas + APK compilado (21/09/2026). `flutter analyze` y `flutter test` (8 tests) en verde. Angular reducido a solo-web (admin/staff/POS/landing) con PWA. CI/CD en GitHub Actions.
**Última tarea completada (21/09/2026):** Técnicos finales: **email real via Gmail SMTP** (App Password, `notification_service` con `smtplib` STARTTLS, `render.yaml` con vars SMTP), **UI de notificaciones** en web (`NotificationsComponent` campana + página `/notifications`, navbar) y móvil (`notifications_screen.dart` conectado a `GET/PATCH /notifications`), y **BD demo sembrada desde cero** con el seed extendido: 6 roles (incluye cliente real `sonclargod@gmail.com` / `Client123!`), CASHIER con Employee, 2 sucursales (La Paz + Santa Cruz), 10 prendas con variantes/inventario en ambas, promoción, 3 reservas demo y 1 venta PAID con pago/comprobante. BD Neon re-creada (`DROP SCHEMA public CASCADE` + `alembic upgrade head` + seed) y verificado login de los 6 usuarios + rutas. Backend: **87/87 tests verdes**; móvil: `flutter analyze` sin issues + 8 tests; web: `ng build` OK. Se corrigió además el bug de la migración `62fce272acff` que borraba la constraint única de `product_embeddings.variant_id` y el índice ivfflat (rompía `ON CONFLICT`).

**Próxima tarea:** Probar el APK en dispositivo físico (CU-19 cámara/AR y deep links) y confirmar redeploy Vercel. Pendiente del dueño: **App Password de Gmail** de `sonclargod@gmail.com` para activar el envío real (configurar `SMTP_USER`/`SMTP_PASSWORD`/`MAIL_FROM` en `backend/.env` y Render).
---

## Resumen del Proyecto

### Arquitectura Definitiva (Basada en Casos de Uso)
- **Flutter App (APK)** - Cliente completo: Auth, Catálogo, Carrito, Checkout, Reservas, Perfil, AR, IA, Notificaciones
- **Web Angular (Admin/Staff/SEO)** - Solo: Admin dashboard, Staff sucursal, POS, Inventario, Reportes, Landing SEO
- **Backend FastAPI** - API compartida para ambos
- **Design System Unificado** - `design-tokens.json` como única fuente de verdad

### Distribución por CU (Confirmada)
| Plataforma | Casos de Uso |
|------------|--------------|
| **Flutter (Móvil)** | CU-01,02,03,05,12,13,14,15,16,19,20,21,22,25,26,30,31 |
| **Web (Solo Web)** | CU-04,06,07,08,09,10,11,17,18,23,24,27,28,29,32,33,34,35 |
| **Ambas** | CU-01,02,03,12,13,14,20,21,22,25,26,30,31 |

---

## Fases del Plan

### ✅ FASE 0: Design System Unificado (COMPLETADA)

**Completado:**
- [x] `design-tokens.json` en raíz del proyecto
- [x] `mobile/lib/app.dart` actualizado con nuevo color scheme (#FF8C00)
- [x] `mobile/lib/core/design/design_tokens.dart` con todas las clases (AppColors, AppSpacing, AppRadius, AppShadows, AppTypography, AppBreakpoints, AppZIndex)
- [x] `mobile/lib/core/design/app_theme.dart` - ThemeData light/dark completo usando design tokens
- [x] `mobile/lib/core/design/app_text_theme.dart` - TextTheme con GoogleFonts (Inter + Geist)
- [x] `mobile/lib/core/design/app_color_scheme.dart` - ColorScheme light/dark
- [x] Verificar `frontend/src/styles/design-system.css` consistencia con JSON

---

### ✅ FASE 1: Flutter Shared UI Library (4-5 días) (COMPLETADA)

**Ubicación:** `mobile/lib/shared/widgets/`

**Componentes a crear:**
| Archivo | Componente | Referencia Stitch |
|---------|------------|-------------------|
| `app_button.dart` | AppButton (variant, size, loading, icon) | ButtonProps |
| `app_text_field.dart` | AppTextField (label, error, hint, floatingLabel) | InputProps |
| `app_select.dart` | AppSelect (searchable, chips) | SelectProps |
| `app_card.dart` | AppCard (image, title, actions, onTap) | CardProps |
| `app_badge.dart` | AppBadge (variant, dot, size) | BadgeProps |
| `app_chip.dart` | AppChip (selected, removable, onSelect) | ChipProps |
| `app_avatar.dart` | AppAvatar (image, fallback, size) | Stitch avatar |
| `app_data_table.dart` | AppDataTable (sort, pagination, mobile cards) | Admin tables |
| `app_tabs.dart` | AppTabs (lazy, keyboard nav) | PDP tabs |
| `app_stepper.dart` | AppStepper (steps, currentStep, onTap) | Checkout stepper |
| `app_modal.dart` | AppModal (title, actions, size) | Modals |
| `app_toast.dart` + `toast_service.dart` | Toast system | Toasts |
| `app_dropdown.dart` | AppDropdown (position, items) | User dropdown |
| `app_skeleton.dart` | AppSkeleton (text, card, avatar, image) | Skeletons |
| `app_empty_state.dart` | AppEmptyState (icon, title, action) | Empty states |
| `app_chip_selector.dart` | AppChipSelector (talla/color chips) | Size/Color chips |
| `app_bottom_nav.dart` | BottomNavigationBar (4-5 tabs) | Navegación global |
| `app_drawer.dart` | NavigationDrawer responsive | Drawer móvil |
| `app_scaffold.dart` | Scaffold global con bottom nav/drawer | Layout base |

**Barrel export:** `shared_widgets.dart`

---

### ✅ FASE 2: Flutter Navigation + Auth (2-3 días) (COMPLETADA)

**Routing:** `mobile/lib/core/routing/app_router.dart`
- Configurar go_router con todas las rutas
- Deep link handler para `fashionstore://fitting/:variantId`
- Guards de autenticación (Riverpod)

**Pantallas Auth:**
| Archivo | CU | Ruta |
|---------|-----|------|
| `features/auth/login_screen.dart` | CU-01 | `/auth/login` |
| `features/auth/register_screen.dart` | CU-01 | `/auth/register` |
| `features/auth/forgot_password_screen.dart` | CU-03 | `/auth/forgot` |
| `features/auth/reset_password_screen.dart` | CU-03 | `/auth/reset` |
| `features/auth/auth_controller.dart` | - | State management |

**Rutas principales a configurar:**
```dart
GoRoute(path: '/', redirect: (_,__) => '/catalog'),
GoRoute(path: '/catalog', builder: CatalogScreen),
GoRoute(path: '/catalog/:id', builder: ProductDetailScreen),
GoRoute(path: '/fitting/:variantId', builder: ArFittingScreen), // YA EXISTE
GoRoute(path: '/cart', builder: CartScreen),
GoRoute(path: '/checkout', builder: CheckoutScreen),
GoRoute(path: '/reservations', builder: ReservationsScreen),
GoRoute(path: '/profile', builder: ProfileScreen),
GoRoute(path: '/auth/login', builder: LoginScreen),
GoRoute(path: '/auth/register', builder: RegisterScreen),
GoRoute(path: '/auth/forgot', builder: ForgotPasswordScreen),
GoRoute(path: '/auth/reset', builder: ResetPasswordScreen),
GoRoute(path: '/admin', builder: AdminShell), // Solo si se decide mover admin a Flutter
GoRoute(path: '/branch', builder: BranchScreen),
GoRoute(path: '/pos', builder: POSScreen),
```

**Deep Links Android/iOS:**
- `android/app/src/main/AndroidManifest.xml` - intent-filter `fashionstore://`
- `ios/Runner/Info.plist` - CFBundleURLSchemes `fashionstore`

---

### ✅ FASE 3: Flutter Catálogo + Detalle + AR (4-5 días) (COMPLETADA 21/09/2026)

**Estructura:** `mobile/lib/features/catalog/`

| Archivo | CU | Descripción |
|---------|-----|-------------|
| `catalog_screen.dart` | CU-12,13,14 | Lista con sidebar filtros, grid responsive, skeletons |
| `product_detail_screen.dart` | CU-12,13,19,30 | Galería, chips talla/color, CTA sticky, tabs, recomendaciones |
| `catalog_controller.dart` | - | Riverpod state (productos, filtros, paginación) |
| `widgets/product_card.dart` | CU-12,13 | Card con badges, wishlist, quick-add, swatches |
| `widgets/filter_sidebar.dart` | CU-13 | Categorías, precio slider, tallas chips, colores swatches, rating |
| `widgets/filter_chips.dart` | CU-13 | Chips filtros activos + "Limpiar todos" |

**AR (Ya implementado - CU-19):**
- `features/ar_fitting/ar_fitting_screen.dart` ✅ EXISTE
- `features/ar_fitting/pose_detector.dart` ✅ EXISTE (MediaPipe Pose → `DetectedPose` hombros/caderas)
- `features/ar_fitting/garment_overlay_painter.dart` ✅ REESCRITO 21/09/2026: anclaje **automático** al cuadrilátero hombro izq→der→cadera der→izq
- ✅ Agregado: Fetch AR config desde backend (`GET /catalog/:id/ar-config`) — hecho 21/09/2026
- ✅ Reemplazados placeholders por prendas reales: `mobile/assets/images/garments/*.png` (camiseta, playera, hoodie, vestido, chaqueta, blusa) generadas como PNG transparentes (PIL, alpha). Selector de prenda por chips en `ArFittingScreen` (`_GarmentPicker`) y carga con `instantiateImageCodec`.
- Deep link back a web **N/A**: la web se redujo a Admin/Staff/POS/Landing (Fase 7); se usa enlace web→app `fashionstore://fitting/1` en el landing. **SIN** ajuste manual (pinch/arrastre) — decisión del dueño: solo anclaje automático.

---

### ✅ FASE 4: Flutter Carrito + Checkout + Pagos (4-5 días) (COMPLETADA)

**Estructura:** `mobile/lib/features/cart/`

| Archivo | CU | Descripción |
|---------|-----|-------------|
| `cart_screen.dart` | CU-20 | 70/30 grid, items con stepper, swipe-to-delete |
| `checkout_screen.dart` | CU-20,25 | Stepper 4 pasos: Cesta → Envío → Pago → Confirmación |
| `cart_controller.dart` | - | Riverpod state (items, totales, cupón) |
| `widgets/cart_item.dart` | CU-20 | Imagen, variante chips, qty stepper 40px, subtotal |
| `widgets/order_summary.dart` | CU-20,25 | Subtotal, envío, cupón input, total, CTA |
| `widgets/checkout_stepper.dart` | CU-20,25 | 4 pasos con validación |

---

### ✅ FASE 5: Flutter Reservas + Perfil + Notificaciones (3-4 días) (COMPLETADA 21/09/2026)

**Notas de cierre Fase 5:**
- Notificaciones: `notifications_screen.dart` conectado a `GET /notifications?limit=` + `PATCH /notifications/:id/read` + marcar todas (via `ApiClient.getList/patch`); badge/campana en navbar web (`NotificationsComponent`) + página `/notifications` (web). `flutter analyze` sin issues + tests en verde.

**Estructura:** `mobile/lib/features/reservations/`, `mobile/lib/features/profile/`

| Archivo | CU | Ruta |
|---------|-----|------|
| `reservations_screen.dart` | CU-15,16 | `/reservations` - Lista con filtros, chips, timeline |
| `reservation_detail_screen.dart` | CU-15,16 | `/reservations/:id` - Items, historial, comprobante |
| `profile_screen.dart` | **CU-05 Solo Móvil** | `/profile` - Avatar, tabs (Datos/Direcciones/Pedidos/Puntos/Seguridad) |
| `notifications_screen.dart` | CU-21 | `/notifications` - Push + In-app |
| `purchase_history_screen.dart` | CU-22 | `/profile/orders` - Tabla filtrable, expandible |

---

### ✅ FASE 6: Flutter IA Features (2-3 días) (COMPLETADA)

| Archivo | CU | Ruta |
|---------|-----|------|
| `recommendations_screen.dart` | CU-30 | `/recommendations` - Grid personalizado |
| `ai_chat_screen.dart` | CU-31 | `/ai/chat` - Streaming chat con Ollama |

---

### ✅ FASE 7: Web Admin (Angular) - Solo Web (5-6 días) (COMPLETADA 21/09/2026)

**Mantener solo lo que CU dicen "Solo Web":**

| Módulo | CU | Rutas Angular |
|--------|-----|---------------|
| Auth Admin/Staff | CU-01,02,03 | `/auth/*` (guards por rol) |
| Usuarios & Roles | CU-04 | `/admin/users` |
| Catálogo Admin | CU-06,07,08,09,10,11 | `/admin/catalog/*` |
| Gestión Productos | CU-07 | `/admin/products` |
| Staff Sucursal | CU-17,18 | `/staff/reservations` |
| POS (Cajero) | CU-23,24 | `/pos` |
| Inventario | CU-27,28,29 | `/admin/inventory` |
| Reportes IA | CU-32 | `/admin/reports/ai` |
| Reportes Admin | CU-33,34,35 | `/admin/reports/*` |
| Landing SEO | - | `/` |

**Eliminar de Angular (mover a Flutter):**
- Catálogo público, Auth cliente, Carrito, Checkout, Perfil, Reservas, IA Cliente

**Nota del estado (HECHO 21/09/2026):**
- `app.routes.ts` reconstruido: `/` → Landing SEO, `/auth` (login/forgot/reset, sin register), `/admin`, `/staff`, `/pos`; guards `AuthGuard` + `RoleGuard` (lee `data.roles`; roles ADMIN/MANAGER para `/admin`).
- `AuthService` decodifica JWT: `roles()`, `hasAnyRole()`, `isStaff()`, `homeRoute()` (login navega según rol).
- Eliminadas features de cliente: `catalog`, `cart`, `profile`, `reservations`, `branch` (inventario movido a admin) y `register.component.ts`.
- Nuevos: `features/landing/`, `features/admin/` (admin-shell + users|catalog|products|inventory|reports|ai-reports), `features/staff/` (staff-shell + reservations CU-17/18 mediante `GET /reservations` + `PATCH /reservations/:id/status` con transiciones PENDING→PREPARED→IN_TRIAL→COMPLETED).
- Reportes: `/reports/indicators|consolidated|sales-by-period|top-products|low-stock|inventory-turnover|audit-log` (CU-33/34/35) y POST `/ai/reports/generate` + `/ai/reports/explain` (CU-32).
- `index.html` con meta tags SEO; `vercel.json` intacto; `ng build` OK.

---

### ✅ FASE 8: Integración + Deep Links + Deploy (2-3 días)

> **Decisión del dueño:** el APK es **solo para el celular por side-loading** (NO se publica en Play Store); **Firebase/FCM se omite** (no hay credenciales `google-services.json` / VAPID, igual que el TODO). Después de esta fase se hace el **redeploy a Vercel** (commit + push a GitHub, auto-deploy).

| Tarea | Detalle | Estado |
|-------|---------|--------|
| Deep links bidireccionales | `fashionstore://fitting/123` → apertura del probador virtual | ✅ **HECHO 21/09/2026**: intent-filter `fashionstore://fitting` en `AndroidManifest.xml` (acción VIEW, BROWSABLE); la ruta `/fitting/{variantId}` ya existe en GoRouter (`ArFittingRoutes`). Lado web: botón "Abrir probador virtual en la app" (`class="btn btn-outline"`) en el landing con `href="fashionstore://fitting/1"`. Nota: el `https://web/cart?add=123` dejó de existir porque la web se redujo a Admin/Staff/POS/Landing en Fase 7; se reemplazó por el enlace web→app. |
| Push notifications | FCM (Flutter) + VAPID (Web) | ⏭️ **OMITIDO** (sin proyecto Firebase/`google-services.json`; no se publica en Play Store). Documentar en `TODO.md`. |
| AR Config endpoint | `GET /api/v1/catalog/:id/ar-config` en backend | ✅ **HECHO 21/09/2026**: creado `ArConfigRead`/`ArVariantRead` en `backend/app/schemas/catalog.py`, `catalog_service.get_ar_config()` y ruta en `routes_catalog.py`. Consumido por `ArFittingScreen` (`_loadArConfig()`): muestra el nombre real de la prenda en el overlay. `ruff` + import OK. |
| Build APK/AAB | `flutter build apk --release` / `flutter build appbundle` | ✅ **HECHO 21/09/2026** (REGENERADO tras AR real ✓, APK 16:22, 94.3 MB): `app-release.apk` en `mobile/build/app/outputs/flutter-apk/`. NDK 28.2.13676358; fixes en `android/gradle.properties` (`kotlin.incremental=false`, `kotlin.compiler.execution.strategy=in-process`) y `android/build.gradle.kts` (`compileOnly androidx.concurrent:concurrent-futures:1.2.0`). `flutter analyze` sin issues + **8 tests en verde** (incluye 3 de `garment_overlay_painter_test.dart`). |
| Play Store | Screenshots, metadata, release tracks | ⏭️ **CANCELADO** por decisión del dueño (solo APK para el celular, no se publica). |
| Angular PWA | `ng add @angular/pwa` para Admin | ✅ **HECHO 21/09/2026**: `ng add @angular/pwa@18.2.21` (ngsw-config.json, `public/manifest.webmanifest`, iconos 72‑512px). Se ajustó: manifest con paleta `#FF8C00`/`#FFF3E0` y nombre "FashionStore"; `theme-color` duplicado eliminado de `index.html`; `angular.json` assets incluyen `public/manifest.webmanifest` + `public/icons/*` (el builder `application` de Angular 18 no copió `public/` solo). `ng build --configuration production` OK, `ngsw.json` generado en `dist`. |
| CI/CD | GitHub Actions para ambos | ✅ **HECHO 21/09/2026**: `.github/workflows/ci.yml` con 3 jobs: backend (ruff + pytest con servicio Postgres pgvector/pg16), frontend (`npm ci` + `ng build`), mobile (`flutter analyze` + `flutter test`). |

---

## Endpoints Backend Necesarios (Verificar Disponibilidad)

| Endpoint | CU | Estado |
|----------|-----|--------|
| `GET /catalog?page=&size=&search=&category_id=` | CU-12,13 | Verificar |
| `GET /catalog/categories` | CU-13 | Verificar |
| `GET /catalog/:id` | CU-12,19 | Verificar |
| `GET /catalog/:id/ar-config` | CU-19 | ✅ **HECHO 21/09/2026** |
| `POST /auth/login` | CU-01 | Verificar |
| `POST /auth/register` | CU-01 | Verificar |
| `POST /auth/forgot-password` | CU-03 | Verificar |
| `POST /auth/reset-password` | CU-03 | Verificar |
| `GET /cart` | CU-20 | Verificar |
| `POST /cart/items` | CU-20 | Verificar |
| `PATCH /cart/items/:variantId` | CU-20 | Verificar |
| `DELETE /cart/items/:variantId` | CU-20 | Verificar |
| `POST /cart/checkout` | CU-20 | Verificar |
| `POST /cart/purchase` | CU-25 | Verificar |
| `GET /reservations/me` | CU-16 | Verificar |
| `POST /reservations` | CU-15 | Verificar |
| `PATCH /reservations/:id/status` | CU-16 | Verificar |
| `GET /clients/me` | CU-05 | Verificar |
| `PATCH /clients/me` | CU-05 | Verificar |
| `GET /ai/recommendations` | CU-30 | Verificar |
| `POST /ai/chat` | CU-31 | Verificar |
| `GET /ai/recommendations/trending` | CU-30 | Verificar |

---

## Próximo Paso Inmediato

**Crear `mobile/lib/core/design/app_theme.dart`** con:

```dart
// ThemeData lightTheme y darkTheme usando:
// - AppColors (light/dark variants)
// - AppTypography (GoogleFonts.inter + Geist)
// - AppSpacing, AppRadius, AppShadows
// - ColorScheme.fromSeed(seedColor: AppColors.primary)
// - Material3: true
```

---

## Comandos Útiles para Continuar

```bash
# Verificar estructura móvil
find mobile/lib -type f -name "*.dart" | head -50

# Verificar dependencias Flutter
cd mobile && flutter pub get

# Verificar análisis
cd mobile && flutter analyze

# Ejecutar tests
cd mobile && flutter test
```

---

## Notas para el Próximo Agente

1. **Design tokens:** Ya existe `design-tokens.json` en raíz y `design_tokens.dart` en Flutter. Úsalos como única fuente de verdad.
2. **Stitch references:** Todos los mockups están en `stitch_fashionstore_design_system_redesign/` con `code.html` y `screen.png` por pantalla.
3. **CU-19 (AR):** Implementado y completo en `mobile/lib/features/ar_fitting/` (pantalla + `PoseService` + `GarmentOverlayPainter` con anclaje automático por hombros/caderas, prendas PNG en `assets/images/garments/`, selector de prendas, consume `/catalog/:id/ar-config`). NO lleva ajuste manual (decisión del dueño).
4. **Email real:** `notification_service.notify()` envía email real via Gmail SMTP (`smtplib`, STARTTLS/587) solo si `settings.smtp_password` está configurado; si no, loguea `[email-mock]`. Falta la App Password de Gmail del dueño para `SMTP_USER=sonclargod@gmail.com` (`SMTP_PASSWORD`, `MAIL_FROM` en `backend/.env` + vars de Render declaradas en `render.yaml`).
5. **BD demo:** `backend/scripts/seed.py` idempotente. Cliente demo con email real: `sonclargod@gmail.com` / `Client123!`. También existe `client@fashionstore.dev`/`Client123!` (usado por fixtures de tests). 6 usuarios, 2 sucursales, 10 prendas, promoción, 3 reservas demo, 1 venta PAID. La constraint única `uq_product_embeddings_variant_id` y el índice ivfflat fueron restaurados en la migración `62fce272acff` (bug de autogeneración).
6. **Backend:** Verificar endpoints antes de bloquear features Flutter.
7. **Distribución CU:** Respeta estrictamente la tabla de distribución - no dupliques funcionalidad entre plataformas.
8. **Shared UI:** Crea componentes genéricos y reutilizables, no pantallas completas en shared.

---

**Última actualización:** 21/09/2026
**Estado:** ✅ Fases 0-8 completas. Pendiente: probar APK en dispositivo físico + redeploy Vercel + App Password de Gmail.