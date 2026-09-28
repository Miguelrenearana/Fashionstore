import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ClientService, CartItem } from './client.service';

@Component({
  selector: 'app-client-cart',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="page">
      <h1 class="page-title">Carrito de compras</h1>
      <p class="page-subtitle">Revisa tus prendas antes de continuar con la compra.</p>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      @if (loading) {
        <div class="loading">Cargando carrito...</div>
      } @else if (items.length === 0) {
        <div class="empty card">
          <p>Tu carrito está vacío.</p>
          <a routerLink="/client/catalog" class="btn btn-primary">Ir al catálogo</a>
        </div>
      } @else {
        <div class="cart-layout">
          <div class="cart-items card">
            @for (item of items; track item.variant_id) {
              <div class="cart-item">
                <div class="thumb">
                  @if (item.image_url) {
                    <img [src]="item.image_url" [alt]="item.name" />
                  } @else {
                    <span class="no-img">Sin imagen</span>
                  }
                </div>
                <div class="info">
                  <h3 class="name">{{ item.name }}</h3>
                  <p class="meta">
                    {{ item.size || 'Talla única' }} · {{ item.color || '' }}
                  </p>
                  <p class="unit-price">Bs {{ item.price | number:'1.2-2' }} c/u</p>
                </div>
                <div class="qty-control">
                  <button type="button" class="qty-btn" (click)="changeQty(item, item.quantity - 1)" [disabled]="item.quantity <= 1 || updating.has(item.variant_id)">−</button>
                  <span class="qty-value">{{ item.quantity }}</span>
                  <button type="button" class="qty-btn" (click)="changeQty(item, item.quantity + 1)" [disabled]="updating.has(item.variant_id)">+</button>
                </div>
                <p class="line-total">Bs {{ (item.price * item.quantity) | number:'1.2-2' }}</p>
                <button type="button" class="btn btn-ghost btn-sm" (click)="remove(item)">Eliminar</button>
              </div>
            }
          </div>

          <aside class="summary card">
            <h2 class="summary-title">Resumen del pedido</h2>
            <div class="row"><span>Subtotal</span><span>Bs {{ subtotal | number:'1.2-2' }}</span></div>
            <div class="row total"><span>Total de prendas</span><span>Bs {{ total | number:'1.2-2' }}</span></div>

            <a routerLink="/client/checkout" class="btn btn-primary w-full" (click)="goCheckout($event)">Proceder al pago</a>
          </aside>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .page-title { margin-bottom: 4px; }
      .page-subtitle { color: var(--color-text-muted); margin-bottom: 1.25rem; }
      .cart-layout { display: grid; grid-template-columns: 1fr 300px; gap: 1.5rem; align-items: start; }
      @media (max-width: 800px) { .cart-layout { grid-template-columns: 1fr; } }
      .cart-items { padding: 0; overflow: hidden; }
      .cart-item { display: grid; grid-template-columns: 80px 1fr auto auto auto; gap: 1rem; align-items: center; padding: 1rem; border-bottom: 1px solid var(--color-border); }
      .cart-item:last-child { border-bottom: none; }
      .thumb { width: 80px; height: 90px; overflow: hidden; border-radius: 8px; background: var(--color-surface-variant, #f3f4f6); }
      .thumb img { width: 100%; height: 100%; object-fit: cover; }
      .no-img { display: flex; align-items: center; justify-content: center; height: 100%; font-size: 0.7rem; color: var(--color-text-muted); }
      .name { margin: 0 0 4px; font-size: 0.95rem; }
      .meta { margin: 0 0 4px; font-size: 0.8rem; color: var(--color-text-muted); }
      .unit-price { margin: 0; font-size: 0.85rem; }
      .qty-control { display: flex; align-items: center; gap: 0.5rem; }
      .qty-btn { width: 28px; height: 28px; border-radius: 8px; border: 1px solid var(--color-border); background: var(--color-surface); cursor: pointer; }
      .qty-value { min-width: 22px; text-align: center; font-weight: 600; }
      .line-total { font-weight: 600; min-width: 80px; text-align: right; }
      .summary { padding: 1.25rem; position: sticky; top: 1rem; }
      .summary-title { margin: 0 0 1rem; font-size: 1.1rem; }
      .row { display: flex; justify-content: space-between; padding: 0.35rem 0; font-size: 0.9rem; }
      .row.total { border-top: 1px solid var(--color-border); margin-top: 0.5rem; padding-top: 0.75rem; font-weight: 700; font-size: 1.05rem; }
      .w-full { width: 100%; text-align: center; }
      .empty { text-align: center; padding: 3rem 1rem; }
      .empty p { margin-bottom: 1rem; }
    `,
  ],
})
export class CartComponent implements OnInit {
  private api = inject(ClientService);

  items: CartItem[] = [];
  updating = new Set<number>();
  loading = false;
  error = '';

  subtotal = 0;
  total = 0;


  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.api.getCart().subscribe({
      next: (res) => {
        this.items = res.items ?? [];
        this.subtotal = this.items.reduce((s, i) => s + i.price * i.quantity, 0);
        this.total = res.total ?? this.subtotal;
        this.loading = false;
      },
      error: () => { this.error = 'No se pudo cargar el carrito.'; this.loading = false; },
    });
  }

  changeQty(item: CartItem, qty: number): void {
    if (qty < 1 || this.updating.has(item.variant_id)) return;
    const previous = item.quantity;
    this.updating.add(item.variant_id);
    this.error = '';
    this.api.updateCartItem(item.variant_id, qty).subscribe({
      next: () => {
        item.quantity = qty;
        this.updating.delete(item.variant_id);
        this.recalc();
      },
      error: () => {
        item.quantity = previous;
        this.updating.delete(item.variant_id);
        this.error = 'No se pudo actualizar la cantidad.';
      },
    });
  }

  remove(item: CartItem): void {
    this.api.removeCartItem(item.variant_id).subscribe({
      next: () => this.load(),
      error: () => (this.error = 'No se pudo eliminar el producto.'),
    });
  }

  private recalc(): void {
    this.subtotal = this.items.reduce((s, i) => s + i.price * i.quantity, 0);
    this.total = this.subtotal;
  }

  goCheckout(e: Event): void {
    if (this.items.length === 0) {
      e.preventDefault();
      this.error = 'El carrito está vacío.';
    }
  }
}
