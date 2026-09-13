import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';

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
  imports: [RouterLink],
  template: `
    <section class="detail">
      @if (item(); as item) {
        <a class="back" routerLink="/catalog">← Volver al catálogo</a>
        <div class="layout">
          <div class="gallery">
            @if (primaryImage(item)) {
              <img [src]="primaryImage(item)" alt="" />
            } @else {
              <div class="ph">FashionStore</div>
            }
          </div>
          <div class="info">
            <h2>{{ item.name }}</h2>
            <p class="cat">{{ item.category?.name }} · SKU variantes disponibles</p>
            <p>{{ item.description }}</p>
            <strong class="price">Bs {{ selected()?.price ?? item.min_price }}</strong>
            <p class="stock" [class.out]="!item.in_stock">
              {{ item.in_stock ? 'Disponible' : 'Agotado' }}
            </p>

            <label for="variant">Talla / Color</label>
            <select id="variant" [value]="selected()?.id ?? ''" (change)="select($event)">
              @for (v of item.variants; track v.id) {
                <option [value]="v.id">{{ v.size_name }} / {{ v.color_name }} — Bs {{ v.price }}</option>
              }
            </select>

            <div class="actions">
              <button (click)="addToCart()" [disabled]="!selected() || adding()">
                Agregar al carrito
              </button>
            </div>
            <p class="msg">{{ message() }}</p>
          </div>
        </div>

        @if (recommendations().length > 0) {
          <div class="recommendations">
            <h3>También te puede interesar</h3>
            @for (r of recommendations(); track r.suggested_variant_id) {
              <a class="rec card" [routerLink]="['/catalog', r.garment_id]">
                <span>{{ r.variant_name }}</span>
                <small>{{ r.variant_sku }} · afinidad {{ (r.score * 100).toFixed(0) }}%</small>
              </a>
            }
          </div>
        }
      } @else {
        <p>Cargando producto...</p>
      }
    </section>
  `,
  styles: [
    `
      .detail {
        padding: 1.5rem;
        max-width: 960px;
        margin: 0 auto;
      }
      .back {
        color: var(--color-primary);
      }
      .layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-top: 1rem;
      }
      .gallery img {
        width: 100%;
        max-height: 420px;
        object-fit: cover;
        border-radius: 8px;
      }
      .ph {
        height: 420px;
        display: grid;
        place-items: center;
        background: #f2f2f2;
        color: #999;
        border-radius: 8px;
      }
      .cat {
        color: #777;
      }
      .price {
        font-size: 1.5rem;
        display: block;
        margin: 0.75rem 0;
      }
      .stock {
        display: inline-block;
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
      select {
        display: block;
        margin: 0.5rem 0 1rem;
        padding: 0.5rem;
        min-width: 220px;
      }
      button {
        padding: 0.6rem 1.2rem;
        background: var(--color-primary);
        color: #fff;
        border: none;
        border-radius: 6px;
        cursor: pointer;
      }
      button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
      .msg {
        margin-top: 0.75rem;
      }
      .recommendations {
        margin-top: 2rem;
      }
      .recommendations h3 {
        margin-bottom: 0.5rem;
      }
      .rec {
        display: block;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        color: inherit;
        text-decoration: none;
      }
      .rec small {
        display: block;
        color: #777;
        margin-top: 0.2rem;
      }
    `,
  ],
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

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.http
      .get<ProductDetail>(`${environment.apiUrl}/catalog/${id}`)
      .subscribe((item) => {
        this.item.set(item);
        this.selected.set(item.variants[0] ?? null);
        this.loadRecommendations(item.variants[0]?.id);
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