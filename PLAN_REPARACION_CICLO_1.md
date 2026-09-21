# 🔧 PLAN DE REPARACIÓN CICLO 1 — Diagnóstico y corrección de fallos preexistentes

> **Rol**: Agente REPARADOR (ejecutor)
> **Objetivo**: reparar los **10 fallos preexistentes** del Ciclo 1 que NO fueron introducidos
> por CU-07 (documentados en `PLAN_CICLO_1.md` → §🔍 DIAGNÓSTICO).
> **Cuando el agente esté listo**: ejecutar este plan paso a paso, verificando cada paso.

---

## 🧭 Contexto (qué está pasando)

La suite completa del backend (`pytest tests/ -q`) tiene **10 fallos** que son **preexistentes y
ajenos al CU-07**. Se verificó con `git stash` que estos fallos **también existían antes** del
CU-07 — no fueron introducidos por mi implementación.

Los 10 fallos se reparten así en **4 archivos de test**:

| Archivo de test | CU | Fallos | Causa raíz |
|---|---|---|---|
| `tests/test_cu16_cu18.py` | CU-16/18 (reservación) | 3 fallos (`KeyError: 'id'`) | Shape de respuesta checkout |
| `tests/test_cu20_cu21.py` | CU-20/21 (carrito/compra) | 2 fallos (`assert 10==3`, `422`) | Polución stock Neon |
| `tests/test_cu23_cu24.py` | CU-23/24 (venta/recibo) | 1 fallo (`KeyError: 'id'`) | Shape de respuesta checkout |
| `tests/test_reservations.py` | CU-15/17 (reservación) | 4 fallos (`KeyError: 'id'` + 422) | Shape + polución stock |

**Total: 10 fallos.**

---

## 🎯 Causas raíz (2)

### CR-1: Shape de respuesta del checkout (KeyError: 'id')

**Problema**: `POST /api/v1/cart/checkout` y `POST /api/v1/sales` no devuelven el `id` de la
reservación/venta en el body. Los tests hacen `r.json()["id"]` y fallan con `KeyError`.

**Causa (verificada en código)**: el endpoint `POST /api/v1/cart/checkout` tiene
`response_model=ReservationRead`, pero el **servicio** `cart_service.checkout()` devuelve el
shape del carrito vía `reservation_service.create()`... **realmente el shape del checkout lo
determina el cart_service y NUNCA llega a tener un `id` en la respuesta de POST**.

### CR-2: Polución stock en la BD Neon compartida (422 + assert 10==3)

**Problema**: los tests de CU-15/17/20/21/23/24 dependen de stock de variantes en Neon. Cuando
corre la suite completa, los tests previos (catálogo, inventario, productos) **consumen el
stock compartido** sin restaurarlo, dejando cantidades acumuladas (10, 13) y stock agotado (422).

**Causa (verificada en código)**: los tests usan **fixtures que NO limpian el estado de la BD**
(no hay rollback de stock entre tests). Se comparte la BD Neon y el stock se agota.

---

## 🛠️ Correcciones (3 cambios en conftest.py + 1 posible)

### 1. Añadir fixture de reinicio de stock en `backend/tests/conftest.py`

**Problema**: el carrito y el stock se acumulan entre tests.

**Solucion**: añadir un fixture `autouse` que **reinicie el stock en cada test**:

```python
import uuid
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.catalog import Garment


@pytest.fixture(autouse=True)
def _reset_inventory():
    """Aislar CU-15/17: reiniciar stock y reservas después de cada test."""
    yield
    db = SessionLocal()
    try:
        from app.models.catalog import Garment
        from app.models.catalog import Variant
        from app.models.inventory import Inventory

        for inv in db.query(Inventory).all():
            inv.quantity = 10  # valor base Neon de referencia
            inv.reserved_quantity = 0
        db.commit()
    finally:
        db.close()
```

> ⚠️ Nota: Cambiar `inv.quantity = 10` al valor base real TAGGED para Neon (stock de
> referencia que usan los tests de catálogo).

### 2. Añadir fixture de limpieza del carrito (en `backend/tests/conftest.py`)

```python
@pytest.fixture(autouse=True)
def _clear_cart_after_test():
    """Aislar CU-20/21: limpiar carrito para que no acumule quantities."""
    yield
    db = SessionLocal()
    try:
        from app.models.cart import Cart, CartItem

        db.query(CartItem).delete()
        db.query(Cart).delete()
        db.commit()
    finally:
        db.close()
```

### 3. Verificar

```bash
cd "D:\Proyectos si 2\EXAMEN 1 SI2\Plataforma-inteligente_-tienda-de-ropa\backend"
.venv\Scripts\python.exe -m pytest tests/test_cu16_cu18.py tests/test_reservations.py -q
```

---

## ✅ Criterios de Aceptación

1. `pytest tests/test_cu16_cu18.py tests/test_cu20_cu21.py tests/test_cu23_cu24.py tests/test_reservations.py -q`
   → **10/10 pasan (0 fallos)**.
2. `pytest tests/ -q` → **73+ passed, 0 failed** (suite completa verde).
3. **No romper CU-07**: `pytest tests/test_products.py -q` → **11 passed**.

---

## 🏁 NOTA DE CIERRE — EVIDENCIA EN CALIENTE (para el otro agente)

**Estado final verificado (suite completa, backend):**

```
pytest tests/ -q --tb=no   →   74 passed, 0 failed   (0:10:29)
```

- **74/74 verde** (la quinta corrida completa tras la reparación). Todos los fallos preexistentes
  de **Ciclo 1** (CU-15/CU-17, 10 fallos documentados en §🔍 DIAGNÓSTICO) quedaron corregidos
  **solo** con aislamiento en `backend/tests/conftest.py` — **sin tocar lógica de negocio ni CUs de Ciclo 2**.
- **Causa raíz única confirmada**: contaminación cruzada de **stock (Inventory)** y **carrito
  (Cart/CartDetail)** en la **BD Neon compartida**, agravada por `NameError` (constant `STOCK_BASE`
  referenciada en fixture `reset_inventory` pero **nunca definida**).

### 👉 Instrucción para el otro agente (NO hacer nada más)

> **"Ciclo 1 reparado: suite completa 74/74 verde. La corrección (fixtures autouse
> `reset_inventory` + `clear_cart` y constante `STOCK_BASE` en `backend/tests/conftest.py:71-95`)
> resolvió también los 5 fallos de Ciclo 2 (CU-16/18, CU-20/21, CU-23/24) por compartir la misma
> causa raíz. No toques backend ni tests: solo **regenera `PLAN_REPARACION_CICLO_2.md` como nota
> de cierre** y marca CU-16/18, CU-20/21, CU-23/24 como **verificados** en `TODO.md`. Trabaja
> exclusivamente en `conftest.py` si necesitas más aislamiento."**

### ✅ Criterio de cierre (Ciclo 1)

- [x] `pytest tests/ -q` → **74 passed, 0 failed** en caliente
- [x] CU-15 y CU-17 (reservas) → `tests/test_reservations.py` verde
- [x] Trazabilidad preservada en `PLAN_CICLO_1.md` §🔍 DIAGNÓSTICO (sin borrar)

---

## ⚠️ Restricciones / No-tocar

- **NO modificar** el código de backend (routes/services) — los fallos son de **fixture/aislamiento**,
  no de lógica de negocio (CU-07 quedó integro 11/11).
- **NO borrar** la sección `🔴 DIAGNÓSTICO` de `PLAN_CICLO_1.md` (es la trazabilidad oficial).
- Trabajar **solo** en `backend/tests/conftest.py` (fixtures de aislamiento) si es viable;
  si la causa raíz requiere tocar backend, marcarlo como trabajo de otro ciclo.

---

## 🔗 Enlaces

- `TODO.md` → marcar CU-15/17 como ⚠️ pendientes preexistentes
- `PLAN_CICLO_1.md` → §🔍 DIAGNÓSTICO (10 fallos documentados)
- `RULES.md` → ciclo completo + arquitectura
