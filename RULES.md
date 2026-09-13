# Reglas de desarrollo — FashionStore

Normas obligatorias para el equipo. Cualquier PR debe cumplirlas.

## 1. Idiomas

- **Código, identificadores, API y BD**: en inglés (clases, tablas, endpoints, mensajes de error).
- **Comunicación entre equipo, documentación funcional y entregables**: en español.
- Tablas del **DDL en español** (requisito de la materia) pero los **modelos SQLAlchemy en inglés**
  (1 tabla ↔ 1 clase; columna ↔ atributo).

## 2. Git flow

- Ramas: `main` (protegida, tags `v1.0.0-ciclo{1,2,3}`), `dev`, y `feature/CU-XX-descripcion`.
- **Merge**: squash hacia `dev` (Opción A: commits directos al histórico si la tarea es pequeña).
- Commits con **Conventional Commits + número de caso de uso**:
  `feat(scope): descripción [CU-XX]` · `fix(catalog): corregir stock [CU-14]` · `chore: ...`.
- Nunca commitear `.env`, secretos ni credenciales reales.

## 3. Backend (FastAPI)

- **Arquitectura**: routers → services → repositories/SQLAlchemy. Nada de lógica en los routers.
- **Validación** con Pydantic (schemas) en `app/schemas/`.
- Recursos `REST` en inglés, plurales; paginación simple y coherente (`?page=&size=`).
- Errores: excepciones tipadas en `app/core/exceptions.py`, manejadas por `app/core/dependencies.py`.
- Comentarios en inglés (mínimos); docstrings solo en puntos no evidentes.

## 4. Arquitectura general

- **Monolito modular** en `backend/`; frontend y mobile consumen solo la API pública.
- **Desacoplamiento de pagos**: dominio abstracto `PaymentGateway`; adapters
  `MockGateway` (dev) y `PagosNetGateway` (sandbox). Se seleccionan por variable `PAYMENT_GATEWAY`.
- **IA**: embeddings con sentence-transformers guardados en `product_embeddings` (pgvector);
  recomendación por similitud coseno en el índice `ivfflat (vector_cosine_ops)`.

## 5. BD

- Todas las tablas en esquema público; `created_at`/`updated_at` en todas (timestamptz).
- **Reserva**: `PENDING → PREPARED → IN_TRIAL → COMPLETED | CANCELLED | EXPIRED`.
- Nunca borrado físico de tablas maestro (soft delete con `is_active` cuando aplique).
- Migraciones solo con **Alembic** (nada de SQL a mano en código).

## 6. UML (entregables)

- Por cada caso de uso implementado se generan **2 diagramas PlantUML**:
  - **Secuencia** y **Comunicación**, ambos con plantilla de 4 columnas:
    `Actor → «UI» → «Controller» → «Model»` (colaboración: Actor — Boundary — Controller — Entity).
- Salida en `docs/uml/{cicloX}/CU-XX/{sequence,communication}.puml`.
- **No** se generan diagramas de clases (ya entregados aparte por el equipo).

## 7. Entregables por caso de uso (tabla)

Cada CU documentado con columnas estrictas:

```
CASO DE USO | PROPÓSITO | ACTORES | ACTOR INICIADOR
PRECONDICIÓN | FLUJO DE SUCESO PRINCIPAL | POSTCONDICIÓN | EXCEPCIÓN
```

## 8. Ciclos

- **Ciclo 1**: CU-01, 02, 04, 06, 07, 12, 13, 14, 15, 17.
- **Ciclo 2**: CU-03, 05, 08, 09, 10, 16, 18, 19, 20, 21, 23, 24.
- **Ciclo 3**: pausado — no tocar hasta que lo solicite el dueño del proyecto.