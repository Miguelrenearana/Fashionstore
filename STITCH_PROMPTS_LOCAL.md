# Stitch Prompts - FashionStore UI Redesign

> **IMPORTANTE:** Stitch es un chat interactivo. NO lee este archivo y ejecuta todo solo.
> Debes **copiar-pegar cada prompt uno a la vez** en el chat de Stitch.
> Entre prompts: **Exporta el proyecto** (Download ZIP / Push to GitHub) para no perder contexto si se acaban tokens.

---

## CONTEXTO INICIAL (Pega PRIMERO en Stitch)

```
Proyecto: FashionStore - E-commerce fashion Angular 18

STACK ACTUAL:
- Angular 18 + TypeScript + RxJS
- Componentes standalone con styles inline (CSS en @Component)
- Sin framework UI (ni Material, Tailwind, Bootstrap)
- 4 variables CSS globales básicas
- Backend: FastAPI en Render, BD: Neon (PostgreSQL)
- Deploy: Frontend Vercel, Backend Render

OBJETIVO: Rediseño completo UI/UX con design system coherente, mobile-first, accesible.

PALETA FIJA (NO CAMBIAR):
- Primary/CTA: #FF8C00 (naranja Amazon)
- Primary hover: #E67E00, light: #FFF3E0, dark: #CC7000
- Nav/Header: #1A2B3A (navy oscuro estilo Amazon)
- Background: #F5F7FA (gris azulado suave)
- Surface: #FFFFFF, Surface-alt: #F8FAFC
- Texto: #1E293B (slate-800), Secondary: #64748B, Muted: #94A3B8
- Success: #059669, Warning: #D97706, Error: #DC2626, Info: #0284C7
- Radius: 4/8/12px, Shadows: sm/md/lg, Transitions: 150/200ms
- Dark mode: soporte completo via prefers-color-scheme

INVENTARIO PANTALLAS (14 rutas):
PÚBLICAS: Login, Register, Forgot Password, Reset Password, Catalog List, Product Detail
USUARIO: Cart (2 cols, sticky summary, stepper checkout), Reservations, Profile (tabs)
ADMIN/STAFF: Admin (usuarios CRUD, catálogo grid CRUD, productos tabla editable), Branches (grid + inventario inline-edit), POS (kiosko 3 paneles)
LAYOUT: Navbar responsive (desktop horizontal, mobile drawer), User dropdown, Cart badge

OUTPUT ESPERADO: React + Tailwind + shadcn/ui patterns (adaptaré a Angular después)
```

---

## PROMPT 1: Design System + Catálogo

```
Genera el DESIGN SYSTEM completo + 2 mockups interactivos.

STACK: React 18 + TypeScript + Tailwind CSS + shadcn/ui patterns

1. DESIGN SYSTEM TOKENS (JSON + CSS variables):
   - Colors (primary, semantic, neutrals, dark mode)
   - Spacing scale (--space-1 a --space-8)
   - Typography (Inter, scale xs-3xl)
   - Radius (sm/md/lg/full), Shadows (sm/md/lg/focus)
   - Z-index layers, Transitions

2. SHARED COMPONENTS (TypeScript interfaces + Tailwind):
   Button, Input, Select, Card, Badge, Avatar, Chip, Table, Tabs, Stepper, Navbar
   Props: variant, size, loading, disabled, error states, accessibility

3. MOCKUP 1 - /catalog (Product List):
   Desktop: Sidebar filtros colapsable (280px) + Grid responsive (4/3/2/1 cols)
   Toolbar: vista grid/lista toggle, sort select, products per page
   Skeleton loaders (6 cards), infinite scroll/pagination
   Empty state ilustrado + "Limpiar filtros"
   Mobile: filtros en bottom sheet, chips filtros activos, pull-to-refresh

4. MOCKUP 2 - /catalog/[id] (Product Detail):
   Layout: galería izquierda (thumbnails + zoom) + info derecha (sticky)
   Galería: thumbnails verticales, zoom on hover, fullscreen modal
   Variantes: chips visuales (talla/color) NO dropdown
   CTA sticky: "Agregar al carrito" + "Reservar en tienda"
   Tabs: Descripción | Especificaciones | Reseñas | Recomendaciones
   Badges: "AR disponible", "Pocos en stock", "Nuevo"
   Mobile: swipe galería, info en accordion, CTA sticky bottom

ESTÉTICA: Elegante, fashion, premium, confianza, limpio. Mobile-first.
ACCESIBILIDAD: WCAG AA, focus-visible, ARIA, skip links, reduced motion.
```

---

## PROMPT 2: Auth Pages (Después de aprobar Prompt 1)

```
Usando el design system aprobado, genera 4 páginas auth como mockups interactivos.

REUTILIZA: Todos los componentes shared del Prompt 1.

PÁGINAS:
1. /auth (Login) - Split screen desktop: izquierda branding/ilustración fashion, derecha formulario centrado max 420px
2. /auth/register - Mismo layout, más campos
3. /auth/forgot-password - Card centrada
4. /auth/reset-password - Card centrada

REQUISITOS POR PÁGINA:
- Floating labels en todos los inputs
- Password strength meter (solo register)
- Show/hide password toggle
- Validación inline en tiempo real
- Social login placeholders (Google, Apple - botones ghost)
- "Recordarme" checkbox (login)
- Estados: loading spinner en botón, error alert, success toast
- Mobile: full screen, keyboard-aware, sticky bottom CTA en formularios largos
- Dark mode: automático via design tokens
- Accesibilidad: labels, autocomplete, focus-visible, error announcements

FORMULARIOS:
- Login: email, password, forgot link, register link
- Register: email, password, first_name, last_name, phone (opcional), birth_date (opcional)
- Forgot: solo email
- Reset: token, new password, confirm password
```

---

## PROMPT 3: User Pages - Cart + Reservations + Profile

```
Genera 3 páginas de usuario usando el design system.

REUTILIZA: Todos los componentes shared.

1. /cart (Carrito)
   DESKTOP: 2-cols (70% items | 30% resumen sticky)
   - Items: imagen, nombre, variant chips, qty stepper (+/-), precio unitario, subtotal, delete
   - Resumen: subtotal, envío (calculado en checkout), cupón input, total
   - CTAs: "Reservar y recoger" (secondary) | "Comprar ahora" (primary)
   - Stepper checkout wizard: Datos → Envío → Pago → Confirmación
   MOBILE: Stack vertical, resumen en bottom sheet expandible, swipe-to-delete
   EMPTY: Ilustración + "Ir al catálogo" CTA

2. /reservations (Mis reservas)
   - Lista tarjetas: pickup_code (botón copiar), status badge, total, expira, tienda
   - Filtros: status chips, date range, store select
   - Detalle expandible: items, timeline historial estados, link comprobante
   - Empty state ilustrado

3. /profile (Mi perfil)
   DESKTOP: 2-cols (avatar + datos | tabs: Datos | Direcciones | Pedidos | Puntos | Seguridad)
   - Avatar: drag & drop upload, fallback initials
   - Floating labels, validación inline
   - Tab Pedidos: tabla filtrable/ordenable, fila expandible para detalle
   MOBILE: Segmented control tabs, avatar centrado
   - Seguridad: change password, 2FA placeholder
```

---

## PROMPT 4: Admin + Branch + POS (Staff Pages)

```
Genera 3 páginas staff/admin (desktop-first, mobile functional).

REUTILIZA: Todos los componentes shared.

1. /admin (Admin Panel - MÁS COMPLEJA)
   LAYOUT: Sidebar nav (Usuarios | Catálogo | Productos) + Main content
   - USUARIOS: DataTable (sort, filter, paginate), Create User modal, Roles como chips, "Vincular empleado" inline expandible
   - CATÁLOGO: Grid 6 cards (Tallas, Colores, Temporadas, Categorías, Colecciones, Proveedores) - cada una con Create modal + lista inline editable
   - PRODUCTOS: Tabla editable inline (nombre, precio, AR toggle, active toggle), acciones por fila (save, toggle, delete), paginación, búsqueda
   MOBILE: Read-only + FAB acciones críticas

2. /branch (Sucursales + Inventario)
   - Grid cards: nombre, ciudad, dirección, teléfono, acciones
   - Create store modal
   - Inventario: Select sucursal → Tabla inline-edit qty (+1/-1), filtros, export CSV
   MOBILE: Acordeón sucursales, inventario como cards

3. /pos (Punto de Venta - KIOSK MODE TABLET)
   LAYOUT: 3 paneles (Catálogo rápido | Ticket actual | Acciones pago)
   - Catálogo: Buscador + botones touch grandes (min 48x48px), filtros category chips
   - Ticket: Lista items, ajuste qty, subtotal línea, total running
   - Pago: Efectivo / Tarjeta / QR buttons, calculadora cambio
   - Fullscreen kiosk mode, flow imprimir recibo
   - Touch-friendly everywhere, no hover states
```

---

## PROMPT 5: Navbar Component (SOLO Componente, NO Página)

```
⚠️ IMPORTANTE: Genera **SOLO el componente Navbar reutilizable**.
- NO generar página /navbar
- NO generar routing
- SÍ: Componente `<Navbar />` que se importa en layout root (App.tsx)

ARCHIVO: `components/ui/Navbar.tsx`
EXPORT: `export function Navbar({ user, cartCount, isAdmin }: NavbarProps)`

PROPS INTERFACE:
interface NavbarProps {
  user?: { first_name: string; last_name: string; email: string } | null;
  cartCount: number;
  isAdmin: boolean;
}

DESKTOP (≥768px):
- Logo "FashionStore" + link a /catalog
- Nav links: Catálogo, Carrito, Reservas
- Search (opcional, placeholder)
- User avatar dropdown: Perfil, Pedidos, Admin (si isAdmin), Cerrar sesión
- Badge count en Carrito (cartCount)

MOBILE (<768px):
- Logo | Hamburger button (☰)
- Click → Drawer lateral derecho (300px, overlay backdrop)
- Drawer header: avatar + nombre/email del user
- Nav links apilados (touch-target 48px mínimo)
- Footer: botón "Cerrar sesión" (danger) o "Iniciar sesión" (primary)

ACCESIBILIDAD (OBLIGATORIO):
- Skip link "Saltar al contenido principal" (primer focus, href="#main-content")
- ARIA: role="navigation", aria-label="Navegación principal"
- Hamburger: aria-expanded, aria-controls="mobile-nav", aria-label="Abrir menú"
- Focus trap en drawer abierto
- ESC para cerrar drawer
- Focus visible en TODOS los elementos interactivos

ANIMACIONES:
- Drawer slide-in right (200ms ease)
- Overlay fade-in (150ms)
- Soporte prefers-reduced-motion

ESTILOS: Usar design tokens (--color-nav, --color-primary, etc.) + Tailwind
```

---

## FLUJO DE TRABAJO RECOMENDADO

```
1. Abre Stitch → New Chat
2. Pega CONTEXTO INICIAL → Enter
3. Pega PROMPT 1 → Enter → Itera visualmente hasta aprobar
4. EXPORT: Download ZIP / Push to GitHub
5. Nueva sesión / Nueva cuenta si tokens agotados → Import ZIP / Clone repo
6. Pega PROMPT 2 → Enter → Itera → Export
7. Repite: Prompt 3 → Export → Prompt 4 → Export → Prompt 5
```

---

## COMANDOS ÚTILES EN STITCH

| Qué necesitas | Escribe en chat |
|---------------|-----------------|
| Ver código de un componente | `"Show me the Button component code only"` |
| Exportar todo | `"Export as zip"` / `"Push to GitHub"` |
| Cambiar colores | `"Update design tokens: primary to #FF6B00, regenerate all components"` |
| Versión Angular | `"Convert Button to Angular standalone with @Input() signals"` |
| Solo Tailwind classes | `"Give me just the Tailwind classes for Card component"` |

---

## TOKENS PARA COPIAR RÁPIDO (JSON)

```json
{
  "colors": {
    "primary": "#FF8C00",
    "primaryHover": "#E67E00",
    "primaryLight": "#FFF3E0",
    "primaryDark": "#CC7000",
    "nav": "#1A2B3A",
    "navHover": "#243B4E",
    "bg": "#F5F7FA",
    "surface": "#FFFFFF",
    "surfaceAlt": "#F8FAFC",
    "text": "#1E293B",
    "textSecondary": "#64748B",
    "textMuted": "#94A3B8",
    "success": "#059669",
    "warning": "#D97706",
    "error": "#DC2626",
    "info": "#0284C7"
  },
  "radius": { "sm": "4px", "md": "8px", "lg": "12px", "full": "9999px" },
  "shadows": {
    "sm": "0 1px 2px rgba(15,23,42,0.05)",
    "md": "0 4px 6px rgba(15,23,42,0.07)",
    "lg": "0 10px 15px rgba(15,23,42,0.1)",
    "focus": "0 0 0 3px rgba(255,140,0,0.25)"
  },
  "spacing": { "1": "0.25rem", "2": "0.5rem", "3": "0.75rem", "4": "1rem", "5": "1.5rem", "6": "2rem", "8": "3rem" }
}
```

---

## NOTAS PARA ADAPTAR A ANGULAR DESPUÉS

| Stitch/React | Tu Angular |
|--------------|------------|
| Tailwind classes | Tus utilidades CSS (`.btn-primary`, `.card`, `.grid-cols-4`) |
| `useState` / `useSignal` | `signal()` / `computed()` |
| `onClick` | `(click)="handler()"` |
| `className={cn(...)}` | `[class]="{'btn-primary': true}"` o `[ngClass]` |
| `<Component prop={value} />` | `<app-component [prop]="value" />` |
| `interface Props` | `@Input() prop = input<Type>()` |

---

*Archivo generado localmente - No subir al repo*