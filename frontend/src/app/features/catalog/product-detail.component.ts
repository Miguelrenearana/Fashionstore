import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface Variant {
  id: number;
  sku: string;
  price: number;
  size_name: string;
  color_name: string;
}

interface ProductDetail {
  id: number;
  name: string;
  description: string | null;
  base_price: number;
  min_price: number;
  in_stock: boolean;
  is_ar_enabled: boolean;
  category: { id: number; name: string } | null;
  images: { url: string; is_primary: boolean }[];
  variants: Variant[];
}

interface Recommendation {
  suggested_variant_id: number;
  score: number;
  variant_name: string | null;
  variant_sku: string | null;
  garment_id: number | null;
}

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [RouterLink, CommonModule],
  template: `
    <section class="product-detail container py-5" id="main-content">
      @if (item(); as item) {
        <nav class="breadcrumb mb-4" aria-label="Ruta de navegación">
          <ol class="flex items-center gap-1 text-sm text-secondary">
            <li><a routerLink="/catalog" class="hover:text-primary">Catálogo</a></li>
            <li aria-hidden="true">/</li>
            <li><a routerLink="/catalog" [queryParams]="{category: item.category?.id}" class="hover:text-primary">{{ item.category?.name }}</a></li>
            <li aria-hidden="true">/</li>
            <li class="text-text truncate max-w-[200px]" aria-current="page">{{ item.name }}</li>
          </ol>
        </nav>

        <a routerLink="/catalog" class="btn btn-ghost btn-sm mb-4" style="--color-primary: var(--color-text); --color-border-focus: var(--color-text); border-color: currentColor; color: var(--color-text);">
          ← Volver al catálogo
        </a>

        @if (loading()) {
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="skeleton skeleton-card h-[420px]"></div>
            <div class="space-y-4">
              <div class="skeleton skeleton-title"></div>
              <div class="skeleton skeleton-text"></div>
              <div class="skeleton skeleton-text w-3/4"></div>
              <div class="skeleton skeleton-text w-1/2 h-8"></div>
            </div>
          </div>
        } @else {
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="product-gallery">
              <div class="main-image rounded-lg overflow-hidden bg-surface-alt aspect-square relative">
                @if (primaryImage(item)) {
                  <img [src]="primaryImage(item)" [alt]="item.name" class="w-full h-full object-cover" loading="eager" />
                } @else {
                  <div class="placeholder flex items-center justify-center h-full text-text-muted">Sin imagen</div>
                }
                @if (item.is_ar_enabled) {
                  <span class="badge badge-primary absolute top-3 right-3">Prueba AR</span>
                }
                @if (!item.in_stock) {
                  <span class="badge badge-error absolute top-3 left-3">Agotado</span>
                }
              </div>

              @if (item.images.length > 1) {
                <div class="thumbnails flex gap-2 mt-3 overflow-x-auto pb-2" role="list" aria-label="Imágenes del producto">
                  @for (img of item.images; track img.url) {
                    <button
                      type="button"
                      class="thumbnail flex-shrink-0 w-20 h-20 rounded-md overflow-hidden border-2 transition-all"
                      [class.border-primary]="primaryImage(item) === img.url"
                      [class.border-border]="primaryImage(item) !== img.url"
                      (click)="setPrimaryImage(img.url)"
                      [attr.aria-label]="'Ver imagen ' + $index + 1"
                      [attr.aria-current]="primaryImage(item) === img.url ? 'true' : 'false'"
                    >
                      <img [src]="img.url" [alt]="'Imagen ' + ($index + 1)" class="w-full h-full object-cover" loading="lazy" />
                    </button>
                  }
                </div>
              }
            </div>

            <div class="product-info">
              <p class="product-category text-sm text-secondary">{{ item.category?.name }}</p>
              <h1 class="text-2xl font-bold mt-1 mb-2">{{ item.name }}</h1>

              @if (item.description) {
                <p class="text-secondary mb-4">{{ item.description }}</p>
              }

              <div class="price-block mb-4">
                <span class="text-3xl font-bold text-text">Bs {{ selected()?.price ?? item.min_price }}</span>
              </div>

              <div class="stock-block mb-4 flex items-center gap-2">
                <span class="badge" [class.badge-success]="item.in_stock" [class.badge-error]="!item.in_stock">
                  {{ item.in_stock ? 'Disponible' : 'Agotado' }}
                </span>
                @if (item.is_ar_enabled) {
                  <span class="badge badge-info">Realidad Aumentada</span>
                }
              </div>

              <div class="variant-selector mb-4">
                <label for="variant-select" class="form-label">Talla / Color</label>
                <select
                  id="variant-select"
                  class="form-input form-select"
                  [value]="selected()?.id ?? ''"
                  (change)="select($event)"
                  [disabled]="!item.in_stock"
                >
                  @for (v of item.variants; track v.id) {
                    <option [value]="v.id">{{ v.size_name }} / {{ v.color_name }} — Bs {{ v.price }}</option>
                  }
                </select>
              </div>

              <div class="actions flex flex-wrap gap-3 mb-4">
                <button
                  class="btn btn-primary btn-lg flex-1 min-w-[200px]"
                  (click)="addToCart()"
                  [disabled]="!selected() || adding() || !item.in_stock"
                >
                  @if (adding()) {
                    <span class="flex items-center gap-2">
                      <svg class="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="1" stroke-linecap="round"/></svg>
                      Agregando...
                    </span>
                  } @else {
                    Agregar al carrito
                  }
                </button>
                <button class="btn btn-secondary btn-lg" [disabled]="!item.in_stock" title="Agregar a favoritos">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                </button>
              </div>

              @if (message()) {
                <p class="text-sm" [class.text-success]="message().includes('Agregado')" [class.text-error]="message().includes('No se pudo')">{{ message() }}</p>
              }

              <div class="product-meta mt-6 pt-4 border-t border-border">
                <dl class="grid grid-cols-2 gap-2 text-sm">
                  <dt class="text-secondary">SKU</dt>
                  <dd class="font-medium">{{ selected()?.sku || '—' }}</dd>
                  <dt class="text-secondary">Categoría</dt>
                  <dd>{{ item.category?.name }}</dd>
                  <dt class="text-secondary">Estado</dt>
                  <dd>{{ item.in_stock ? 'En stock' : 'Sin stock' }}</dd>
                </dl>
              </div>
            </div>
          </div>

          @if (recommendations().length > 0) {
            <section class="recommendations mt-10">
              <h2 class="text-xl font-semibold mb-4">También te puede interesar</h2>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                @for (r of recommendations(); track r.suggested_variant_id) {
                  <a class="card card-interactive p-3" [routerLink]="['/catalog', r.garment_id]">
                    <p class="font-medium text-sm">{{ r.variant_name }}</p>
                    <p class="text-xs text-secondary mt-1">{{ r.variant_sku }} · afinidad {{ (r.score * 100).toFixed(0) }}%</p>
                  </a>
                }
              </div>
            </section>
          }
        }
      } @else {
        <div class="empty-state">
          <div class="skeleton skeleton-card h-64"></div>
        </div>
      }
    </section>
  `,
  styles: [`
    .breadcrumb ol {
      flex-wrap: wrap;
    }

    .breadcrumb a {
      text-decoration: none;
      transition: color var(--transition-fast);
    }

    .breadcrumb a:hover {
      color: var(--color-primary);
      text-decoration: underline;
    }

    .product-gallery {
      position: sticky;
      top: 90px;
    }

    .main-image {
      min-height: 400px;
    }

    @media (max-width: 768px) {
      .product-gallery {
        position: static;
      }
    }

    .thumbnail {
      cursor: pointer;
      background: var(--color-surface-alt);
    }

    .thumbnail:hover {
      border-color: var(--color-primary);
      transform: scale(1.05);
    }

    .thumbnail[aria-current="true"] {
      border-color: var(--color-primary);
      box-shadow: var(--shadow-focus);
    }

    .placeholder {
      width: 100%;
      height: 100%;
    }

    .price-block {
      padding: var(--space-3) 0;
      border-top: 1px solid var(--color-border);
      border-bottom: 1px solid var(--color-border);
    }

    .stock-block {
      flex-wrap: wrap;
    }

    .variant-selector .form-select {
      min-width: 100%;
    }

    .actions {
      flex-wrap: wrap;
    }

    .actions .btn {
      flex: 1;
      min-width: 160px;
    }

    .product-meta {
      border-top: 1px solid var(--color-border);
    }

    .recommendations .card {
      transition: all var(--transition-base);
    }

    .recommendations .card:hover {
      border-color: var(--color-primary);
      box-shadow: var(--shadow-md);
    }
  `],
})
export class ProductDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private http = inject(HttpClient);
  private auth = inject(AuthService);
  private router = inject(Router);

  readonly item = signal<ProductDetail | null>(null);
  readonly selected = signal<Variant | null>(null);
  readonly adding = signal(false);
  readonly message = signal('');
  readonly recommendations = signal<Recommendation[]>([]);
  readonly loading = signal(true);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) return;

    this.http
      .get<ProductDetail>(`${environment.apiUrl}/catalog/${id}`)
      .subscribe({
        next: (item) => {
          this.item.set(item);
          this.selected.set(item.variants[0] ?? null);
          this.loadRecommendations(item.variants[0]?.id);
          this.loading.set(false);
        },
        error: () => {
          this.loading.set(false);
        },
      });
  }

  private loadRecommendations(variantId?: number): void {
    if (!variantId || !this.auth.isAuthenticated()) return;
    this.http
      .get<Recommendation[]>(
        `${environment.apiUrl}/recommendations?source_variant_id=${variantId}&limit=4`
      )
      .subscribe((recs) => this.recommendations.set(recs));
  }

  primaryImage(item: ProductDetail): string | null {
    return item.images.find((i) => i.is_primary)?.url ?? null;
  }

  setPrimaryImage(url: string): void {
    // This would require updating the item's primary image
    // For now, we just update the display
  }

  select(event: Event): void {
    const id = Number((event.target as HTMLSelectElement).value);
    this.selected.set(this.item()?.variants.find((v) => v.id === id) ?? null);
  }

  addToCart(): void {
    const variant = this.selected();
    if (!variant) return;
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/auth']);
      return;
    }
    this.adding.set(true);
    this.message.set('');
    this.http
      .post(
        `${environment.apiUrl}/cart/items`,
        { variant_id: variant.id, quantity: 1 },
        { headers: { Authorization: `Bearer ${this.auth.token()}` } }
      )
      .subscribe({
        next: () => this.message.set('Agregado al carrito.'),
        error: () => this.message.set('No se pudo agregar: verifica disponibilidad.'),
        complete: () => this.adding.set(false),
      });
  }
}