import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

@Component({
  selector: 'app-admin-catalog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="catalog-admin">
      <h2>Catálogo (CU-06 · CU-08 · CU-09 · CU-10 · CU-11)</h2>

      @if (error) {
        <p class="error">{{ error }}</p>
      }

      <div class="grid">
        <form class="card" (ngSubmit)="createSize()">
          <h3>Tallas</h3>
          <input [(ngModel)]="newSize" name="size" placeholder="Nueva talla" required />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (s of sizes; track s.id) { <li>{{ s.name }}</li> }</ul>
        </form>
        <form class="card" (ngSubmit)="createColor()">
          <h3>Colores</h3>
          <input [(ngModel)]="newColor" name="color" placeholder="Nuevo color" required />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (c of colors; track c.id) { <li>{{ c.name }} @if (c.hex_code) { <span>({{ c.hex_code }})</span> }</li> }</ul>
        </form>
        <form class="card" (ngSubmit)="createSeason()">
          <h3>Temporadas</h3>
          <input [(ngModel)]="newSeason" name="season" placeholder="Nueva temporada" required />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (s of seasons; track s.id) { <li>{{ s.name }}</li> }</ul>
        </form>
        <form class="card" (ngSubmit)="createCategory()">
          <h3>Categorías</h3>
          <input [(ngModel)]="newCategory.name" name="cat_name" placeholder="Nueva categoría" required />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (c of categories; track c.id) { <li>{{ c.name }}</li> }</ul>
        </form>
        <form class="card" (ngSubmit)="createCollection()">
          <h3>Colecciones</h3>
          <input [(ngModel)]="newCollection.name" name="col_name" placeholder="Nueva colección" required />
          <select [(ngModel)]="newCollection.season_id" name="col_season" required>
            <option [ngValue]="0" disabled>Temporada...</option>
            @for (s of seasons; track s.id) {
              <option [ngValue]="s.id">{{ s.name }}</option>
            }
          </select>
          <input [(ngModel)]="newCollection.launch_year" name="col_year" type="number" required />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (c of collections; track c.id) { <li>{{ c.name }} ({{ c.launch_year }})</li> }</ul>
        </form>
        <form class="card" (ngSubmit)="createSupplier()">
          <h3>Proveedores</h3>
          <input [(ngModel)]="newSupplier.company_name" name="sup_name" placeholder="Empresa" required />
          <input [(ngModel)]="newSupplier.contact_name" name="sup_contact" placeholder="Contacto" />
          <input [(ngModel)]="newSupplier.email" name="sup_email" type="email" placeholder="Correo" />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (s of suppliers; track s.id) { <li>{{ s.company_name }}</li> }</ul>
        </form>
      </div>
    </section>
  `,
  styles: [
    `
      .catalog-admin {
        max-width: 1100px;
      }
      .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
      }
      .card input,
      .card select {
        display: block;
        margin-bottom: 0.5rem;
        padding: 0.4rem;
        width: 100%;
        box-sizing: border-box;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1rem;
      }
      .grid ul {
        margin: 0.5rem 0 0;
        padding-left: 1.1rem;
        font-size: 0.85rem;
      }
      button {
        cursor: pointer;
      }
      .error {
        color: #b00020;
      }
    `,
  ],
})
export class AdminCatalogComponent implements OnInit {
  private auth = inject(AuthService);

  error = '';
  loading = false;

  sizes: { id: number; name: string }[] = [];
  colors: { id: number; name: string; hex_code?: string | null }[] = [];
  seasons: { id: number; name: string }[] = [];
  categories: { id: number; name: string }[] = [];
  collections: { id: number; name: string; launch_year: number }[] = [];
  suppliers: { id: number; company_name: string; contact_name?: string | null }[] = [];
  newSize = '';
  newColor = '';
  newSeason = '';
  newCategory = { name: '', description: '' };
  newCollection = { season_id: 0, name: '', launch_year: new Date().getFullYear() };
  newSupplier = { company_name: '', contact_name: '', email: '' };

  ngOnInit(): void {
    this.loadOptions();
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

  loadOptions(): void {
    Promise.all([
      this.json('/catalog/options/sizes'),
      this.json('/catalog/options/colors'),
      this.json('/catalog/options/seasons'),
      this.json('/catalog/options/categories'),
      this.json('/catalog/options/collections'),
      this.json('/suppliers'),
    ])
      .then(([sizes, colors, seasons, categories, collections, suppliers]) => {
        this.sizes = sizes;
        this.colors = colors;
        this.seasons = seasons;
        this.categories = categories;
        this.collections = collections;
        this.suppliers = suppliers;
      })
      .catch((e) => (this.error = `No se pudieron cargar opciones: ${e}`));
  }

  private create(path: string, payload: unknown): void {
    this.loading = true;
    this.api(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((r) => {
        if (!r.ok) {
          return r.json().then((b: { detail?: string }) => Promise.reject(b.detail ?? r.statusText));
        }
        return r.json();
      })
      .then(() => this.loadOptions())
      .catch((e) => (this.error = `No se pudo guardar: ${e}`))
      .finally(() => (this.loading = false));
  }

  createSize(): void {
    if (this.newSize.trim()) {
      const name = this.newSize.trim();
      this.create('/catalog/options/sizes', { name });
      this.newSize = '';
    }
  }

  createColor(): void {
    if (this.newColor.trim()) {
      const name = this.newColor.trim();
      this.create('/catalog/options/colors', { name });
      this.newColor = '';
    }
  }

  createSeason(): void {
    if (this.newSeason.trim()) {
      const name = this.newSeason.trim();
      this.create('/catalog/options/seasons', { name });
      this.newSeason = '';
    }
  }

  createCategory(): void {
    if (this.newCategory.name.trim()) {
      this.create('/catalog/options/categories', { ...this.newCategory });
      this.newCategory = { name: '', description: '' };
    }
  }

  createCollection(): void {
    if (this.newCollection.season_id && this.newCollection.name.trim()) {
      this.create('/catalog/options/collections', { ...this.newCollection });
      this.newCollection = {
        season_id: 0,
        name: '',
        launch_year: new Date().getFullYear(),
      };
    }
  }

  createSupplier(): void {
    if (this.newSupplier.company_name.trim()) {
      this.create('/suppliers', { ...this.newSupplier });
      this.newSupplier = { company_name: '', contact_name: '', email: '' };
    }
  }
}