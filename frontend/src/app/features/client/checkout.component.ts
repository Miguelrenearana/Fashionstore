import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ClientService, CartItem } from './client.service';

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
            <button type="button" class="btn btn-primary w-full" [disabled]="processing" (click)="placeOrder()">
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
    this.api.getCart().subscribe({
      next: (res: any) => {
        this.items = res.items ?? [];
        this.total = Math.max(0, (res.total ?? 0) || this.items.reduce((s, i) => s + i.price * i.quantity, 0));
      },
      error: () => (this.error = 'No se pudo cargar el carrito.'),
    });
  }

  placeOrder(): void {
    if (!this.name.trim()) { this.error = 'Ingresa el nombre del destinatario.'; return; }
    if (!this.pickup && !this.address.trim()) { this.error = 'Ingresa la dirección de entrega.'; return; }

    this.processing = true;
    this.error = '';
    this.api
      .checkout(
        this.pickup ? null : { name: this.name, phone: this.phone, address: this.address, city: this.city },
        this.paymentMethod
      )
      .subscribe({
        next: () => {
          this.success = true;
          this.processing = false;
        },
        error: () => {
          this.error = 'No se pudo completar el pago. Revisa los datos e intenta nuevamente.';
          this.processing = false;
        },
      });
  }
}