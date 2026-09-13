import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@core/environments/environment';

interface CartItem {
  id: number;
  variant_id: number;
  quantity: number;
  unit_price: number;
}

@Component({
  selector: 'app-cart',
  standalone: true,
  template: `
    <section class="cart">
      <h2>Carrito</h2>
      @for (item of items(); track item.id) {
        <p>Variante #{{ item.variant_id }} × {{ item.quantity }} — Bs {{ item.unit_price }}</p>
      } @empty {
        <p>Tu carrito está vacío.</p>
      }
    </section>
  `,
})
export class CartComponent {
  private http = inject(HttpClient);
  readonly items = signal<CartItem[]>([]);

  constructor() {
    this.http.get<{ details: CartItem[] }>(`${environment.apiUrl}/cart`).subscribe((res) => {
      this.items.set(res.details);
    });
  }
}