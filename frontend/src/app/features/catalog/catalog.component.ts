import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@core/environments/environment';

interface CatalogItem {
  id: number;
  name: string;
  description: string | null;
  base_price: number;
  is_ar_enabled: boolean;
}

@Component({
  selector: 'app-catalog',
  standalone: true,
  template: `
    <section class="catalog">
      <h2>Catálogo</h2>
      <div class="grid">
        @for (item of items(); track item.id) {
          <article class="card">
            <h3>{{ item.name }}</h3>
            <p>{{ item.description }}</p>
            <strong>Bs {{ item.base_price }}</strong>
            @if (item.is_ar_enabled) {
              <span class="badge">AR</span>
            }
          </article>
        } @empty {
          <p>Cargando catálogo...</p>
        }
      </div>
    </section>
  `,
  styles: [
    `
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

  constructor() {
    this.http
      .get<{ items: CatalogItem[] }>(`${environment.apiUrl}/catalog?page=1&size=20`)
      .subscribe((res) => this.items.set(res.items));
  }
}