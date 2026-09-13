# TODO — Pendientes del proyecto

Formato:
- 🔴 infraestructura/credenciales (bloquea deploy, no el desarrollo local)
- 🟡 técnicos/calidad
- 🟢 backlog por ciclo

> **Ciclo 3 queda congelado.** No registramos tareas para él hasta que el
> dueño del proyecto lo retome.

---

## 🔴 Infraestructura pendiente (usuario)

- [x] **Neon**: proyecto creado y conectado → `backend/.env` con `DATABASE_URL` (directa,
  `sslmode=require`). Esquema aplicado con `alembic upgrade head` (38 tablas + `vector` 0.8.6
  + índice ivfflat) y seed cargado. **El backend corre en localhost apuntando a esta BD.**
- [ ] **Render**: desplegar `backend/` desde `render.yaml` (Docker). Ajustar variables de
  entorno y health check `/health`.
- [ ] **Vercel**: importar `frontend/`, usar rewrites SPA de `vercel.json`.
- [ ] **Firebase**: crear proyecto para **App Distribution** (Android/iOS).
- [ ] **GitHub**: subir el repo renombrado (origin) y `git pull` al iniciar para sincronizar.
- [ ] **PagosNet (sandbox)**: crear cuenta en modo testing (gratis) → obtener
  `PAGOSNET_API_KEY` y `PAGOSNET_ENCRYPTION_KEY` → cargar en `.env`.
  *No es tarea de Ciclo 3; se habilita solo cuando lo pida el dueño.*

## 🟡 Técnicos

- [x] Generar **migración Alembic inicial** (todas las tablas) + `scripts/init_extensions.sql`.
- [ ] AR: hoy se usan **placeholders PNG** en `mobile/assets/images/placeholders/`; sustituir
  por assets reales cuando existan.
- [ ] Email: actualmente **log/consola**; conectar SendGrid/Mailgun en **Ciclo 2** (RULES §8).

## 🟢 Backlog

### Ciclo 1 (completado — tag `v1.0.0-ciclo1`)
- [x] Base del backend (FastAPI + core + esquemas).
- [x] CU-01 Iniciar sesión (+ UML/paquetes)
- [x] CU-02 Cerrar sesión (+ UML)
- [x] CU-04 Gestionar usuarios y roles (+ UML)
- [x] CU-06 Gestionar ciudades y sucursales (+ UML)
- [x] CU-07 Gestionar productos de ropa (+ UML; actualizar/eliminar prendas en Ciclo 2)
- [x] CU-12 Consultar catálogo (+ UML)
- [x] CU-13 Buscar y filtrar prendas (+ UML)
- [x] CU-14 Consultar disponibilidad por sucursal (+ UML)
- [x] CU-15 Gestionar reserva de múltiples prendas (+ UML)
- [x] CU-17 Gestión de recepción y atención de reservas (+ UML; listado de reservas por staff pendiente)
- [x] UML (secuencia + comunicación) por cada CU implementado, agrupado por paquete.
- [x] Tabla de caso de uso por CU (formato RULES §7).

> Nota: diagramas y tablas usan la **numeración oficial** del proyecto
> (`docs/uml/ciclo1/{autenticacion-usuarios,gestion-catalogo,reservas}/CU-XX/`).
> Pagos e inventario/ajustes y recomendaciones IA se evalúan en Ciclo 2.

### Ciclo 2
- [ ] CU-03 Gestión de clientes
- [ ] CU-05 Gestión de catálogo (categorías/colecciones)
- [ ] CU-08 Gestión de promociones
- [ ] CU-09 Carrito de compras
- [ ] CU-10 Venta en punto de venta (POS)
- [ ] CU-16 Facturación / comprobantes
- [ ] CU-18 Recepción de producto (proveedores)
- [ ] CU-19 Gestión de proveedores
- [ ] CU-20 Notificaciones
- [ ] CU-21 Historial de navegación / seguimiento
- [ ] CU-23 Cierre de caja
- [ ] CU-24 Reportes de ventas
- [ ] Email → SendGrid/Mailgun (item 🟡).