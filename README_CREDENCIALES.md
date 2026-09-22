# Credenciales de Prueba - FashionStore

## URLs de la API
- **Base**: `https://fashionstore-api-r4me.onrender.com`
- **Registrar usuario**: `POST /api/v1/auth/register`
- **Iniciar sesión**: `POST /api/v1/auth/login`

## Cuentas Creadas (ya registradas)

Si ya ejecutaste el registro anteriormente, estas cuentas existen. Si no, ejecuta los comandos curl a continuación.

### 1. Admin (Panel completo)
- **Email**: `admin@fashionstore.test`
- **Contraseña**: `TestPass123!`
- **Permisos**: Todos los CUs (1-35)

### 2. Manager (Gestión de tienda)
- **Email**: `manager@fashionstore.test`
- **Contraseña**: `TestPass123!`
- **Permisos**: CU-06, CU-07, CU-08, CU-09, CU-10, CU-17, CU-18, CU-27, CU-28, CU-29, CU-32, CU-33, CU-34, CU-35

### 3. Staff (Personal de tienda)
- **Email**: `staff@fashionstore.test`
- **Contraseña**: `TestPass123!`
- **Permisos**: CU-17, CU-18 (reservas staff)

### 4. Cliente (Móvil / Web)
- **Email**: `cliente@fashionstore.test`
- **Contraseña**: `TestPass123!`
- **Permisos**: Catálogo, carrito, perfil, AR Fitting

## Comando curl para registrarlos (si no existen)

Ejecuta cada uno en una terminal (PowerShell, CMD o Linux):

```powershell
# 1. Registrar Admin
curl -X POST "https://fashionstore-api-r4me.onrender.com/api/v1/auth/register" `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@fashionstore.test","password":"TestPass123!","first_name":"Admin","last_name":"User","phone":"+525512345678"}'

# 2. Registrar Manager
curl -X POST "https://fashionstore-api-r4me.onrender.com/api/v1/auth/register" `
  -H "Content-Type: application/json" `
  -d '{"email":"manager@fashionstore.test","password":"TestPass123!","first_name":"Manager","last_name":"User","phone":"+525512345678"}'

# 3. Registrar Staff
curl -X POST "https://fashionstore-api-r4me.onrender.com/api/v1/auth/register" `
  -H "Content-Type: application/json" `
  -d '{"email":"staff@fashionstore.test","password":"TestPass123!","first_name":"Staff","last_name":"User","phone":"+525512345678"}'

# 4. Registrar Cliente
curl -X POST "https://fashionstore-api-r4me.onrender.com/api/v1/auth/register" `
  -H "Content-Type: application/json" `
  -d '{"email":"cliente@fashionstore.test","password":"TestPass123!","first_name":"Cliente","last_name":"User","phone":"+525512345678"}'
```

## Comandos de login (después de registrar)

```powershell
# Iniciar sesión como admin (obtener JWT)
curl -X POST "https://fashionstore-api-r4me.onrender.com/api/v1/auth/login" `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@fashionstore.test","password":"TestPass123!"}'
```

El response te dará un `access_token` que puedes usar para probar los endpoints protegidos.

## Endpoints importantes para probar

### Web (Admin/Staff):
- `GET /api/v1/admin/users` - Listar usuarios (Admin)
- `GET /api/v1/admin/products` - Productos (Admin)
- `POST /api/v1/pos/venta` - Nueva venta (Staff/POS)

### Mobile (Cliente):
- `GET /api/v1/catalog` - Catálogo de productos
- `POST /api/v1/cart/items` - Agregar al carrito
- `GET /api/v1/profile` - Perfil del cliente

## Nota importante
El sistema usa `PAYMENT_GATEWAY=mock`, por lo que los pagos simularán automáticamente sin necesidad de tarjetas reales.

## Si ya tenías cuentas registradas anteriormente
Intenta hacer login con los emails y contraseñas arriba. Si el sistema dice "invalid credentials", significa que las cuentas fueron eliminadas o la base de datos se reinició.