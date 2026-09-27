# FASHIONSTORE — Web Cliente (PC) · Estado del Plan

Fecha: 2026-09-22
Propósito: Hacer funcionales TODOS los casos de uso de **cliente (A1)** en la **web de PC** según `SI2 - 1erParcial - G33 (1).md`.

---

## 📋 Mapa Casos de Uso (A1 Cliente) → Web

| CU | Caso de uso | Ruta Web | Componente | Estado |
|----|-------------|----------|------------|--------|
| CU-01 | Iniciar sesión | `/auth/login` | `features/auth/login.component.ts` | ✅ Existente |
| CU-02 | Cerrar sesión | botón en shell | `client-shell` `logout()` | ✅ |
| CU-03 | Recuperar contraseña | `/auth/forgot-password` · `/auth/reset-password` | auth routes | ✅ Existente |
| CU-05 | Registrar y gestionar perfil | `/client/profile` → `PATCH /clients/me` | `client/profile.component.ts` | ✅ Nuevo |
| CU-12 | Consultar catálogo | `/client/catalog` → `GET /catalog` | `client/catalog.component.ts` | ✅ Nuevo |
| CU-13 | Buscar y filtrar prendas | `/client/catalog` (search + categoría + sucursal + orden) | `client/catalog.component.ts` | ✅ Nuevo |
| CU-14 | Consultar disponibilidad por sucursal | `/client/catalog/:id` selector de sucursal → `branch_id` | `client/product-detail.component.ts` | ✅ Nuevo |
| CU-15 | Gestionar reserva de múltiples prendas | botón "Reservar" en detalle → `POST /reservations` | `client/product-detail.component.ts` + listado | ✅ Nuevo |
| CU-16 | Consultar y cancelar reservas | `/client/reservations` + `/client/reservations/:id` → `GET /reservations/me`, `PATCH /status=cancelled` | `client/reservations.component.ts` · `reservation-detail.component.ts` | ✅ Nuevo |
| CU-19 | Vestidor virtual (AR) | **Solo móvil** (requiere cámara) — no aplica en PC | — | ⛔ N/A (móvil) |
| CU-20 | Gestionar carrito | `/client/cart` → `GET/POST/PATCH/DELETE /cart` | `client/cart.component.ts` | ✅ Nuevo |
| CU-21 | Comprar plataforma web | `/client/checkout` → `POST /cart/purchase` | `client/checkout.component.ts` | ✅ Nuevo |
| CU-22 | Consultar historial de compras | `/client/history` → `GET /history` | `client/purchase-history.component.ts` | ✅ Nuevo |
| CU-25 | Procesar pago electrónico | Paso de pago en checkout (card/QR/transfer, simulado) | `client/checkout.component.ts` | ✅ Nuevo |
| CU-26 | Consultar comprobantes y compras | Modal comprobante en historial → `GET /receipts/{id}` · `GET /sales/{id}` | `client/purchase-history.component.ts` | ✅ Nuevo |
| CU-30 | Recomendar productos mediante IA | `/client/recommendations` → `GET /ai/recommendations` (fallback trending) | `client/recommendations.component.ts` | ✅ Nuevo |
| CU-31 | Asistir al cliente mediante IA | `/client/chat` → `POST /ai/chat` | `client/chat.component.ts` | ✅ Nuevo |
| — | Notificaciones | `/client/notifications` → `GET /notifications` · `PATCH /{id}/read` | `client/notifications.component.ts` | ✅ Nuevo |

---

## ✅ COMPLETADO

### Infraestructura y rutas
- `core/auth/auth.service.ts` → `homeRoute()` ahora envía a **CLIENT** a `/client/catalog`.
- `app.routes.ts` → nueva ruta raíz `/client` (lazy `CLIENT_ROUTES`, AuthGuard).
- `features/landing/landing.component.ts` → botón **"Tienda en línea"** → `/client/catalog`.
- `features/client/client.routes.ts` → 12 rutas hijas bajo el shell.

### Capa de servicios
- `features/client/client.service.ts` → servicio centralizado `ClientService` con TODAS las llamadas API del cliente (catálogo, sucursales, carrito, reservas, checkout, historial, comprobantes, notificaciones, recomendaciones, chat, perfil).
- El **auth interceptor** existente (`core/interceptors/auth.interceptor.ts`) ya adjunta `Authorization: Bearer` a cada request → funciona para carrito/reservas/etc.

### Componentes (14 archivos en `features/client/`)
1. `client-shell.component.ts` — sidebar con nav completo (catálogo, reservas, carrito, IA recomendados, asistente, historial, notificaciones, perfil) + logout.
2. `catalog.component.ts` — CU-12/13: grid de productos, búsqueda, filtro por categoría, filtro por sucursal, ordenamiento, paginación.
3. `product-detail.component.ts` — CU-12 detalle, CU-14 selector de talla/color + disponibilidad por sucursal, CU-15 botón reservar, CU-20 agregar al carrito.
4. `cart.component.ts` — CU-20: listado, cambiar cantidad, eliminar, cupón, resumen (subtotal/envío/descuento/total).
5. `checkout.component.ts` — CU-21/25: pasos envío (o pickup) + método de pago (tarjeta/QR/transferencia, simulado) + `POST /cart/purchase`.
6. `reservations.component.ts` — CU-15/16: listado de mis reservas con estado, sucursal, código de recogida.
7. `reservation-detail.component.ts` — CU-16: detalle, timeline de estado, cancelar reserva (solo si pending/confirmed).
8. `profile.component.ts` — CU-05: ver/editar nombre, teléfono, fecha nacimiento; puntos; `PATCH /clients/me`.
9. `purchase-history.component.ts` — CU-22/26: historial + modal comprobante (fallback a detalle de venta).
10. `notifications.component.ts` — Notificaciones: listado, marcar leída/todas, íconos por tipo.
11. `recommendations.component.ts` — CU-30: recomendaciones IA (fallback a trending).
12. `chat.component.ts` — CU-31: asistente IA con burbujas y historial.
13. `client.routes.ts` — lazy routing.
14. `client-servicio` (service).

### Builds
- ✅ `ng build --configuration development` → **OK** (solo 1 warning NG8102, corregido).
- ✅ `ng build` (producción) → **OK**.
- ✅ `ng serve --port 4200` corriendo (Watch mode).

---

## 🔄 EN PROGRESO / PENDIENTE

1. **🌐 Verificar en navegador** (`http://localhost:4200`):
   - [ ] Login con `client@fashionstore.dev` / `Client123!` → debe redirigir a `/client/catalog`.
   - [ ] Catálogo mustra las prendas (backend Render `https://fashionstore-api-r4me.onrender.com/api/v1`).
   - [ ] Detalle: seleccionar talla/color → disponibilidad por sucursal.
   - [ ] Agregar al carrito → carrito → checkout → pago simulado.
   - [ ] Crear reserva → aparece en "Mis reservas" → cancelar.
   - [ ] Historial + comprobante.
   - [ ] Recomendados IA + chat IA.
   - [ ] Notificaciones.
   - [ ] Perfil (editar y guardar).

2. **🔍 Posibles ajustes según respuesta del backend real** (los formatos pueden variar):
   - Catálogo: responde `{items, total, pages, page, size}` o array → ya se maneja ambos.
   - Variantes en detalle: `size_name`/`color_name` vs `size`/`color` → ya se maneja ambos.
   - Precio: `min_price ?? base_price ?? price` → ya se maneja.

3. **📱 Recordatorio móvil**: `CU-19 Vestidor virtual` es **exclusivo móvil** (requiere cámara+AR). En PC no aplica según el documento.

4. **🚀 Desplegar** web (si se requiere): `ng build --configuration production` → subir `dist/fashionstore` (Netlify/Vercel/Render estático). El APK móvil ya está construido.

---

## 📁 ARCHIVOS CLAVE
- `SI2 - 1erParcial - G33 (1).md` — documento de casos de uso (fuente).
- `frontend/src/app/features/client/*.ts` — módulo cliente web (nuevo).
- `frontend/src/app/app.routes.ts`, `core/auth/auth.service.ts`, `features/landing/landing.component.ts` — modificados.
- `backend/app/api/v1/` — endpoints ya existentes (no modificados).
- Dev server: `http://localhost:4200` (proceso `ng.cmd serve`, PID 32100).
- Logs dev server: `C:\Users\Asus\AppData\Local\Temp\opencode\ngserve.log` y `ngserve-err.log`.