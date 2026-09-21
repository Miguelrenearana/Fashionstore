import { Component, inject, signal, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { environment } from '@core/environments/environment';

interface Category {
  id: number;
  name: string;
}

interface CatalogItem {
  id: number;
  name: string;
  description: string | null;
  base_price: number;
  min_price: number;
  in_stock: boolean;
  is_ar_enabled: boolean;
  category: { id: number; name: string } | null;
  images: { url: string; is_primary: boolean }[];
}

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [RouterLink],
  template: `
    <section class="catalog container py-5" id="main-content">
      <header class="catalog-header mb-5">
        <h1 class="text-2xl font-bold mb-1">Catálogo</h1>
        <p class="text-secondary">Descubre nuestra colección de prendas</p>
      </header>

      <div class="catalog-layout grid gap-5">
        <aside class="catalog-filters aside" aria-label="Filtros">
          <div class="card p-4">
            <h3 class="font-semibold mb-4">Filtros</h3>

            <div class="form-field mb-4">
              <label class="form-label" for="search">Buscar</label>
              <input
                id="search"
                type="search"
                class="form-input"
                placeholder="Buscar prendas..."
                [value]="search()"
                (input)="onSearch($event)"
                aria-describedby="search-hint"
              />
              <span id="search-hint" class="form-hint">Escribe nombre, descripción o SKU</span>
            </div>

            <div class="form-field mb-4">
              <label class="form-label" for="category">Categoría</label>
              <select
                id="category"
                class="form-input form-select"
                [value]="category()"
                (change)="onCategory($event)"
              >
                <option value="">Todas las categorías</option>
                @for (cat of categories(); track cat.id) {
                  <option [value]="cat.id">{{ cat.name }}</option>
                }
              </select>
            </div>

            @if (search() || category()) {
              <button type="button" class="btn btn-ghost btn-sm btn-block" (click)="clearFilters()">
                Limpiar filtros
              </button>
            }
          </div>
        </aside>

        <main class="catalog-results">
          <div class="results-toolbar flex flex-wrap items-center justify-between gap-3 mb-4">
            <p class="text-sm text-secondary">
              @if (items().length > 0) {
                Mostrando {{ items().length }} producto{{ items().length !== 1 ? 's' : '' }}
              } @else {
                No se encontraron productos
              }
            </p>
            <div class="flex items-center gap-2">
              <label for="sort" class="text-sm text-secondary">Ordenar:</label>
              <select id="sort" class="form-input form-select form-select-sm" style="width: auto;">
                <option value="relevance">Relevancia</option>
                <option value="price-asc">Precio: menor a mayor</option>
                <option value="price-desc">Precio: mayor a menor</option>
                <option value="newest">Más recientes</option>
              </select>
              <div class="flex gap-1" role="group" aria-label="Vista">
                <button type="button" class="btn btn-ghost btn-sm" [class.active]="view() === 'grid'" (click)="view.set('grid')" aria-label="Vista cuadrícula" aria-pressed="true">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
                </button>
                <button type="button" class="btn btn-ghost btn-sm" [class.active]="view() === 'list'" (click)="view.set('list')" aria-label="Vista lista" aria-pressed="false">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
                </button>
              </div>
            </div>
          </div>

          @if (loading()) {
            <div class="catalog-grid" [class.list-view]="view() === 'list'">
              @for (i of [1,2,3,4,5,6]; track i) {
                <div class="skeleton-card"></div>
              }
            </div>
          } @else if (items().length === 0) {
            <div class="empty-state">
              <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/><path d="M8 8L3 3"/>
              </svg>
              <h3 class="empty-state-title">No hay productos</h3>
              <p class="empty-state-message">
                @if (search() || category()) {
                  No se encontraron productos con los filtros actuales.
                  <button type="button" class="btn btn-primary btn-sm mt-3" (click)="clearFilters()">Limpiar filtros</button>
                } @else {
                  El catálogo está vacío por el momento.
                }
              </p>
            </div>
          } @else {
            <div class="catalog-grid" [class.list-view]="view() === 'list'">
              @for (item of items(); track item.id) {
                <a class="product-card card card-interactive" [routerLink]="['/catalog', item.id]" [attr.aria-label]="'Ver ' + item.name" aria-label="Ver producto">
                  <div class="product-image">
                    @if (primaryImage(item)) {
                      <img [src]="primaryImage(item)" [alt]="item.name" loading="lazy" />
                    } @else {
                      <div class="placeholder">Sin imagen</div>
                    }
                    @if (item.is_ar_enabled) {
                      <span class="badge badge-primary product-badge">AR</span>
                    }
                  </div>
                  <div class="product-info">
                    <p class="product-category text-xs text-secondary">{{ item.category?.name }}</p>
                    <h3 class="product-name font-medium text-base mb-1">{{ item.name }}</h3>
                    @if (item.description) {
                      <p class="product-desc text-sm text-secondary line-clamp-2">{{ item.description }}</p>
                    }
                    <div class="product-footer flex items-center justify-between mt-3">
                      <strong class="product-price text-lg">Bs {{ item.min_price }}</strong>
                      <span class="badge" [class.badge-success]="item.in_stock" [class.badge-error]="!item.in_stock">
                        {{ item.in_stock ? 'Disponible' : 'Agotado' }}
                      </span>
                    </div>
                  </div>
                </a>
              }
            </div>

            <div class="pagination mt-5 flex items-center justify-center gap-2" role="navigation" aria-label="Paginación">
              <button class="btn btn-secondary btn-sm" disabled>Anterior</button>
              <span class="text-sm text-secondary">Página 1 de 1</span>
              <button class="btn btn-secondary btn-sm" disabled>Siguiente</button>
            </div>
          }
        </main>
      </div>
    </section>
  `,
  styles: [`
    .catalog-layout {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--space-5);
    }

    @media (min-width: 900px) {
      .catalog-layout {
        grid-template-columns: 260px 1fr;
      }
      .catalog-filters {
        position: sticky;
        top: 80px;
        height: fit-content;
      }
    }

    .catalog-header h1 {
      color: var(--color-text);
    }

    .results-toolbar {
      flex-wrap: wrap;
    }

    .form-select-sm {
      padding: var(--space-1) var(--space-6) var(--space-1) var(--space-2);
      font-size: var(--text-sm);
    }

    .catalog-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: var(--space-4);
    }

    @media (max-width: 640px) {
      .catalog-grid {
        grid-template-columns: 1fr;
      }
    }

    .catalog-grid.list-view {
      grid-template-columns: 1fr;
    }

    .catalog-grid.list-view .product-card {
      display: flex;
      flex-direction: row;
    }

    .catalog-grid.list-view .product-image {
      width: 160px;
      min-width: 160px;
      border-radius: var(--radius-lg) 0 0 var(--radius-lg);
    }

    .catalog-grid.list-view .product-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    @media (max-width: 640px) {
      .catalog-grid.list-view .product-card {
        flex-direction: column;
      }
      .catalog-grid.list-view .product-image {
        width: 100%;
        min-width: 100%;
        height: 180px;
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
      }
    }

    .product-card {
      display: flex;
      flex-direction: column;
      text-decoration: none;
      color: inherit;
      overflow: hidden;
      transition: box-shadow var(--transition-base), transform var(--transition-base);
    }

    .product-card:hover {
      box-shadow: var(--shadow-lg);
      transform: translateY(-2px);
    }

    .product-image {
      position: relative;
      aspect-ratio: 1;
      overflow: hidden;
      background: var(--color-surface-alt);
    }

    .product-image img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform var(--transition-base);
    }

    .product-card:hover .product-image img {
      transform: scale(1.03);
    }

    .placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      color: var(--color-text-muted);
      font-size: var(--text-sm);
    }

    .product-badge {
      position: absolute;
      top: var(--space-2);
      right: var(--space-2);
    }

    .product-info {
      padding: var(--space-3);
      display: flex;
      flex-direction: column;
      flex: 1;
    }

    .product-category {
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .product-name {
      margin: 0;
      font-size: var(--text-base);
      line-height: 1.3;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .product-desc {
      margin: 0;
      flex: 1;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .product-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: var(--space-2);
      border-top: 1px solid var(--color-border);
    }

    .line-clamp-2 {
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .pagination button:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
  `],
})
export class CatalogComponent implements OnInit {
  private http = inject(HttpClient);
  readonly items = signal<CatalogItem[]>([]);
  readonly categories = signal<Category[]>([]);
  readonly loading = signal(true);
  readonly search = signal('');
  readonly category = signal('');
  readonly view = signal<'grid' | 'list'>('grid');

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading.set(true);
    this.http
      .get<{ items: CatalogItem[] }>(`${environment.apiUrl}/catalog?page=1&size=50`)
      .subscribe({
        next: (res) => this.items.set(res.items),
        error: () => this.items.set([]),
        complete: () => this.loading.set(false),
      });
    this.http.get<Category[]>(`${environment.apiUrl}/catalog/categories`).subscribe({
      next: (res) => this.categories.set(res),
      error: () => this.categories.set([]),
    });
  }

  primaryImage(item: CatalogItem): string | null {
    return item.images.find((i) => i.is_primary)?.url ?? null;
  }

  onSearch(event: Event): void {
    this.search.set((event.target as HTMLInputElement).value);
    this.reload();
  }

  onCategory(event: Event): void {
    this.category.set((event.target as HTMLSelectElement).value);
    this.reload();
  }

  clearFilters(): void {
    this.search.set('');
    this.category.set('');
    this.reload();
  }

  private reload(): void {
    this.loading.set(true);
    const params = new URLSearchParams({ page: '1', size: '50' });
    if (this.search()) params.set('search', this.search());
    if (this.category()) params.set('category_id', this.category());
    this.http
      .get<{ items: CatalogItem[] }>(`${environment.apiUrl}/catalog?${params}`)
      .subscribe({
        next: (res) => this.items.set(res.items),
        error: () => this.items.set([]),
        complete: () => this.loading.set(false),
      });
  }
}