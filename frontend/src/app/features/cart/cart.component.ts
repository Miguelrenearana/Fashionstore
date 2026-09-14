import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@core/environments/environment';

interface CartItem {
  id: number;
  variant_id: number;
  quantity: number;
  unit_price: number;
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
  template: `
    <section class="cart">
      <h2>Carrito</h2>
      @if (error) {
        <p class="error">{{ error }}</p>
      }
      @if (reservation()) {
        <p class="ok">
          <strong>¡Reserva generada!</strong> Código de recogida: {{ reservation()?.pickup_code }}
          — Total: Bs {{ reservation()?.total_amount }}
        </p>
      }
      @if (purchase()) {
        <p class="ok">
          <strong>¡Compra registrada!</strong> Factura {{ purchase()?.sale?.invoice_number }} —
          Total: Bs {{ purchase()?.sale?.total_amount }}
        </p>
      }
      @for (item of items(); track item.id) {
        <div class="line">
          <span>Variante #{{ item.variant_id }} — Bs {{ item.unit_price }}</span>
          <button (click)="changeQty(item, item.quantity - 1)">−</button>
          <span>{{ item.quantity }}</span>
          <button (click)="changeQty(item, item.quantity + 1)">+</button>
          <button class="link" (click)="remove(item)">quitar</button>
        </div>
      } @empty {
        @if (!reservation() && !purchase()) {
          <p>Tu carrito está vacío.</p>
        }
      }
      @if (items().length > 0) {
        <p class="total">Total: Bs {{ total() }}</p>
        <div class="actions">
          <button (click)="checkout()" [disabled]="loading">Reservar y check-out</button>
          <button class="primary" (click)="purchaseCart()" [disabled]="loading">Comprar ahora</button>
        </div>
      }
    </section>
  `,
  styles: [
    `
      .cart {
        padding: 1.5rem;
        max-width: 640px;
        margin: 0 auto;
      }
      .line {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.4rem 0;
        border-bottom: 1px solid #eee;
      }
      .total {
        font-weight: 700;
        margin-top: 1rem;
      }
      .actions {
        display: flex;
        gap: 0.6rem;
        margin-top: 0.5rem;
      }
      .primary {
        background: var(--color-primary);
        color: #fff;
        border: none;
      }
      .error {
        color: #b00020;
      }
      .ok {
        color: #0a7d2f;
        background: #e8f5e9;
        padding: 0.75rem;
        border-radius: 6px;
      }
      button {
        cursor: pointer;
        padding: 0.35rem 0.7rem;
      }
      .link {
        background: none;
        border: none;
        color: var(--color-primary);
        text-decoration: underline;
      }
    `,
  ],
})
export class CartComponent {
  private http = inject(HttpClient);
  readonly items = signal<CartItem[]>([]);
  readonly total = signal(0);
  readonly reservation = signal<Reservation | null>(null);
  readonly purchase = signal<PurchaseResult | null>(null);
  loading = false;
  error = '';

  constructor() {
    this.loadCart();
  }

  private loadCart(): void {
    this.http.get<CartState>(`${environment.apiUrl}/cart`).subscribe((res) => {
      this.items.set(res.details);
      this.total.set(res.total);
    });
  }

  changeQty(item: CartItem, quantity: number): void {
    if (quantity < 1) {
      return;
    }
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
        error: (e) => (this.error = e.error?.detail ?? 'No se pudo actualizar la línea.'),
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
        error: (e) => (this.error = e.error?.detail ?? 'No se pudo quitar el producto.'),
      });
  }

  checkout(): void {
    this.loading = true;
    this.error = '';
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
          this.error = e.error?.detail ?? 'No se pudo generar la reserva.';
        },
      })
      .add(() => (this.loading = false));
  }

  purchaseCart(): void {
    this.loading = true;
    this.error = '';
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
          this.error = e.error?.detail ?? 'No se pudo completar la compra.';
        },
      })
      .add(() => (this.loading = false));
  }
}