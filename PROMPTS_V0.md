# PROMPTS PARA v0.dev - FashionStore UI Redesign

## 📋 Cómo usar:
1. Entra a **https://v0.dev** → Sign in con GitHub
2. Click **"New Chat"**
3. Pega **Prompt 1** → Enter → Itera visualmente
4. Cuando apruebes → Pega **Prompt 2** → etc.

---

## PROMPT 1: Design System + Catálogo (Pega PRIMERO)

```
Tengo un proyecto Angular 18 (standalone, inline styles) de e-commerce fashion "FashionStore". 

STACK ACTUAL:
- Angular 18 + TypeScript + RxJS
- Componentes standalone con styles inline
- Sin framework UI (ni Material, Tailwind, Bootstrap)
- 4 variables CSS globales básicas
- Backend: FastAPI en Render, BD: Neon
- Deploy: Frontend Vercel, Backend Render

NUEVA PALETA APROBADA (estilo Amazon/Ubuy/Elgentos):
- Primary/CTA: #FF8C00 (naranja Amazon)
- Primary hover: #E67E00, light: #FFF3E0, dark: #CC7000
- Nav/Header: #1A2B3A (navy oscuro estilo Amazon)
- Background: #F5F7FA (gris azulado suave)
- Surface: #FFFFFF, Surface alt: #F8FAFC
- Texto: #1E293B (slate 800), Secondary: #64748B, Muted: #94A3B8
- Success: #059669, Warning: #D97706, Error: #DC2626, Info: #0284C7
- Spacing scale: --space-1 a --space-8
- Radius: 4/8/12px, Shadows: sm/md/lg, Transitions: 150/200ms

INVENTARIO DE PANTALLAS (14 rutas):
PÚBLICAS: Login, Register, Forgot Password, Reset Password, Catalog List, Product Detail
USUARIO: Cart (2 cols, sticky summary, stepper checkout), Reservations, Profile (tabs)
ADMIN/STAFF: Admin (usuarios CRUD, catálogo grid CRUD, productos tabla editable), Branches (grid + inventario inline-edit), POS (kiosko 3 paneles)
LAYOUT: Navbar responsive (desktop horizontal, mobile drawer), User dropdown, Cart badge

DAME EN ESTE ORDEN:
1. ESPECIFICACIÓN COMPLETA DEL DESIGN SYSTEM (tokens JSON/CSS con todas las escalas: color, spacing, typo, shadows, radius, z-index, dark mode)
2. LISTA DE COMPONENTES SHARED con props/inputs: Button, Input, Select, Card, Badge, Spinner, EmptyState, Toast, Modal, Avatar, Chip, Table, Tabs, Stepper, Navbar
3. MOCKUP INTERACTIVO DE /catalog (lista con sidebar filtros colapsable, grid responsive 4/3/2/1 cols, skeleton loaders, vista grid/lista toggle, empty state)
4. MOCKUP INTERACTIVO DE /catalog/:id (detalle: galería thumbnails + zoom, variantes como chips visuales, CTA sticky, tabs descripción/especs/reviews, recomendaciones)

ESTÉTICA: Elegante, fashion, premium, confianza, limpio. Mobile-first.
OUTPUT: Design system tokens + componentes shared (Angular standalone + CSS/Tailwind patterns) + 2 mockups interactivos.
```

---

## PROMPT 2: Pantallas Auth (Pega DESPUÉS de aprobar Prompt 1)

```
Basado en el design system aprobado, dame mockups interactivos para las 4 pantallas AUTH:

1. /auth (Login)
2. /auth/register  
3. /auth/forgot-password
4. /auth/reset-password

REQUISITOS:
- Split screen desktop (izq: branding/ilustración fashion, der: formulario centrado max 420px)
- Mobile full screen, formulario 100% viewport
- Floating labels en inputs
- Password strength meter en register
- Show/hide password toggle
- Validación inline en tiempo real
- Social login placeholders (Google, Apple)
- "Recordarme" checkbox
- Estados: loading, error, success
- Accesibilidad: labels asociados, autocomplete, focus visible
- Dark mode support
- Usar componentes shared del Prompt 1 (Button, Input, Card, etc.)
```

---

## PROMPT 3: Usuario - Cart + Checkout + Reservations + Profile

```
Mockups interactivos para pantallas USUARIO (mobile-first):

1. /cart (Carrito)
   - Desktop: 2 cols (70% items, 30% resumen sticky con subtotal/envío/descuento/total)
   - Item: imagen, nombre, variante chips, qty stepper, precio, subtotal, delete
   - Cupón input + "Aplicar"
   - CTA: "Reservar y recoger" (secondary) | "Comprar ahora" (primary)
   - Stepper checkout wizard: Datos → Envío → Pago → Confirmación
   - Mobile: stack vertical, resumen bottom sheet expandible, swipe-to-delete

2. /reservations (Mis reservas)
   - Lista tarjetas: pickup_code (copiable), status badge, total, expira, tienda
   - Filtros: status, fecha, tienda
   - Detalle expandible: items, historial estados, comprobante
   - Empty state ilustrado

3. /profile (Mi perfil)
   - Desktop: 2 cols (avatar+datos | tabs: Datos/Direcciones/Pedidos/Puntos/Seguridad)
   - Avatar editable drag&drop, floating labels, validación inline
   - Tab Pedidos: tabla filtrable, expandible a detalle
   - Mobile: tabs segmented control, avatar centrado
```

---

## PROMPT 4: Admin + Branch + POS (Las más complejas)

```
Mockups para pantallas ADMIN/STAFF (desktop-first, mobile functional):

1. /admin (Panel admin - MÁS COMPLEJA)
   - Sidebar navigation: Usuarios | Catálogo | Productos
   - Usuarios: tabla sortable/filtrable/paginable, crear usuario (modal), roles chips, vincular empleado (inline form expandible)
   - Catálogo: grid 6 cards (Tallas, Colores, Temporadas, Categorías, Colecciones, Proveedores) cada una con modal crear + lista inline editable
   - Productos: tabla editable inline (nombre, precio, AR, activo), acciones por fila, paginación, búsqueda
   - Mobile: versión readonly + FAB acciones críticas

2. /branch (Sucursales + Inventario)
   - Grid cards sucursales con acciones
   - Modal crear sucursal
   - Inventario: select sucursal → tabla inline-edit qty (+1/-1), filtros, export CSV
   - Mobile: acordeón sucursales, inventario en cards

3. /pos (Punto de venta - MODO KIOSKO TABLET)
   - 3 paneles: Catálogo rápido (buscador + grid botones grandes) | Ticket actual (items, totales) | Acciones pago
   - Botones touch-friendly ≥48px
   - Flujo: Agregar → Pago (efectivo/tarjeta/QR) → Imprimir
   - Fullscreen kiosk mode
```

---

## PROMPT 5: Navbar Global + Responsive

```
Navbar responsive completo usando design system:

DESKTOP (≥768px):
- Logo | Nav links (Catálogo, Carrito, Reservas) | Search (opcional) | User avatar dropdown
- Dropdown: Perfil, Pedidos, Admin (si staff), Cerrar sesión
- Badge count en Carrito

MOBILE (<768px):
- Logo | Hamburger → Drawer lateral (overlay + backdrop)
- Drawer: Nav links + User section (avatar, nombre, email) + Acciones (Perfil, Admin, Logout)
- Bottom sheet alternativo para nav principal

ACCESIBILIDAD:
- Skip to content link
- ARIA labels, roles, states
- Focus trap en drawer
- ESC para cerrar
- Focus visible en todos los elementos
```

---

## 🎯 Tips para mejores resultados en v0:

| Tip | Descripción |
|-----|-------------|
| **Un prompt a la vez** | v0 pierde contexto si pegas todo junto |
| **Itera visual** | "Haz el botón más grande", "Oscurece el primary", "Más spacing en cards" |
| **Pide código Angular** | "Dame el componente Button en Angular standalone con inputs tipados" |
| **Sube capturas** | Si tienes screenshots de tu app actual, súbelas con 📎 en v0 |
| **Guarda versiones** | Cada chat es un "Project" en sidebar izquierdo |
| **Exporta código** | Click "Get Code" en cada componente → Adapta a tu Angular |

---

## 📁 Archivos creados en tu repo (para referencia):

```
frontend/src/styles/
├── design-system.css    # Tokens completos (colores, spacing, typo, shadows, dark mode)
├── reset.css            # Normalize + base styles + accessibility
└── utilities.css        # Clases utilitarias: .btn, .input, .card, .badge, .grid, .container, etc.

Componentes actualizados:
├── navbar.component.ts     # Responsive, mobile drawer, user dropdown
├── catalog.component.ts    # Sidebar filtros, grid responsive, skeleton loaders
├── product-detail.component.ts  # Galería, chips variantes, CTA sticky, tabs
└── cart.component.ts       # 2 cols, sticky summary, stepper, mobile bottom sheet
```

---

## ✅ Próximos pasos sugeridos:

1. **Ejecuta prompts en v0.dev** en orden (1→5)
2. **Copia CSS/TSX generado** → Adapta a tus componentes Angular
3. **Remplaza inline styles** por clases del design system
4. **Haz deploy a Vercel** → Verifica en mobile/desktop
5. **Itera** con feedback real de usuarios