import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

@Component({
  selector: 'app-admin-products',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="products">
      <h2>Productos (CU-07)</h2>

      @if (error) {
        <p class="error">{{ error }}</p>
      }

      <form class="card" (ngSubmit)="createProduct()">
        <h3>Nueva prenda</h3>
        <select [(ngModel)]="newProduct.category_id" name="prod_cat" required>
          <option [ngValue]="0" disabled>Categoría...</option>
          @for (c of categories; track c.id) {
            <option [ngValue]="c.id">{{ c.name }}</option>
          }
        </select>
        <input [(ngModel)]="newProduct.name" name="prod_name" placeholder="Nombre de la prenda" required />
        <input [(ngModel)]="newProduct.base_price" name="prod_price" type="number" step="0.01" min="0" required />
        <label class="chip">
          <input type="checkbox" [(ngModel)]="newProduct.is_ar_enabled" name="prod_ar" />
          AR habilitado
        </label>
        <button type="submit" [disabled]="loading">Agregar</button>
      </form>
      <section class="card">
        <h3>Listado de prendas ({{ products.length }})</h3>
        <table>
          <thead>
            <tr><th>ID</th><th>Nombre</th><th>Categoría</th><th>Precio base</th><th>AR</th><th>Activo</th><th></th></tr>
          </thead>
          <tbody>
            @for (p of products; track p.id) {
              <tr>
                <td>{{ p.id }}</td>
                <td><input [(ngModel)]="p.name" name="p_name_{{ p.id }}" placeholder="Nombre" /></td>
                <td>{{ p.category_name || p.category?.name || '-' }}</td>
                <td><input [(ngModel)]="p.base_price" name="p_price_{{ p.id }}" type="number" step="0.01" /></td>
                <td>{{ p.is_ar_enabled ? 'Sí' : 'No' }}</td>
                <td>{{ p.is_active ? 'Sí' : 'No' }}</td>
                <td class="inline">
                  <button (click)="saveProduct(p)" [disabled]="loading">Guardar</button>
                  <button (click)="toggleProductActive(p)" [disabled]="loading">Activar/Desactivar</button>
                  <button class="danger" (click)="deleteProduct(p.id)" [disabled]="loading">Eliminar</button>
                </td>
              </tr>
            }
          </tbody>
        </table>
      </section>
    </section>
  `,
  styles: [
    `
      .products {
        max-width: 960px;
      }
      .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
      }
      .card input,
      .card select {
        display: block;
        margin-bottom: 0.5rem;
        padding: 0.4rem;
        width: 100%;
        box-sizing: border-box;
      }
      .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        margin-bottom: 0.5rem;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
      }
      th,
      td {
        border: 1px solid #ddd;
        padding: 0.4rem 0.6rem;
        text-align: left;
      }
      .inline {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
      }
      .inline input,
      .inline select {
        padding: 0.35rem;
      }
      button {
        cursor: pointer;
      }
      .danger {
        color: #b00020;
      }
      .error {
        color: #b00020;
      }
    `,
  ],
})
export class AdminProductsComponent implements OnInit {
  private auth = inject(AuthService);

  error = '';
  loading = false;
  products: any[] = [];
  categories: { id: number; name: string }[] = [];

  newProduct = {
    category_id: 1,
    name: '',
    base_price: 0,
    is_ar_enabled: false,
  };

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
        this.loadProducts();
      })
      .catch((e) => (this.error = `No se pudo crear el producto: ${e}`))
      .finally(() => (this.loading = false));
  }

  saveProduct(p: any): void {
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

  toggleProductActive(p: any): void {
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