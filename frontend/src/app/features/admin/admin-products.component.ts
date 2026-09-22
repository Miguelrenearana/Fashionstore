import { Component, inject, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';
import { UiButtonComponent } from '@shared/ui/button';
import { UiInputComponent } from '@shared/ui/input';
import { UiSelectComponent } from '@shared/ui/select';
import { UiTableComponent } from '@shared/ui/table';
import { UiCardComponent } from '@shared/ui/card';

interface Product {
  id: number;
  name: string;
  base_price: number;
  category_id: number;
  category_name?: string;
  is_ar_enabled: boolean;
  is_active: boolean;
}

interface Category {
  id: number;
  name: string;
}

@Component({
  selector: 'app-admin-products',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    UiButtonComponent,
    UiInputComponent,
    UiSelectComponent,
    UiTableComponent,
    UiCardComponent,
  ],
  template: `
    <section class="products container py-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-semibold">Productos (CU-07)</h2>
        <ui-button variant="primary" (click)="showCreateForm = true" size="md">
          + Nueva prenda
        </ui-button>
      </div>

      @if (error) {
        <div class="alert alert-error mb-4">{{ error }}</div>
      }

      @if (showCreateForm) {
        <ui-card class="mb-6 p-4">
          <h3 class="text-lg font-semibold mb-4">Nueva prenda</h3>
          <form (ngSubmit)="createProduct()" class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <ui-select
              [options]="categoryOptions()"
              [(ngModel)]="newProduct.category_id"
              name="prod_cat"
              [required]="true"
              placeholder="Categoría..."
              label="Categoría"
            />
            <ui-input
              label="Nombre"
              placeholder="Nombre de la prenda"
              [(ngModel)]="newProduct.name"
              name="prod_name"
              required
            />
            <ui-input
              label="Precio base"
              type="number"
              step="0.01"
              min="0"
              [(ngModel)]="newProduct.base_price"
              name="prod_price"
              required
            />
            <div class="md:col-span-4 flex items-center gap-2">
              <input
                type="checkbox"
                id="prod_ar"
                [(ngModel)]="newProduct.is_ar_enabled"
                name="prod_ar"
                class="form-checkbox"
              />
              <label for="prod_ar" class="text-sm">AR habilitado</label>
            </div>
            <div class="md:col-span-4 flex justify-end gap-2 pt-2">
              <ui-button variant="secondary" type="button" (click)="showCreateForm = false">
                Cancelar
              </ui-button>
              <ui-button variant="primary" type="submit" [disabled]="loading" [loading]="loading">
                {{ loading ? 'Guardando...' : 'Agregar' }}
              </ui-button>
            </div>
          </form>
        </ui-card>
      }

      <ui-card class="mb-6">
        <div class="card-header flex justify-between items-center">
          <h3 class="text-lg font-semibold">Listado de prendas ({{ products.length }})</h3>
        </div>
        <ui-table
          [columns]="tableColumns"
          [items]="products"
          [trackByItem]="trackById"
          emptyMessage="No hay productos"
        />
      </ui-card>
    </section>
  `,
  styles: []
})
export class AdminProductsComponent implements OnInit {
  private auth = inject(AuthService);

  error = '';
  loading = false;
  showCreateForm = false;

  products: Product[] = [];
  categories: Category[] = [];

  newProduct = {
    category_id: 1,
    name: '',
    base_price: 0,
    is_ar_enabled: false,
  };

  trackById = (_: number, item: Product) => item.id;

  categoryOptions = computed(() => 
    this.categories.map(c => ({ value: String(c.id), label: c.name }))
  );

  tableColumns = [
    { header: 'ID', property: 'id', cellSelector: '.id' },
    { header: 'Nombre', property: 'name', cellSelector: '.name' },
    { header: 'Categoría', property: 'category_name', cellSelector: '.category' },
    { header: 'Precio base', property: 'base_price', cellSelector: '.price' },
    { header: 'AR', property: 'is_ar_enabled', cellSelector: '.ar' },
    { header: 'Activo', property: 'is_active', cellSelector: '.active' },
    { header: 'Acciones', property: 'actions', cellSelector: '.actions' },
  ];

  constructor() {}

  ngOnInit(): void {
    this.loadProducts();
    this.loadCategories();
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

  loadProducts(): void {
    this.json('/products')
      .then((data) => (this.products = data))
      .catch((e) => (this.error = `No se pudieron cargar productos: ${e}`));
  }

  loadCategories(): void {
    this.json('/catalog/options/categories')
      .then((data) => {
        this.categories = data;
        if (data.length && !data.some((c: { id: number }) => c.id === this.newProduct.category_id)) {
          this.newProduct.category_id = data[0].id;
        }
      })
      .catch((e) => (this.error = `No se pudieron cargar categorías: ${e}`));
  }

  createProduct(): void {
    if (!this.newProduct.name.trim() || !this.newProduct.base_price) return;
    this.loading = true;
    const payload = { ...this.newProduct };
    this.api('/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((r) => {
        if (!r.ok) return r.json().then((b: { detail?: string }) => Promise.reject(b.detail ?? r.statusText));
      })
      .then(() => {
        this.newProduct = { category_id: 1, name: '', base_price: 0, is_ar_enabled: false };
        this.showCreateForm = false;
        this.loadProducts();
      })
      .catch((e) => (this.error = `No se pudo crear el producto: ${e}`))
      .finally(() => (this.loading = false));
  }

  saveProduct(p: Product): void {
    this.loading = true;
    this.api(`/products/${p.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: p.name,
        base_price: p.base_price,
        is_ar_enabled: p.is_ar_enabled,
      }),
    })
      .then((r) => {
        if (!r.ok) return r.json().then((b: { detail?: string }) => Promise.reject(b.detail ?? r.statusText));
      })
      .then(() => this.loadProducts())
      .catch((e) => (this.error = `No se pudo guardar: ${e}`))
      .finally(() => (this.loading = false));
  }

  toggleProductActive(p: Product): void {
    this.loading = true;
    this.api(`/products/${p.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: !p.is_active }),
    })
      .then((r) => {
        if (!r.ok) return r.json().then((b: { detail?: string }) => Promise.reject(b.detail ?? r.statusText));
      })
      .then(() => this.loadProducts())
      .catch((e) => (this.error = `No se pudo cambiar el estado: ${e}`))
      .finally(() => (this.loading = false));
  }

  deleteProduct(id: number): void {
    if (!confirm('¿Desactivar esta prenda? (soft delete)')) return;
    this.loading = true;
    this.api(`/products/${id}`, { method: 'DELETE' })
      .then((r) => {
        if (!r.ok) return r.json().then((b: { detail?: string }) => Promise.reject(b.detail ?? r.statusText));
      })
      .then(() => this.loadProducts())
      .catch((e) => (this.error = `No se pudo desactivar: ${e}`))
      .finally(() => (this.loading = false));
  }
}