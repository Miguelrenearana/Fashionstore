# ADR-001: Mock Payment Gateway como pasarela de pagos

- **Fecha**: 2026-09-13
- **Estado**: Aceptado
- **Decisores**: equipo del proyecto

## Contexto

El sistema requiere cobros en línea (reservas y ventas). El despliegue ocurre en varias fases y
el proyecto es de una materia de universidad: no se dispone de credenciales reales al inicio y el
flujo debe funcionar completa y demostrablemente en cada entrega.

Se evaluaron pasarelas reales compatibles con comercios bolivianos (2026):

- **MercadoPago / Stripe / PayU** → **no** operan con comercios bolivianos. Descartadas.
- **Libélula** → pasarela financiera centroamericana; no aplica para el mercado objetivo. Descartada.
- **PagosNet (Red Enlace / ASOBAN, Bolivia)** → opción real nacional: tarjetas débito/crédito
  (3D Secure), efectivo, portales bancarios y QR vía Red Enlace; ofrece **sandbox/modo testing**
  con `identification_key` + `encryption_key`, confirmación vía **webhook/notificación** y
  estados `PE` (pendiente) → `CO` (confirmada) / `CA` (cancelada).

## Decisión

1. **Dominio abstracto `PaymentGateway`** con método unificado: `create_payment`, `get_status`,
   `refund`.
2. **`MockGateway`**: primera implementación y la **única usada en desarrollo**. Escenarios
   configurables: `Success`, `Declined`, `Timeout`, `Refund` (sin pago parcial). Devuelve
   `payment_url` fake y permite confirmar por `mock_token`.
3. **`PagosNetGateway`**: adapter de sandbox real, seleccionado por `PAYMENT_GATEWAY=pagosnet`.
   Mapea estados de PagosNet → dominio (`PE→PENDING`, `CO→COMPLETED`, `CA→CANCELLED`).
4. La selección se hace por configuración (`app.core.config.Settings.payment_gateway`),
   nunca por imports directos en servicios de negocio.

## Motivos

- Demo universitaria siempre funcional (sin dependencias externas).
- Costo cero en desarrollo (Mock y sandbox PagosNet).
- Migración a producción sin tocar dominio o servicios: solo nueva credencial + variable.

## Consecuencias

- Los servicios de venta/reserva dependen solo del dominio `PaymentGateway`.
- `TODO.md` registra la cuenta PagosNet sandbox como pendiente (🔴).

## Alternativas consideradas

- PagosNet al 100% desde el inicio → bloquea el desarrollo sin credenciales. Rechazada.
- Stripe/PayPal vía entidad extranjera → fuera de alcance académico. Rechazada.