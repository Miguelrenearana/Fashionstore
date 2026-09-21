import { Component, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '@core/environments/environment';

interface CartItem {
  id: number;
  variant_id: number;
  quantity: number;
  unit_price: number;
  variant?: {
    id: number;
    sku: string;
    price: number;
    size_name?: string;
    color_name?: string;
    garment?: { id: number; name: string; images?: { url: string; is_primary: boolean }[] } | null;
  };
}

interface CartState {
  total: number;
  details: CartItem[];
}

interface Reservation {
  id: number;
  pickup_code: string;
  status: string;
  total_amount: number;
}

interface PurchaseResult {
  sale: { id: number; invoice_number: string; status: string; total_amount: number };
  payment: { id: number; gateway_reference: string; status: string };
}

interface Receipt {
  id: number;
  type: string;
  rnc_or_cuf: string | null;
  document_url: string | null;
}

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="cart container py-5" id="main-content">
      <header class="mb-5">
        <h1 class="text-2xl font-bold mb-1">Carrito de compras</h1>
        <p class="text-secondary">Revisa tus productos antes de continuar</p>
      </header>

      @if (error()) {
        <div class="alert alert-error mb-4" role="alert">
          <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <div class="alert-content">{{ error() }}</div>
        </div>
      }

      @if (reservation()) {
        <div class="alert alert-success mb-4" role="alert">
          <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          <div class="alert-content">
            <p class="alert-title">¡Reserva generada!</p>
            <p class="alert-message">Código de recogida: <strong>{{ reservation()?.pickup_code }}</strong> — Total: <strong>Bs {{ reservation()?.total_amount }}</strong></p>
          </div>
        </div>
      }

      @if (purchase()) {
        <div class="alert alert-success mb-4" role="alert">
          <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          <div class="alert-content">
            <p class="alert-title">¡Compra registrada!</p>
            <p class="alert-message">Factura <strong>{{ purchase()?.sale?.invoice_number }}</strong> — Total: <strong>Bs {{ purchase()?.sale?.total_amount }}</strong></p>
          </div>
        </div>
      }

      @if (items().length > 0) {
        <div class="cart-layout grid gap-6">
          <div class="cart-items">
            <div class="card overflow-hidden">
              <div class="cart-header hidden sm:flex px-4 py-3 border-b border-border font-medium text-secondary text-sm">
                <div class="flex-1">Producto</div>
                <div class="w-24 text-center">Precio</div>
                <div class="w-32 text-center">Cantidad</div>
                <div class="w-24 text-right">Subtotal</div>
                <div class="w-10"></div>
              </div>

              @for (item of items(); track item.id) {
                <div class="cart-item flex items-center gap-4 px-4 py-4 border-b border-border last:border-0" [class.sm:hidden]="true">
                  <div class="item-image w-20 h-20 flex-shrink-0 rounded-md overflow-hidden bg-surface-alt relative">
                    @if (getItemImage(item)) {
                      <img [src]="getItemImage(item)" [alt]="getItemName(item)" class="w-full h-full object-cover" loading="lazy" />
                    } @else {
                      <div class="placeholder w-full h-full flex items-center justify-center text-text-muted text-xs">Sin img</div>
                    }
                  </div>

                  <div class="item-details flex-1 min-w-0">
                    <h3 class="font-medium text-sm truncate">{{ getItemName(item) }}</h3>
                    <p class="text-xs text-secondary">{{ item.variant?.size_name || '' }} / {{ item.variant?.color_name || '' }}</p>
                    <p class="text-xs text-secondary">SKU: {{ item.variant?.sku || '—' }}</p>
                    <p class="text-sm font-medium text-text mt-1">Bs {{ item.unit_price }}</p>
                  </div>

                  <div class="item-qty flex items-center gap-2 hidden sm:flex">
                    <button type="button" class="btn btn-ghost btn-sm btn-icon" (click)="changeQty(item, item.quantity - 1)" [disabled]="item.quantity <= 1" aria-label="Disminuir cantidad">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/></svg>
                    </button>
                    <span class="w-10 text-center font-medium">{{ item.quantity }}</span>
                    <button type="button" class="btn btn-ghost btn-sm btn-icon" (click)="changeQty(item, item.quantity + 1)" aria-label="Aumentar cantidad">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                    </button>
                  </div>

                  <div class="item-subtotal w-24 text-right font-medium hidden sm:block">Bs {{ item.unit_price * item.quantity }}</div>

                  <button type="button" class="btn btn-ghost btn-sm btn-icon text-error hover:text-error" (click)="remove(item)" aria-label="Eliminar producto">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                  </button>
                </div>

                @if (true) {
                  <div class="cart-item-mobile sm:hidden px-4 py-3 border-b border-border">
                    <div class="flex items-start gap-3">
                      <div class="item-image w-16 h-16 flex-shrink-0 rounded-md overflow-hidden bg-surface-alt">
@if (getItemImage(item)) {
                      <img [src]="getItemImage(item)" [alt]="getItemName(item)" class="w-full h-full object-cover" loading="lazy" />
                    } @else {
                          <div class="placeholder w-full h-full flex items-center justify-center text-text-muted text-xs">Sin img</div>
                        }
                      </div>
                      <div class="flex-1 min-w-0">
                        <h3 class="font-medium text-sm">{{ item.variant?.garment?.name || 'Producto' }}</h3>
                        <p class="text-xs text-secondary">{{ item.variant?.size_name || '' }} / {{ item.variant?.color_name || '' }}</p>
                        <div class="flex items-center justify-between mt-2">
                          <div class="flex items-center gap-2">
                            <button type="button" class="btn btn-ghost btn-sm btn-icon" (click)="changeQty(item, item.quantity - 1)" [disabled]="item.quantity <= 1" aria-label="Disminuir">
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/></svg>
                            </button>
                            <span class="w-8 text-center font-medium">{{ item.quantity }}</span>
                            <button type="button" class="btn btn-ghost btn-sm btn-icon" (click)="changeQty(item, item.quantity + 1)" aria-label="Aumentar">
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                            </button>
                          </div>
                          <span class="font-medium">Bs {{ item.unit_price * item.quantity }}</span>
                        </div>
                      </div>
                      <button type="button" class="btn btn-ghost btn-sm btn-icon text-error" (click)="remove(item)" aria-label="Eliminar">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                      </button>
                    </div>
                  </div>
                }
              }
            </div>
          </div>

          <aside class="cart-summary">
            <div class="card p-5 sticky top-90">
              <h2 class="text-lg font-semibold mb-4">Resumen del pedido</h2>

              <dl class="space-y-3 mb-4">
                <div class="flex justify-between text-sm">
                  <dt class="text-secondary">Subtotal</dt>
                  <dd class="font-medium">Bs {{ total() }}</dd>
                </div>
                <div class="flex justify-between text-sm">
                  <dt class="text-secondary">Envío</dt>
                  <dd class="font-medium">Calculado en checkout</dd>
                </div>
                <div class="flex justify-between text-sm">
                  <dt class="text-secondary">Descuento</dt>
                  <dd class="font-medium text-success">Bs 0</dd>
                </div>
                <div class="flex justify-between border-t border-border pt-3">
                  <dt class="font-semibold">Total</dt>
                  <dd class="font-semibold text-lg">Bs {{ total() }}</dd>
                </div>
              </dl>

              <div class="coupon-field mb-4">
                <label for="coupon" class="form-label">Cupón de descuento</label>
                <div class="flex gap-2">
                  <input type="text" id="coupon" class="form-input flex-1" placeholder="CÓDIGO" />
                  <button type="button" class="btn btn-secondary btn-sm whitespace-nowrap">Aplicar</button>
                </div>
              </div>

              <div class="actions flex flex-col gap-3">
                <button
                  type="button"
                  class="btn btn-secondary btn-lg"
                  (click)="checkout()"
                  [disabled]="loading()"
                >
                  @if (loading()) {
                    <span class="flex items-center justify-center gap-2">
                      <svg class="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="1" stroke-linecap="round"/></svg>
                      Procesando...
                    </span>
                  } @else {
                    Reservar y recoger en tienda
                  }
                </button>
                <button
                  type="button"
                  class="btn btn-primary btn-lg"
                  (click)="purchaseCart()"
                  [disabled]="loading()"
                >
                  @if (loading()) {
                    <span class="flex items-center justify-center gap-2">
                      <svg class="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="1" stroke-linecap="round"/></svg>
                      Procesando...
                    </span>
                  } @else {
                    Comprar ahora
                  }
                </button>
              </div>

              <p class="text-xs text-secondary text-center mt-4">
                Al continuar, aceptas nuestros <a href="#" class="text-primary hover:underline">Términos y Condiciones</a>
              </p>
            </div>
          </aside>
        </div>
      } @else {
        <div class="empty-state">
          <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
            <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
          </svg>
          <h3 class="empty-state-title">Tu carrito está vacío</h3>
          <p class="empty-state-message">Agrega productos para comenzar tu compra</p>
          <a routerLink="/catalog" class="btn btn-primary mt-4">Ir al catálogo</a>
        </div>
      }
    </section>
  `,
  styles: [`
    .cart-layout {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--space-6);
    }

    @media (min-width: 900px) {
      .cart-layout {
        grid-template-columns: 1fr 380px;
      }
      .cart-summary {
        position: sticky;
        top: 90px;
      }
    }

    .cart-header {
      background: var(--color-surface-alt);
    }

    .cart-item {
      transition: background var(--transition-fast);
    }

    .cart-item:hover {
      background: var(--color-surface-alt);
    }

    .item-image {
      border-radius: var(--radius-md);
    }

    .placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .cart-summary .card {
      box-shadow: var(--shadow-md);
    }

    .coupon-field .form-input {
      flex: 1;
    }

    .actions .btn {
      width: 100%;
    }

    @media (max-width: 640px) {
      .actions .btn {
        padding: var(--space-3) var(--space-4);
      }
    }

    .animate-spin {
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  `],
})
export class CartComponent {
  private http = inject(HttpClient);
  readonly items = signal<CartItem[]>([]);
  readonly total = signal(0);
  readonly reservation = signal<Reservation | null>(null);
  readonly purchase = signal<PurchaseResult | null>(null);
  readonly loading = signal(false);
  readonly error = signal('');

  constructor() {
    this.loadCart();
  }

  private loadCart(): void {
    this.http.get<CartState>(`${environment.apiUrl}/cart`).subscribe({
      next: (res) => {
        this.items.set(res.details);
        this.total.set(res.total);
      },
      error: () => {
        this.items.set([]);
        this.total.set(0);
      },
    });
  }

  changeQty(item: CartItem, quantity: number): void {
    if (quantity < 1) return;
    this.http
      .patch<CartState>(`${environment.apiUrl}/cart/items/${item.variant_id}`, {
        variant_id: item.variant_id,
        quantity,
      })
      .subscribe({
        next: (res) => {
          this.items.set(res.details);
          this.total.set(res.total);
        },
        error: (e) => this.error.set(e.error?.detail ?? 'No se pudo actualizar la línea.'),
      });
  }

  remove(item: CartItem): void {
    this.http
      .delete<CartState>(`${environment.apiUrl}/cart/items/${item.variant_id}`)
      .subscribe({
        next: (res) => {
          this.items.set(res.details);
          this.total.set(res.total);
        },
        error: (e) => this.error.set(e.error?.detail ?? 'No se pudo quitar el producto.'),
      });
  }

  checkout(): void {
    this.loading.set(true);
    this.error.set('');
    this.http
      .post<Reservation>(`${environment.apiUrl}/cart/checkout`, { branch_id: null })
      .subscribe({
        next: (res) => {
          this.reservation.set(res);
          this.purchase.set(null);
          this.items.set([]);
          this.total.set(0);
        },
        error: (e) => {
          this.error.set(e.error?.detail ?? 'No se pudo generar la reserva.');
        },
      })
      .add(() => this.loading.set(false));
  }

  purchaseCart(): void {
    this.loading.set(true);
    this.error.set('');
    this.http
      .post<PurchaseResult>(`${environment.apiUrl}/cart/purchase`, {
        branch_id: null,
        payment_method: 'card',
      })
      .subscribe({
        next: (res) => {
          this.purchase.set(res);
          this.reservation.set(null);
          this.items.set([]);
          this.total.set(0);
        },
        error: (e) => {
          this.error.set(e.error?.detail ?? 'No se pudo completar la compra.');
        },
      })
      .add(() => this.loading.set(false));
  }

  getItemImage(item: CartItem): string | null {
    return item.variant?.garment?.images?.[0]?.url ?? null;
  }

  getItemName(item: CartItem): string {
    return item.variant?.garment?.name ?? 'Producto';
  }
}