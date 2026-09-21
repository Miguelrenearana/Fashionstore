# 🏁 PLAN DE REPARACIÓN CICLO 2 — NOTA DE CIERRE

> **Rol**: Agente Ciclo 2 (validador)  
> **Estado**: **VERIFICADO — SIN ACCIÓN REQUERIDA**  
> **Evidencia**: Suite completa `pytest tests/ -q` → **74 passed, 0 failed** (2 corridas consecutivas verdes, ~10 min cada una).

---

## 📋 Contexto

El Ciclo 1 (CU-15/CU-17) tenía 10 fallos preexistentes documentados en `PLAN_CICLO_1.md` §🔍 DIAGNÓSTICO. La reparación se ejecutó exclusivamente en **test-infra** (`backend/tests/conftest.py`):

- Añadida constante `STOCK_BASE = 10` (antes referenciada pero no definida → `NameError`).
- Fixture autouse `reset_inventory`: fuerza `quantity = STOCK_BASE` y `reserved_quantity = 0` **antes** de cada test.
- Fixture autouse `clear_cart`: limpia `CartDetail` y `Cart` **después** de cada test.

**Causa raíz única confirmada**: **contaminación cruzada de stock (Inventory) y carrito (Cart/CartDetail)** en la **BD Neon compartida** entre tests. El aislamiento en `conftest.py` resolvió **todos** los fallos, incluyendo los 5 que pertenecían a CUs del Ciclo 2.

---

## ✅ Verificación de CUs Ciclo 2

| CU | Test file | Estado |
|----|-----------|--------|
| CU-16 Consulta y cancelación de reservas | `test_cu16_cu18.py` | ✅ **VERIFICADO** (3 tests pasan) |
| CU-18 Preparación de prendas reservadas | `test_cu16_cu18.py` | ✅ **VERIFICADO** (mismo archivo) |
| CU-20 Gestión del carrito de compras | `test_cu20_cu21.py` | ✅ **VERIFICADO** (2 tests pasan) |
| CU-21 Realizar compra en línea | `test_cu20_cu21.py` | ✅ **VERIFICADO** (mismo archivo) |
| CU-23 Venta presencial (POS) | `test_cu23_cu24.py` | ✅ **VERIFICADO** (1 test pasa) |
| CU-24 Pago en caja y comprobante | `test_cu23_cu24.py` | ✅ **VERIFICADO** (mismo archivo) |

---

## 📊 Evidencia en caliente

```
# Corrida 1
pytest tests/ -q --tb=no   →   74 passed, 0 failed   (0:10:29)

# Corrida 2 (confirmación)
pytest tests/ -q --tb=no   →   74 passed, 0 failed   (0:10:45)
```

- **Sin modificar** lógica de backend, ni routes, ni services, ni tests.
- Solo fixtures de aislamiento en `backend/tests/conftest.py` (líneas 71-95).

---

## 📝 Actualización de trazabilidad

- `TODO.md` → marca CU-16/18, CU-20/21, CU-23/24 como **verificados** (ya estaban [x] en Ciclo 2; se elimina la nota de "fallos preexistentes" en la sección Ciclo 1).
- `PLAN_CICLO_1.md` §🔍 DIAGNÓSTICO → se conserva como trazabilidad oficial (no se borra).
- `PLAN_REPARACION_CICLO_1.md` → contiene la corrección completa con `NOTA DE CIERRE` para el Ciclo 2.

---

## 🔒 Cierre

**No hay trabajo pendiente para Ciclo 2**. El agente de Ciclo 2 solo valida y cierra.