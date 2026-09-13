import { Component, inject, signal } from '@angular/core';
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
    <section class="catalog">
      <h2>Catálogo</h2>
      <div class="filters">
        <input (input)="onSearch($event)" placeholder="Buscar prendas..." />
        <select (change)="onCategory($event)">
          <option value="">Todas las categorías</option>
          @for (cat of categories(); track cat.id) {
            <option [value]="cat.id">{{ cat.name }}</option>
          }
        </select>
      </div>
      <div class="grid">
        @for (item of items(); track item.id) {
          <a class="card" routerLink="/catalog/{{ item.id }}">
            @if (primaryImage(item)) {
              <img [src]="primaryImage(item)" alt="" />
            } @else {
              <div class="ph">FashionStore</div>
            }
            <h3>{{ item.name }}</h3>
            <p class="cat">{{ item.category?.name }}</p>
            <p>{{ item.description }}</p>
            <strong>Bs {{ item.min_price }}</strong>
            <span class="stock" [class.out]="!item.in_stock">
              {{ item.in_stock ? 'Disponible' : 'Agotado' }}
            </span>
            @if (item.is_ar_enabled) {
              <span class="badge">AR</span>
            }
          </a>
        } @empty {
          <p>Cargando catálogo...</p>
        }
      </div>
    </section>
  `,
  styles: [
    `
      .catalog {
        padding: 1.5rem;
        max-width: 1100px;
        margin: 0 auto;
      }
      .filters {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
      }
      .filters input,
      .filters select {
        padding: 0.5rem;
      }
      .filters input {
        flex: 1;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 1rem;
      }
      .card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        background: #fff;
        color: inherit;
        text-decoration: none;
      }
      .card img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 6px;
      }
      .ph {
        height: 180px;
        display: grid;
        place-items: center;
        background: #f2f2f2;
        color: #999;
        border-radius: 6px;
      }
      .cat {
        color: #777;
        font-size: 0.8rem;
      }
      .stock {
        display: inline-block;
        margin-top: 0.5rem;
        font-size: 0.75rem;
        padding: 0.15rem 0.5rem;
        border-radius: 12px;
        background: #e6f4ea;
        color: #137333;
      }
      .stock.out {
        background: #fce8e6;
        color: #b00020;
      }
      .badge {
        display: inline-block;
        margin-left: 0.5rem;
        background: var(--color-primary);
        color: #fff;
        border-radius: 4px;
        font-size: 0.7rem;
        padding: 0.15rem 0.4rem;
      }
    `,
  ],
})
export class CatalogComponent {
  private http = inject(HttpClient);
  readonly items = signal<CatalogItem[]>([]);
  readonly categories = signal<Category[]>([]);
  private search = '';
  private category = '';

  constructor() {
    this.http
      .get<{ items: CatalogItem[] }>(`${environment.apiUrl}/catalog?page=1&size=50`)
      .subscribe((res) => this.items.set(res.items));
    this.http.get<Category[]>(`${environment.apiUrl}/catalog/categories`).subscribe((res) => {
      this.categories.set(res);
    });
  }

  primaryImage(item: CatalogItem): string | null {
    return item.images.find((i) => i.is_primary)?.url ?? null;
  }

  onSearch(event: Event): void {
    this.search = (event.target as HTMLInputElement).value;
    this.reload();
  }

  onCategory(event: Event): void {
    this.category = (event.target as HTMLSelectElement).value;
    this.reload();
  }

  private reload(): void {
    const params = new URLSearchParams({ page: '1', size: '50' });
    if (this.search) params.set('search', this.search);
    if (this.category) params.set('category_id', this.category);
    this.http
      .get<{ items: CatalogItem[] }>(`${environment.apiUrl}/catalog?${params}`)
      .subscribe((res) => this.items.set(res.items));
  }
}