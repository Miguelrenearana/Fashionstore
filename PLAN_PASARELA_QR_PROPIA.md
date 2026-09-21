# PLAN: Pasarela de Pagos Propia - QR Estático + Verificación Automática

> **Objetivo**: Implementar pasarela de pagos propia con QR estático (Bolivia) y verificación automática, sin depender de terceros (PagosNet, EBANX, etc.)
> **Estado**: Plan para revisión y aprobación
> **Referencia**: Arquitectura existente en `app/payments/` (Gateway pattern, factory, mock/pagosnet adapters)

---

## Contexto y Motivación

- **Problema**: No hay SDK Python para PagosNet Bolivia, EBANX requiere registro + comisión
- **Solución**: Pasarela propia con **QR estático** (formato Bolivia) + **verificación automática** via polling/webhook
- **Ventaja**: Control total, 0% comisión, 0 dependencias externas, listo para producción

---

## Arquitectura General

```
Frontend (QR display) -> Backend API /payments/init -> StaticQRGateway (nuevo adapter)
                              |                           |
                              v                           v
                      Payment DB (Payment model)    QR Code Generator (QR Bolivia fmt)
                              |                           |
                              v                           v
                      Auto-Verifier (polling/worker)  Bank/QR Validator (API banco/QR)
```

---

## Componentes a Implementar

### 1. Nuevo Adapter: StaticQRGateway
**Archivo**: `app/payments/adapters/static_qr_gateway.py`

```python
class StaticQRGateway(PaymentGateway):
    name = "static_qr"
    
    def create_payment(self, request: PaymentRequest) -> PaymentResult:
        # 1. Generar/obtener QR estático del comercio
        # 2. Crear Payment record con reference único
        # 3. Devolver payment_url con QR (SVG/PNG/base64) + monto
        # 4. Iniciar verificación automática (background task)
        
    def get_status(self, reference: str) -> PaymentStatusResult:
        # Consultar estado en BD + validar con banco si necesario
        
    def refund(self, reference: str, amount: Decimal | None) -> PaymentResult:
        # Lógica de devolución (reverso manual o automático)
```

### 2. Generador de QR Bolivia (`app/payments/qr/generator.py`)

**Formato QR Bolivia (estándar Banco Central / QR Simple):**
```
QR Simple Bolivia (formato EMVCo-like):
- Payload: merchant_account, amount, currency (BOB), reference, merchant_name, city
- Formato: CRC16 al final
- Versión: 01 (QR Simple Bolivia)
```

### 3. Verificación Automática (2 estrategias)

#### A. Polling Activo (Background Task / APScheduler)
- Worker cada 10-30s consulta estado de pagos PENDING
- Consulta API del banco / QR validator / webhook interno
- Actualiza estado en BD -> COMPLETED / DECLINED / TIMEOUT

#### B. Webhook Interno (Endpoint público)
- POST /api/v1/payments/webhook/static_qr - recibe notificaciones
- Valida firma/HMAC
- Actualiza estado -> dispara eventos (receipt, stock, etc.)

### 4. Configuración (app/core/config.py - añadir)
```python
# Static QR Gateway
static_qr_merchant_id: str = ""
static_qr_merchant_name: str = "FashionStore"
static_qr_merchant_city: str = "La Paz"
static_qr_account: str = ""  # CUENTA BANCARIA / QR ID
static_qr_bank_api_url: str = ""  # API banco para validación (opcional)
static_qr_webhook_secret: str = ""  # Para validar webhooks internos
static_qr_poll_interval_seconds: int = 15
static_qr_timeout_minutes: int = 10
```

### 5. Factory Update (app/payments/factory.py)
```python
# En build_gateway():
if selected == "static_qr":
    return StaticQRGateway()
```

### 6. Endpoints API (extendiendo app/payments/api/v1/payments.py)
- GET /api/v1/payments/qr/{reference} - devuelve QR (SVG/PNG/base64) + info
- POST /api/v1/payments/webhook/static_qr - webhook interno para validación
- GET /api/v1/payments/qr/status/{reference} - polling manual desde frontend

---

## Flujo Completo

1. Cliente hace checkout -> POST /payments/initiate
2. Backend crea Payment (PENDING) + genera QR estático único
3. Frontend muestra QR (SVG) + monto + timer (10 min)
3. Cliente escanea QR con app bancaria -> paga
4. VERIFICACIÓN AUTOMÁTICA:
   Option A: Worker cada 15s consulta estado en BD + valida con banco
   Option B: Banco/QR envía webhook a /webhook/static_qr
5. Estado cambia a COMPLETED -> genera receipt, libera stock, email
6. Frontend detecta COMPLETED (polling o websocket) -> muestra éxito

---

## Modelo de Datos (extender Payment model)

```python
# En app/models/sales.py - extender Payment
class Payment(Base, TimestampMixin):
    # ... campos existentes
    qr_payload: str | None = None           # Payload QR crudo
    qr_image_svg: str | None = None         # SVG del QR (base64 o path)
    qr_expires_at: DateTime | None = None   # Expiración QR (10 min)
    verification_method: str = "polling"    # "polling" | "webhook"
    verified_at: DateTime | None = None
    bank_response: dict | None = None       # Respuesta cruda del banco
```

**Migración Alembic requerida**: `alembic revision --autogenerate -m "static_qr_gateway_fields"`

---

## Tests Requeridos

| Test | Archivo | Cobertura |
|------|---------|-----------|
| Unit: QR generation | tests/test_static_qr_generator.py | Payload válido, CRC16, formato |
| Unit: Gateway create | tests/test_static_qr_gateway.py | create_payment, get_status, refund |
| Integration: Flow completo | tests/test_static_qr_flow.py | init -> QR -> verify -> complete |
| Unit: QR validator | tests/test_qr_validator.py | CRC16, formato Bolivia |
| Integration: Webhook | tests/test_static_qr_webhook.py | Firma, actualización estado |

---

## Configuración Requerida (.env)

```bash
# Static QR Gateway
PAYMENT_GATEWAY=static_qr
STATIC_QR_MERCHANT_ID=FS001
STATIC_QR_MERCHANT_NAME=FashionStore
STATIC_QR_MERCHANT_CITY=La Paz
STATIC_QR_ACCOUNT=12345678901234567890  # CUENTA BANCARIA / QR ID del banco
STATIC_QR_BANK_API_URL=https://api.banco.bo/qr/validate  # Opcional
STATIC_QR_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxx
STATIC_QR_POLL_INTERVAL_SECONDS=15
STATIC_QR_TIMEOUT_MINUTES=10
```

---

## Dependencias Adicionales

```txt
# requirements.txt - añadir
qrcode[pil]==7.4.2          # Generación QR SVG/PNG
crcmod==1.7                 # CRC16 para QR Bolivia
```

---

## Pasos de Implementación (Orden Sugerido)

| Paso | Acción | Archivos | Tiempo |
|------|--------|----------|--------|
| 1 | Config + Factory | config.py, factory.py | 30 min |
| 2 | QR Generator (Bolivia fmt) | payments/qr/generator.py | 2h |
| 3 | StaticQRGateway adapter | adapters/static_qr_gateway.py | 3h |
| 3b | Modelos + Migración | models/sales.py, alembic | 1h |
| 4 | Verificador (polling + webhook) | services/verification_service.py | 3h |
| 5 | API endpoints + webhook | api/v1/payments.py | 2h |
| 6 | Factory update | factory.py | 15 min |
| 7 | Tests unit/integration | tests/test_static_qr_*.py | 3h |
| 8 | Config .env.example + docs | .env.example, README | 30 min |
| **Total** | | | **~14h** |

---

## Seguridad y Consideraciones

| Aspecto | Implementación |
|---------|----------------|
| QR único por transacción | reference único embebido en QR payload |
| Expiración | 10 min (configurable), limpieza automática |
| Validación webhook | HMAC-SHA256 con STATIC_QR_WEBHOOK_SECRET |
| Idempotencia | reference único, checks de estado antes de actuar |
| Timeout | 10 min default -> TIMEOUT -> liberación stock |
| Logs/Auditoría | AuditLog en cada cambio de estado |
| Rate limiting | En webhook endpoint (slowapi) |

---

## Integración con Frontend

**Endpoint QR**: GET /api/v1/payments/qr/{reference}
```json
{
  "reference": "QR_FS_abc123",
  "qr_svg": "<svg>...</svg>",
  "qr_png_base64": "iVBORw0KGgo...",
  "amount": 150.00,
  "currency": "BOB",
  "expires_at": "2025-01-15T10:15:00Z",
  "merchant_name": "FashionStore"
}
```

**Frontend polling**:
```typescript
// Cada 5s hasta COMPLETED/DECLINED/TIMEOUT
const status = await fetch(/api/v1/payments/qr/status/${reference})
if (status === 'COMPLETED') navigate('/success')
```

---

## Decisiones Pendientes (requieren tu input)

| Decisión | Opciones | Recomendación |
|----------|----------|---------------|
| Validación real vs Mock | Banco real API vs Mock validator | Mock first, real después |
| Verificación | Polling (15s) vs Webhook solo | Híbrido: polling fallback + webhook |
| Banco/QR | Qué banco/QR proveedor? (BISA, BCP, QR Simple) | QR Simple Bolivia estándar |
| Expiración QR | 5min / 10min / 15min | 10 min (configurable) |
| Worker | APScheduler (ya en requirements) vs Celery/Redis | APScheduler (ya en reqs) |
| Reembolso | Manual (admin) vs Automático | Manual primero, auto después |

---

## Checklist de Aceptación

- [ ] PAYMENT_GATEWAY=static_qr funciona en .env
- [ ] POST /payments/initiate devuelve QR SVG + URL
- [ ] QR escaneable en apps bancarias Bolivia (BISA, BCP, etc.)
- [ ] Verificación automática detecta pago en < 30s
- [ ] Estado cambia a COMPLETED -> receipt generado
- [ ] Timeout 10min -> estado TIMEOUT + stock liberado
- [ ] Webhook valida HMAC y actualiza estado
- [ ] Tests: unit (QR, gateway) + integration (flow completo) pasan
- [ ] Suite completa pytest tests/ -q -> 0 fallos
- [ ] Migración Alembic aplica sin error en Neon

---

## Próximos Pasos

1. **Aprobar plan** -> confirmar decisiones pendientes
2. **Crear branch** feature/static-qr-gateway
3. **Implementar** siguiendo orden de pasos arriba
4. **Test local** con QR real en app bancaria (BISA/BCP app)
5. **Deploy staging** -> test end-to-end
5. **Merge** -> tag v3.0.0-ciclo3-static-qr

---

**¿Aprobado para implementar? ¿Confirmas las decisiones pendientes o prefieres ajustar algo?'
