import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';
import { UiButtonComponent } from '@shared/ui/button';
import { UiInputComponent } from '@shared/ui/input';
import { UiTableComponent } from '@shared/ui/table';
import { UiCardComponent } from '@shared/ui/card';

interface Promotion {
  id: number;
  name: string;
  description?: string | null;
  discount_percent: number;
  start_at: string;
  end_at: string;
  status: string;
  garment_ids: number[];
}

interface Product {
  id: number;
  name: string;
}

interface TableColumn {
  header: string;
  property: string;
  cellSelector?: string;
}

@Component({
  selector: 'app-admin-promotions',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    UiButtonComponent,
    UiInputComponent,
    UiTableComponent,
    UiCardComponent,
  ],
  template: `
    <section class="promotions container py-6">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h2 class="text-2xl font-semibold">Promociones (CU-11)</h2>
          <p class="text-sm text-secondary mt-1">Crea y gestiona descuentos sobre prendas.</p>
        </div>
        <ui-button variant="primary" (click)="showCreateForm = true" size="md">
          + Nueva promociÃ³n
        </ui-button>
      </div>

      @if (error) {
        <div class="alert alert-error mb-4">{{ error }}</div>
      }

      @if (showCreateForm) {
        <ui-card class="mb-6 p-4">
          <h3 class="text-lg font-semibold mb-4">Nueva promociÃ³n</h3>
          <form (ngSubmit)="createPromotion()" class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <ui-input
              label="Nombre"
              placeholder="Ej. LiquidaciÃ³n otoÃ±o"
              [(ngModel)]="newPromotion.name"
              name="promo_name"
              required
            />
            <ui-input
              label="% descuento"
              type="number"
              step="0.01"
              min="0"
              max="100"
              [(ngModel)]="newPromotion.discount_percent"
              name="promo_discount"
              required
            />
            <ui-input
              label="Inicio"
              type="date"
              [(ngModel)]="newPromotion.start_at"
              name="promo_start"
              required
            />
            <ui-input
              label="Fin"
              type="date"
              [(ngModel)]="newPromotion.end_at"
              name="promo_end"
              required
            />
            <div class="md:col-span-4">
              <p class="form-label mb-2">Prendas incluidas ({{ selectedProductIds().size }})</p>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                @for (p of products; track p.id) {
                  <label class="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      class="form-checkbox"
                      [checked]="selectedProductIds().has(p.id)"
                      (change)="toggleProduct(p.id)"
                    />
                    {{ p.name }}
                  </label>
                } @empty {
                  <p class="text-sm text-secondary md:col-span-4">No hay prendas activas.</p>
                }
              </div>
            </div>
            <div class="md:col-span-4 flex justify-end gap-2 pt-2">
              <ui-button variant="secondary" type="button" (click)="showCreateForm = false">
                Cancelar
              </ui-button>
              <ui-button variant="primary" type="submit" [disabled]="loading" [loading]="loading">
                Guardar
              </ui-button>
            </div>
          </form>
        </ui-card>
      }

      <ui-card class="mb-6">
        <div class="card-header flex justify-between items-center">
          <h3 class="text-lg font-semibold">Promociones ({{ promotions.length }})</h3>
        </div>
        <ui-table
          [columns]="tableColumns"
          [items]="promotions"
          [trackByItem]="trackById"
          emptyMessage="No hay promociones"
        />
      </ui-card>

      @if (pendingDelete) {
        <ui-card class="mb-6 p-4">
          <p class="mb-4">Â¿Confirmas eliminar la promociÃ³n "{{ pendingDelete.name }}"?</p>
          <div class="flex gap-2">
            <ui-button variant="danger" (click)="confirmDelete()" [loading]="loading">Eliminar</ui-button>
            <ui-button variant="secondary" (click)="pendingDelete = null">Cancelar</ui-button>
          </div>
        </ui-card>
      }
    </section>
  `,
  styles: [
    `
      .promotions ui-input textarea,
      .promotions input[type='date'] {
        width: 100%;
      }
    `,
  ],
})
export class AdminPromotionsComponent implements OnInit {
  private auth = inject(AuthService);

  error = '';
  loading = false;
  showCreateForm = false;

  promotions: Promotion[] = [];
  products: Product[] = [];
  selectedProductIds = signal<Set<number>>(new Set());
  pendingDelete: Promotion | null = null;

  newPromotion = {
    name: '',
    description: '',
    discount_percent: 0,
    start_at: '',
    end_at: '',
  };

  trackById = (_: number, item: Promotion) => item.id;

  tableColumns: TableColumn[] = [
    { header: 'ID', property: 'id', cellSelector: '.id' },
    { header: 'Nombre', property: 'name', cellSelector: '.name' },
    { header: '% desc', property: 'discount_percent', cellSelector: '.discount' },
    { header: 'Inicio', property: 'start_at', cellSelector: '.start' },
    { header: 'Fin', property: 'end_at', cellSelector: '.end' },
    { header: 'Estado', property: 'status', cellSelector: '.status' },
  ];

  constructor() {}

  ngOnInit(): void {
    this.loadPromotions();
    this.loadProducts();
  }

  private headers(): Record<string, string> {
    return { Authorization: `Bearer ${this.auth.token()}` };
  }

  private api(path: string, init?: RequestInit): Promise<Response> {
    return fetch(`${environment.apiUrl}${path}`, {
      ...init,
      headers: this.headers(),
    });
  }

  private json(path: string): Promise<any> {
    return this.api(path).then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)));
  }

  loadPromotions(): void {
    this.loading = true;
    this.json('/promotions')
      .then((data) => (this.promotions = data.items ?? data))
      .catch((e) => (this.error = `No se pudieron cargar promociones: ${e}`))
      .finally(() => (this.loading = false));
  }

  loadProducts(): void {
    this.json('/products')
      .then((data) => (this.products = data))
      .catch((e) => (this.error = `No se pudieron cargar prendas: ${e}`));
  }

  toggleProduct(id: number): void {
    this.selectedProductIds.update((set) => {
      const next = new Set(set);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  createPromotion(): void {
    if (!this.newPromotion.name.trim() || !this.newPromotion.discount_percent) return;
    if (this.selectedProductIds().size === 0) {
      this.error = 'Debes seleccionar al menos una prenda.';
      return;
    }
    this.loading = true;
    const payload = {
      name: this.newPromotion.name,
      description: this.newPromotion.description || null,
      discount_percent: this.newPromotion.discount_percent,
      start_at: new Date(this.newPromotion.start_at).toISOString(),
      end_at: new Date(this.newPromotion.end_at).toISOString(),
      garment_ids: Array.from(this.selectedProductIds()),
    };
    this.api('/promotions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((r) => {
        if (!r.ok) return r.json().then((b: { detail?: string }) => Promise.reject(b.detail ?? r.statusText));
      })
      .then(() => {
        this.newPromotion = { name: '', description: '', discount_percent: 0, start_at: '', end_at: '' };
        this.selectedProductIds.set(new Set());
        this.showCreateForm = false;
        this.loadPromotions();
      })
      .catch((e) => (this.error = `No se pudo crear la promociÃ³n: ${e}`))
      .finally(() => (this.loading = false));
  }

  deletePromotion(p: Promotion): void {
    this.pendingDelete = p;
  }

  confirmDelete(): void {
    if (!this.pendingDelete) return;
    this.loading = true;
    const id = this.pendingDelete.id;
    this.api(`/promotions/${id}`, { method: 'DELETE' })
      .then((r) => {
        if (!r.ok) return r.json().then((b: { detail?: string }) => Promise.reject(b.detail ?? r.statusText));
      })
      .then(() => {
        this.pendingDelete = null;
        this.loadPromotions();
      })
      .catch((e) => (this.error = `No se pudo eliminar: ${e}`))
      .finally(() => (this.loading = false));
  }
}
