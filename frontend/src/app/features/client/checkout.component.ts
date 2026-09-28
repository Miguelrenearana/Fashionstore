import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { ClientService, CartItem, PurchaseResponse } from './client.service';

interface CheckoutPayment {
  saleId: number;
  reference: string;
  status: string;
}

@Component({
  selector: 'app-client-checkout',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="page">
      <h1 class="page-title">Finalizar compra</h1>
      <p class="page-subtitle">Completa los datos del envío y realiza el pago electrónico.</p>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      @if (success) {
        <div class="success card">
          <h2>¡Compra confirmada! 🎉</h2>
          <p>Tu compra fue registrada y el pago procesado correctamente.</p>
          <div class="success-actions">
            <a routerLink="/client/history" class="btn btn-primary">Ver historial de compras</a>
            <a routerLink="/client/catalog" class="btn btn-outline">Seguir comprando</a>
          </div>
        </div>
      } @else if (payment) {
        <section class="card section" aria-live="polite">
          <h2>Estado del pago: {{ payment.status }}</h2>
          @if (payment.saleId) { <p>Venta #{{ payment.saleId }}</p> }
          @if (payment.reference) {
            <p>Referencia: <strong>{{ payment.reference }}</strong></p>
            <button type="button" class="btn btn-primary" [disabled]="processing || !ready || gateway !== 'mock'" (click)="confirmPayment()">
              {{ processing ? 'Consultando pago...' : 'Consultar / reintentar confirmación' }}
            </button>
          } @else {
            <p>No se recibió una referencia de pago. Revisa el historial antes de intentar otra compra.</p>
          }
          <p>Esta consulta conserva la venta existente.</p>
          @if (payment.status === 'DECLINED') {
            <button class="btn btn-outline" [disabled]="processing" (click)="startNewPurchase()">Empezar otra compra</button>
          }
          <a routerLink="/client/history" class="btn btn-outline">Ver historial de compras</a>
        </section>
      } @else if (attempt) {
        <section class="card section" aria-live="polite">
          <h2>{{ processing ? 'Consultando compra...' : 'Resultado de compra por verificar' }}</h2>
          <p>No sabemos todavía si se creó la venta. Consulta este intento antes de iniciar otra compra.</p>
          <button class="btn btn-primary" [disabled]="processing" (click)="recoverPurchase()">Recuperar / consultar venta</button>
          @if (retryAttempt) {
            <button class="btn btn-outline" [disabled]="processing" (click)="submitPurchase()">Reintentar el mismo intento</button>
          }
          <a routerLink="/client/history" class="btn btn-outline">Ver historial</a>
        </section>
      } @else {
        <div class="layout" *ngIf="items.length > 0; else emptyTpl">
          <div class="left">
            <section class="card section">
              <h2 class="section-title">1 · Datos de envío</h2>
              <div class="field">
                <label class="field-label">Nombre del destinatario</label>
                <input type="text" class="input" [(ngModel)]="name" placeholder="Nombre y apellido" />
              </div>
              <div class="field">
                <label class="field-label">Teléfono</label>
                <input type="tel" class="input" [(ngModel)]="phone" placeholder="+591 70000000" />
              </div>
              <div class="field">
                <label class="field-label">Dirección</label>
                <input type="text" class="input" [(ngModel)]="address" placeholder="Calle, Nº, Zona" />
              </div>
              <div class="field">
                <label class="field-label">Ciudad</label>
                <input type="text" class="input" [(ngModel)]="city" placeholder="Santa Cruz de la Sierra" />
              </div>
              <div class="field checkbox">
                <input type="checkbox" id="pickup" [(ngModel)]="pickup" />
                <label for="pickup">Recoger en tienda (sucursal)</label>
              </div>
              @if (pickup) {
                <p class="hint">Elige la sucursal al confirmar la compra. Sin costo de envío.</p>
              }
            </section>

            <section class="card section">
              <h2 class="section-title">2 · Método de pago</h2>
              <p class="hint">Pago electrónico simulado con pasarela. No se cargan datos reales.</p>
              <div class="field">
                <label class="field-label">Método de pago</label>
                <select class="select w-full" [(ngModel)]="paymentMethod">
                  <option value="card">Tarjeta de débito / crédito</option>
                  <option value="qr">Código QR</option>
                  <option value="transfer">Transferencia bancaria</option>
                </select>
              </div>
              @if (paymentMethod === 'card') {
                <div class="field">
                  <label class="field-label">Número de tarjeta</label>
                  <input type="text" class="input" placeholder="0000 0000 0000 0000" [(ngModel)]="cardNumber" />
                </div>
                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Vencimiento</label>
                    <input type="text" class="input" placeholder="MM/AA" [(ngModel)]="cardExpiry" />
                  </div>
                  <div class="field">
                    <label class="field-label">CVC</label>
                    <input type="text" class="input" placeholder="123" [(ngModel)]="cardCvc" />
                  </div>
                </div>
              }
            </section>
          </div>

          <aside class="summary card">
            <h2 class="section-title">Resumen</h2>
            @for (item of items; track item.variant_id) {
              <div class="row">
                <span>{{ item.name }} <small>×{{ item.quantity }}</small></span>
                <span>S/{{ (item.price * item.quantity) | number:'1.2-2' }}</span>
              </div>
            }
            <div class="row total"><span>Total</span><span>S/{{ total | number:'1.2-2' }}</span></div>
            <button type="button" class="btn btn-primary w-full" [disabled]="processing || !ready || gateway !== 'mock'" (click)="placeOrder()">
              {{ processing ? 'Procesando pago...' : 'Pagar S/' + (total | number:'1.2-2') }}
            </button>
            <p class="secure">🔒 Este pago es simulado en entorno de prueba.</p>
          </aside>
        </div>

        <ng-template #emptyTpl>
          <div class="empty card">
            <p>Tu carrito está vacío. Agrega productos antes de finalizar la compra.</p>
            <a routerLink="/client/catalog" class="btn btn-primary">Ir al catálogo</a>
          </div>
        </ng-template>
      }
    </div>
  `,
  styles: [
    `
      .page-title { margin-bottom: 4px; }
      .page-subtitle { color: var(--color-text-muted); margin-bottom: 1.25rem; }
      .layout { display: grid; grid-template-columns: 1fr 340px; gap: 1.5rem; align-items: start; }
      @media (max-width: 800px) { .layout { grid-template-columns: 1fr; } }
      .section { padding: 1.25rem; margin-bottom: 1rem; }
      .section-title { margin: 0 0 1rem; font-size: 1.05rem; }
      .field { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 0.85rem; }
      .field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }
      .field-label { font-size: 0.8rem; color: var(--color-text-muted); }
      .field.checkbox { flex-direction: row; align-items: center; gap: 0.5rem; }
      .hint { color: var(--color-text-muted); font-size: 0.85rem; }
      .w-full { width: 100%; }
      .select.w-full, .input.w-full { width: 100%; }
      .summary { padding: 1.25rem; position: sticky; top: 1rem; }
      .row { display: flex; justify-content: space-between; padding: 0.35rem 0; font-size: 0.9rem; }
      .row small { color: var(--color-text-muted); }
      .row.total { border-top: 1px solid var(--color-border); margin-top: 0.75rem; padding-top: 0.75rem; font-weight: 700; font-size: 1.1rem; }
      .secure { font-size: 0.78rem; color: var(--color-text-muted); text-align: center; margin-top: 0.75rem; }
      .btn-primary { margin-top: 0.75rem; }
      .success { text-align: center; padding: 3rem 1rem; }
      .success h2 { margin: 0 0 0.5rem; }
      .success-actions { display: flex; gap: 0.75rem; justify-content: center; margin-top: 1.25rem; flex-wrap: wrap; }
      .empty { text-align: center; padding: 3rem 1rem; }
      .empty p { margin-bottom: 1rem; }
    `,
  ],
})
export class CheckoutComponent implements OnInit {
  private api = inject(ClientService);

  items: CartItem[] = [];
  total = 0;
  error = '';
  success = false;
  processing = false;
  ready = false;
  gateway = '';
  payment: CheckoutPayment | null = null;
  attempt: { token: string; method: string } | null = null;
  retryAttempt = false;
  private storageKey = '';

  name = '';
  phone = '';
  address = '';
  city = '';
  pickup = false;

  paymentMethod = 'card';
  cardNumber = '';
  cardExpiry = '';
  cardCvc = '';

  ngOnInit(): void {
    forkJoin({ config: this.api.getPaymentConfig(), user: this.api.getMe() }).subscribe({
      next: ({ config, user }) => {
        this.gateway = config.gateway;
        this.storageKey = `fs-checkout-payment:${user.id}`;
        try {
          const saved = sessionStorage.getItem(this.storageKey);
          if (saved) {
            const state = JSON.parse(saved);
            this.payment = state.payment ?? (state.reference && state.saleId ? state : null);
            this.attempt = state.attempt ?? null;
          }
        } catch {
          this.error = 'No se pudo recuperar el pago anterior. Revisa el historial antes de continuar.';
          return;
        }
        this.ready = true;
        if (this.gateway !== 'mock') {
          this.error = 'Este checkout solo permite confirmar pagos con la pasarela mock.';
        }
      },
      error: () => (this.error = 'No se pudo verificar la pasarela de pago. Recarga la página para reintentar.'),
    });
    this.loadCart();
  }

  private loadCart(): void {
    this.api.getCart().subscribe({
      next: (res) => {
        this.items = res.items ?? [];
        this.total = Math.max(0, (res.total ?? 0) || this.items.reduce((s, i) => s + i.price * i.quantity, 0));
      },
      error: () => (this.error = 'No se pudo cargar el carrito.'),
    });
  }

  placeOrder(): void {
    if (this.processing || this.success || !this.ready || this.gateway !== 'mock') return;
    if (this.payment) { this.confirmPayment(); return; }
    if (this.attempt) { this.recoverPurchase(); return; }
    if (!this.items.length) return;
    if (!this.name.trim()) { this.error = 'Ingresa el nombre del destinatario.'; return; }
    if (!this.pickup && !this.address.trim()) { this.error = 'Ingresa la dirección de entrega.'; return; }

    this.attempt = { token: crypto.randomUUID(), method: this.paymentMethod };
    if (!this.savePayment()) { this.attempt = null; return; }
    this.submitPurchase();
  }

  submitPurchase(): void {
    if (!this.attempt || this.payment || this.processing || !this.ready || this.gateway !== 'mock') return;
    this.processing = true;
    this.retryAttempt = false;
    this.error = '';
    this.api
      .checkout(
        this.pickup ? null : { name: this.name, phone: this.phone, address: this.address, city: this.city },
        this.attempt.method,
        this.attempt.token,
      )
      .subscribe({
        next: (res) => this.acceptPurchase(res),
        error: (err) => {
          this.processing = false;
          if ([400, 401, 403, 409, 422].includes(err.status)) {
            this.attempt = null;
            this.savePayment();
            this.error = 'La compra no fue creada. Corrige los datos o revisa el stock e intenta nuevamente.';
          } else {
            this.error = 'No se pudo verificar la creación de la venta. Recupera este intento antes de continuar.';
          }
        },
      });
  }

  recoverPurchase(): void {
    if (!this.attempt || this.processing || !this.ready) return;
    this.processing = true;
    this.error = '';
    this.retryAttempt = false;
    this.api.recoverPurchase(this.attempt.token).subscribe({
      next: (res) => this.acceptPurchase(res),
      error: (err) => {
        this.processing = false;
        this.retryAttempt = err.status === 404;
        this.error = err.status === 404
          ? 'Todavía no se encontró la venta. Puedes reintentar el mismo intento sin duplicarla.'
          : 'No se pudo recuperar la compra. Conservamos el intento para volver a consultar.';
      },
    });
  }

  private acceptPurchase(res: PurchaseResponse): void {
    this.processing = false;
    if (!res.sale?.id || !res.payment?.gateway_reference) {
      this.error = 'La venta aún no tiene una referencia de pago disponible. Vuelve a consultar; si persiste, solicita asistencia con este intento: ' + this.attempt?.token;
      return;
    }
    this.payment = { saleId: res.sale.id, reference: res.payment.gateway_reference, status: res.payment.status };
    this.savePayment();
    this.items = [];
    this.confirmPayment();
  }

  startNewPurchase(): void {
    if (!this.payment || this.processing || !['DECLINED'].includes(this.payment.status)) return;
    this.confirmPayment(true);
  }

  confirmPayment(startNew = false): void {
    const reference = this.payment?.reference;
    if (!reference || this.processing || !this.ready || this.gateway !== 'mock') return;
    this.processing = true;
    this.error = '';
    this.api.confirmPayment(reference).subscribe({
      next: (res) => {
        if (res.reference !== reference) {
          this.error = 'La respuesta no corresponde al pago solicitado. Conservamos la referencia para reintentar.';
          this.processing = false;
          return;
        }
        this.payment = { ...this.payment!, status: res.status };
        this.success = res.status === 'COMPLETED';
        this.processing = false;
        this.savePayment();
        if (startNew && ['DECLINED'].includes(res.status)) {
          this.payment = null;
          this.attempt = null;
          this.savePayment();
          this.loadCart();
        }
        if (this.success) {
          try { sessionStorage.removeItem(this.storageKey); } catch { /* The reference remains recoverable. */ }
        }
      },
      error: () => {
        this.processing = false;
        this.error = 'No se pudo consultar o confirmar el pago. Se muestra el último estado conocido; reintenta con la misma referencia.';
      },
    });
  }

  private savePayment(): boolean {
    try {
      if (!this.payment && !this.attempt) sessionStorage.removeItem(this.storageKey);
      else sessionStorage.setItem(this.storageKey, JSON.stringify({ payment: this.payment, attempt: this.attempt }));
      return true;
    } catch {
      this.error = 'No se pudo guardar la referencia en esta pestaña. Mantén esta página abierta para consultar el pago.';
      return false;
    }
  }
}
