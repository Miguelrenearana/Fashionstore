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
      @for (item of items(); track item.id) {
        <p>Variante #{{ item.variant_id }} × {{ item.quantity }} — Bs {{ item.unit_price }}</p>
      } @empty {
        @if (!reservation()) {
          <p>Tu carrito está vacío.</p>
        }
      }
      @if (items().length > 0) {
        <p class="total">Total: Bs {{ total() }}</p>
        <button (click)="checkout()" [disabled]="loading">Reservar y check-out</button>
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
      .total {
        font-weight: 700;
        margin-top: 1rem;
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
        padding: 0.4rem 1rem;
      }
    `,
  ],
})
export class CartComponent {
  private http = inject(HttpClient);
  readonly items = signal<CartItem[]>([]);
  readonly total = signal(0);
  readonly reservation = signal<Reservation | null>(null);
  loading = false;
  error = '';

  constructor() {
    this.http.get<CartState>(`${environment.apiUrl}/cart`).subscribe((res) => {
      this.items.set(res.details);
      this.total.set(res.total);
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
          this.items.set([]);
          this.total.set(0);
        },
        error: (e) => {
          this.error = e.error?.detail ?? 'No se pudo generar la reserva.';
        },
      })
      .add(() => (this.loading = false));
  }
}