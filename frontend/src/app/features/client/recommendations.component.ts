import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ClientService } from './client.service';

@Component({
  selector: 'app-client-recommendations',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="page">
      <div class="head">
        <h1 class="page-title">Recomendados para ti</h1>
        <a routerLink="/client/chat" class="btn btn-outline btn-sm">💬 Preguntar al asistente</a>
      </div>
      <p class="page-subtitle">Selecciones generadas con inteligencia artificial según el catálogo.</p>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      @if (loading) {
        <div class="loading">Generando recomendaciones...</div>
      } @else if (items.length === 0) {
        <div class="empty card">
          <p>No hay recomendaciones disponibles en este momento.</p>
        </div>
      } @else {
        <div class="grid">
          @for (rec of items; track recVariantId(rec)) {
            <a class="product-card card" [routerLink]="['/client/catalog', productId(rec)]">
              <div class="thumb">
                @if (productImages(rec).length > 0) {
                  <img [src]="productImages(rec)[0]" [alt]="productName(rec)" />
                } @else {
                  <span class="no-img">Sin imagen</span>
                }
              </div>
              <div class="card-body">
                <h3 class="card-name">{{ productName(rec) }}</h3>
                <p class="card-price">S/{{ productPrice(rec) | number:'1.2-2' }}</p>
                @if (productReason(rec)) {
                  <p class="card-reason">✦ {{ productReason(rec) }}</p>
                }
              </div>
            </a>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      .head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
      .page-title { margin: 0; }
      .page-subtitle { color: var(--color-text-muted); margin-bottom: 1.25rem; }
      .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 1rem; }
      .product-card { text-decoration: none; color: inherit; overflow: hidden; transition: transform 0.15s, box-shadow 0.15s; }
      .product-card:hover { transform: translateY(-3px); box-shadow: 0 6px 18px rgba(0,0,0,0.1); }
      .thumb { height: 180px; background: var(--color-surface-variant, #f3f4f6); }
      .thumb img { width: 100%; height: 100%; object-fit: cover; }
      .no-img { display: flex; align-items: center; justify-content: center; height: 100%; color: var(--color-text-muted); }
      .card-body { padding: 0.75rem 1rem; }
      .card-name { font-size: 0.95rem; margin: 0 0 4px; }
      .card-price { font-weight: 600; color: var(--color-primary, #ff8c00); margin: 0 0 4px; }
      .card-reason { font-size: 0.78rem; color: var(--color-text-muted); margin: 0; }
      .loading { text-align: center; color: var(--color-text-muted); padding: 4rem 0; }
      .empty { text-align: center; padding: 3rem 1rem; }
    `,
  ],
})
export class RecommendationsComponent implements OnInit {
  private api = inject(ClientService);

  items: any[] = [];
  loading = false;
  error = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.api.getRecommendations('trending', 12).subscribe({
      next: (data) => {
        this.items = Array.isArray(data) ? data : ((data as any)?.items ?? []);
        this.loading = false;
      },
      error: () => {
        this.api.getTrending(12).subscribe({
          next: (data) => {
            this.items = Array.isArray(data) ? data : ((data as any)?.items ?? []);
            this.loading = false;
          },
          error: () => { this.error = 'No se pudieron generar las recomendaciones.'; this.loading = false; },
        });
      },
    });
  }

  recVariantId(rec: any): number {
    return rec?.variant_id ?? rec?.product?.variant_id ?? rec?.product?.id ?? rec?.id ?? 0;
  }

  productId(rec: any): number {
    return rec?.product_id ?? rec?.product?.id ?? rec?.id ?? 0;
  }

  productName(rec: any): string {
    return rec?.product?.name ?? rec?.product_name ?? rec?.name ?? 'Producto';
  }

  productImages(rec: any): string[] {
    const p = rec?.product ?? rec;
    const imgs = p?.images ?? [];
    return imgs.length ? imgs.map((i: any) => (typeof i === 'string' ? i : i.url)) : [];
  }

  productPrice(rec: any): number {
    const p = rec?.product ?? rec;
    return p?.min_price ?? p?.base_price ?? p?.price ?? 0;
  }

  productReason(rec: any): string {
    return rec?.reason ?? rec?.product?.reason ?? '';
  }
}