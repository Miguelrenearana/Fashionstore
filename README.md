# FashionStore - Plataforma Inteligente de Tienda de Ropa

Sistema de e-commerce completo para una tienda de moda online, desarrollado con arquitectura limpia y tecnologías modernas.

## 🏗️ Arquitectura

```
FashionStore/
├── src/
│   ├── FashionStore.Api/          # API REST (ASP.NET Core 8)
│   ├── FashionStore.Core/         # Lógica de negocio, entidades, interfaces
│   ├── FashionStore.Infrastructure/ # Acceso a datos, repositorios, EF Core
│   └── FashionStore.Tests/        # Pruebas unitarias e integración
├── frontend/                      # SPA React + TypeScript + Vite
├── docker/                        # Configuración Docker
└── docs/                          # Documentación
```

## 🚀 Tecnologías

### Backend
- **ASP.NET Core 8** - Framework web
- **Entity Framework Core 8** - ORM
- **SQL Server** - Base de datos
- **MediatR** - Patrón Mediator/CQRS
- **Ardalis.Specification** - Patrón Specification
- **FluentValidation** - Validaciones
- **Serilog** - Logging
- **Swagger/OpenAPI** - Documentación API
- **JWT + Identity** - Autenticación/Autorización
- **AutoMapper** - Mapeo objeto-objeto

### Frontend
- **React 18** + **TypeScript**
- **Vite** - Build tool
- **React Router 6** - Enrutamiento
- **Tailwind CSS** - Estilos
- **Zustand** - Estado global
- **React Hook Form + Zod** - Formularios y validación
- **Axios** - Cliente HTTP
- **Lucide React** - Iconos

### DevOps
- **Docker + Docker Compose**
- **GitHub Actions** (CI/CD)

## 📋 Requisitos Previos

- .NET 8 SDK
- Node.js 20+
- Docker & Docker Compose (opcional)
- SQL Server (o usar contenedor Docker)

## ⚙️ Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y configura:

```bash
# Backend
ASPNETCORE_ENVIRONMENT=Development
ConnectionStrings__DefaultConnection=Server=localhost,1433;Database=FashionStore;User=sa;Password=YourStrong@Passw0rd;TrustServerCertificate=True;
Jwt__Key=your-super-secret-key-with-at-least-32-characters
Jwt__Issuer=FashionStore
Jwt__Audience=FashionStore.Client

# Frontend
VITE_API_URL=http://localhost:5000/api
```

### Con Docker (Recomendado)

```bash
cd docker
docker-compose up -d
```

La API estará en `http://localhost:5000` y el frontend en `http://localhost:5173`.

### Desarrollo Local

#### Backend
```bash
cd src/FashionStore.Api
dotnet restore
dotnet ef database update
dotnet run
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🗄️ Base de Datos

### Migraciones
```bash
# Crear migración
dotnet ef migrations add NombreMigracion -p src/FashionStore.Infrastructure -s src/FashionStore.Api

# Aplicar migraciones
dotnet ef database update -p src/FashionStore.Infrastructure -s src/FashionStore.Api
```

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
dotnet test

# Con cobertura
dotnet test --collect:"XPlat Code Coverage"
```

## 📦 Estructura de la API

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/products` | Listar productos (filtros, paginación) |
| GET | `/api/products/{id}` | Detalle de producto |
| GET | `/api/products/featured` | Productos destacados |
| GET | `/api/categories` | Listar categorías |
| GET | `/api/categories/{id}/products` | Productos por categoría |
| POST | `/api/auth/register` | Registro de usuario |
| POST | `/api/auth/login` | Inicio de sesión |
| GET | `/api/auth/me` | Usuario actual |
| GET | `/api/orders` | Historial de pedidos (auth) |
| POST | `/api/orders` | Crear pedido (auth) |
| GET | `/api/users/profile` | Perfil de usuario (auth) |

### Autenticación
Usa Bearer Token JWT en header: `Authorization: Bearer <token>`

## 🎨 Frontend - Páginas

- `/` - Home con hero, categorías, productos destacados
- `/productos` - Catálogo con filtros
- `/productos/:slug` - Detalle de producto
- `/carrito` - Carrito de compras
- `/checkout` - Proceso de pago
- `/login` / `/registro` - Autenticación
- `/perfil` - Perfil de usuario
- `/pedidos` - Historial de pedidos
- `/admin/*` - Panel de administración

## 📁 Scripts Útiles

```bash
# Backend
dotnet build                    # Compilar
dotnet run                      # Ejecutar
dotnet test                     # Tests
dotnet ef database update       # Aplicar migraciones

# Frontend
npm run dev                     # Desarrollo
npm run build                   # Producción
npm run lint                    # Linting
npm run preview                 # Preview build
```

## 📚 Documentación

- [API Docs (Swagger)](http://localhost:5000/swagger) - En desarrollo
- [Arquitectura](./docs/architecture.md)
- [Base de Datos](./docs/database.md)
- [Despliegue](./docs/deployment.md)

## 🤝 Contribuir

1. Fork del repositorio
2. Crea rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Add nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre Pull Request

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## 👥 Equipo

- Desarrollo: [Tu Nombre]
- Curso: SI2 - Examen 1

---

**FashionStore** - Tu estilo, un clic de distancia 🛍️