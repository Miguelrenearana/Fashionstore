import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';
import { UiButtonComponent } from '@shared/ui/button';

@Component({
  selector: 'app-admin-catalog-config',
  standalone: true,
  imports: [CommonModule, FormsModule, UiButtonComponent],
  template: `
    <section class="catalog-config container py-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-semibold">Configuración de Catálogo</h2>
        <span class="text-sm text-secondary">CU-06 · CU-08 · CU-09 · CU-10</span>
      </div>

      @if (error) {
        <div class="alert alert-error mb-4">{{ error }}</div>
      }

      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <form class="card p-4" (ngSubmit)="createSize()">
          <h3 class="text-lg font-semibold mb-4">Tallas</h3>
          <div class="form-field mb-2">
            <label class="form-label" for="cc_size">Nombre</label>
            <input id="cc_size" class="form-input" [(ngModel)]="newSize" name="size" placeholder="Nueva talla" required />
          </div>
          <ui-button variant="primary" type="submit" size="sm" [disabled]="loading">Agregar</ui-button>
          <ul class="list">
            @for (s of sizes; track s.id) {
              <li>{{ s.name }}</li>
            } @empty {
              <li class="text-muted">Sin tallas</li>
            }
          </ul>
        </form>

        <form class="card p-4" (ngSubmit)="createColor()">
          <h3 class="text-lg font-semibold mb-4">Colores</h3>
          <div class="form-field mb-2">
            <label class="form-label" for="cc_color">Nombre</label>
            <input id="cc_color" class="form-input" [(ngModel)]="newColor" name="color" placeholder="Nuevo color" required />
          </div>
          <ui-button variant="primary" type="submit" size="sm" [disabled]="loading">Agregar</ui-button>
          <ul class="list">
            @for (c of colors; track c.id) {
              <li>{{ c.name }} @if (c.hex_code) { <span class="text-muted">({{ c.hex_code }})</span> }</li>
            } @empty {
              <li class="text-muted">Sin colores</li>
            }
          </ul>
        </form>

        <form class="card p-4" (ngSubmit)="createSeason()">
          <h3 class="text-lg font-semibold mb-4">Temporadas</h3>
          <div class="form-field mb-2">
            <label class="form-label" for="cc_season">Nombre</label>
            <input id="cc_season" class="form-input" [(ngModel)]="newSeason" name="season" placeholder="Nueva temporada" required />
          </div>
          <ui-button variant="primary" type="submit" size="sm" [disabled]="loading">Agregar</ui-button>
          <ul class="list">
            @for (s of seasons; track s.id) {
              <li>{{ s.name }}</li>
            } @empty {
              <li class="text-muted">Sin temporadas</li>
            }
          </ul>
        </form>

        <form class="card p-4" (ngSubmit)="createCategory()">
          <h3 class="text-lg font-semibold mb-4">Categorías</h3>
          <div class="form-field mb-2">
            <label class="form-label" for="cc_cat">Nombre</label>
            <input id="cc_cat" class="form-input" [(ngModel)]="newCategory.name" name="cat_name" placeholder="Nueva categoría" required />
          </div>
          <ui-button variant="primary" type="submit" size="sm" [disabled]="loading">Agregar</ui-button>
          <ul class="list">
            @for (c of categories; track c.id) {
              <li>{{ c.name }}</li>
            } @empty {
              <li class="text-muted">Sin categorías</li>
            }
          </ul>
        </form>

        <form class="card p-4" (ngSubmit)="createCollection()">
          <h3 class="text-lg font-semibold mb-4">Colecciones</h3>
          <div class="form-field mb-2">
            <label class="form-label" for="cc_col">Nombre</label>
            <input id="cc_col" class="form-input" [(ngModel)]="newCollection.name" name="col_name" placeholder="Nueva colección" required />
          </div>
          <div class="form-field mb-2">
            <label class="form-label" for="cc_col_season">Temporada</label>
            <select id="cc_col_season" class="form-input" [(ngModel)]="newCollection.season_id" name="col_season" required>
              <option [ngValue]="0" disabled>Temporada...</option>
              @for (s of seasons; track s.id) {
                <option [ngValue]="s.id">{{ s.name }}</option>
              }
            </select>
          </div>
          <ui-button variant="primary" type="submit" size="sm" [disabled]="loading">Agregar</ui-button>
          <ul class="list">
            @for (c of collections; track c.id) {
              <li>{{ c.name }} ({{ c.launch_year }})</li>
            } @empty {
              <li class="text-muted">Sin colecciones</li>
            }
          </ul>
        </form>

        <form class="card p-4" (ngSubmit)="createSupplier()">
          <h3 class="text-lg font-semibold mb-4">Proveedores</h3>
          <div class="form-field mb-2">
            <label class="form-label" for="cc_sup">Empresa</label>
            <input id="cc_sup" class="form-input" [(ngModel)]="newSupplier.company_name" name="sup_name" placeholder="Empresa" required />
          </div>
          <div class="form-field mb-2">
            <label class="form-label" for="cc_sup_contact">Contacto</label>
            <input id="cc_sup_contact" class="form-input" [(ngModel)]="newSupplier.contact_name" name="sup_contact" placeholder="Contacto" />
          </div>
          <ui-button variant="primary" type="submit" size="sm" [disabled]="loading">Agregar</ui-button>
          <ul class="list">
            @for (s of suppliers; track s.id) {
              <li>{{ s.company_name }}</li>
            } @empty {
              <li class="text-muted">Sin proveedores</li>
            }
          </ul>
        </form>
      </div>
    </section>
  `,
  styles: [
    `
      .list {
        margin: var(--space-3) 0 0;
        padding-left: 1.1rem;
        font-size: var(--text-sm);
        color: var(--color-text);
      }
      .text-muted {
        color: var(--color-text-muted);
      }
    `,
  ],
})
export class AdminCatalogConfigComponent implements OnInit {
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