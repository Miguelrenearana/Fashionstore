import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface Role {
  id: number;
  name: string;
  description?: string;
}

interface User {
  id: number;
  email: string;
  phone?: string;
  is_active: boolean;
  roles: Role[];
}

interface Branch {
  id: number;
  name: string;
}

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="admin">
      <h2>Panel de administración</h2>

      @if (error) {
        <p class="error">{{ error }}</p>
      }

      <form class="card" (ngSubmit)="createUser()">
        <h3>Nuevo usuario</h3>
        <input [(ngModel)]="newUser.email" name="email" type="email" placeholder="email@fashionstore.dev" required />
        <input [(ngModel)]="newUser.password" name="password" type="password" placeholder="Contraseña" required />
        <input [(ngModel)]="newUser.phone" name="phone" type="text" placeholder="Teléfono (opcional)" />
        <div class="roles">
          @for (role of roles; track role.id) {
            <label class="chip">
              <input type="checkbox" [checked]="newUser.roles.includes(role.name)"
                     (change)="toggleRole(role.name)" />
              {{ role.name }}
            </label>
          }
        </div>
        <button type="submit" [disabled]="loading">Crear usuario</button>
      </form>

      <h3>Empleados ({{ users.length }})</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Roles</th>
            <th>Activo</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          @for (user of users; track user.id) {
            <tr>
              <td>{{ user.id }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.phone || '-' }}</td>
              <td>{{ roleNames(user) }}</td>
              <td>{{ user.is_active ? 'Sí' : 'No' }}</td>
              <td>
                <button class="link" (click)="toggleEmployeeForm(user.id)">Vincular empleado</button>
              </td>
            </tr>
            @if (employeeFormFor === user.id) {
              <tr>
                <td colspan="6">
                  <form class="inline" (ngSubmit)="linkEmployee(user.id)">
                    <input [(ngModel)]="employee.first_name" name="first_name" placeholder="Nombre" required />
                    <input [(ngModel)]="employee.last_name" name="last_name" placeholder="Apellido" required />
                    <select [(ngModel)]="employee.branch_id" name="branch_id" required>
                      <option [ngValue]="0" disabled>Sucursal...</option>
                      @for (branch of branches; track branch.id) {
                        <option [ngValue]="branch.id">{{ branch.name }}</option>
                      }
                    </select>
                    <input [(ngModel)]="employee.hire_date" name="hire_date" type="date" />
                    <button type="submit" [disabled]="loading">Guardar</button>
                  </form>
                </td>
              </tr>
            }
          }
        </tbody>
      </table>

      <h3>Gestión de catálogo</h3>
      <div class="grid">
        <form class="card" (ngSubmit)="createSize()">
          <h4>Tallas</h4>
          <input [(ngModel)]="newSize" name="size" placeholder="Nueva talla" required />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (s of sizes; track s.id) { <li>{{ s.name }}</li> }</ul>
        </form>
        <form class="card" (ngSubmit)="createColor()">
          <h4>Colores</h4>
          <input [(ngModel)]="newColor" name="color" placeholder="Nuevo color" required />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (c of colors; track c.id) { <li>{{ c.name }} @if (c.hex_code) { <span>({{ c.hex_code }})</span> }</li> }</ul>
        </form>
        <form class="card" (ngSubmit)="createSeason()">
          <h4>Temporadas</h4>
          <input [(ngModel)]="newSeason" name="season" placeholder="Nueva temporada" required />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (s of seasons; track s.id) { <li>{{ s.name }}</li> }</ul>
        </form>
        <form class="card" (ngSubmit)="createCategory()">
          <h4>Categorías</h4>
          <input [(ngModel)]="newCategory.name" name="cat_name" placeholder="Nueva categoría" required />
          <button type="submit" [disabled]="loading">Agregar</button>
          <ul>@for (c of categories; track c.id) { <li>{{ c.name }}</li> }</ul>
        </form>
        <form class="card" (ngSubmit)="createCollection()">
          <h4>Colecciones</h4>
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
          <h4>Proveedores</h4>
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
      .admin {
        padding: 1.5rem;
        max-width: 960px;
        margin: 0 auto;
      }
      .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
      }
      .card input {
        display: block;
        margin-bottom: 0.5rem;
        padding: 0.4rem;
        width: 100%;
        box-sizing: border-box;
      }
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
      .roles {
        margin-bottom: 0.75rem;
      }
      .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        border: 1px solid #ccc;
        border-radius: 16px;
        padding: 0.25rem 0.6rem;
        margin-right: 0.4rem;
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
      .link {
        background: none;
        border: none;
        color: var(--color-primary);
        text-decoration: underline;
      }
      .error {
        color: #b00020;
      }
    `,
  ],
})
export class AdminComponent implements OnInit {
  private auth = inject(AuthService);

  users: User[] = [];
  roles: Role[] = [];
  branches: Branch[] = [];
  error = '';
  loading = false;
  employeeFormFor: number | null = null;

  newUser = { email: '', password: '', phone: '', roles: [] as string[] };
  employee = { first_name: '', last_name: '', branch_id: 0, hire_date: '' };

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
    this.loadUsers();
    this.loadRoles();
    this.loadBranches();
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

  loadUsers(): void {
    this.api('/users')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data) => (this.users = data))
      .catch((e) => (this.error = `No se pudieron cargar usuarios: ${e}`));
  }

  loadRoles(): void {
    this.api('/users/roles')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data) => (this.roles = data))
      .catch((e) => (this.error = `No se pudieron cargar roles: ${e}`));
  }

  loadBranches(): void {
    this.api('/locations/branches')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data) => (this.branches = data))
      .catch((e) => (this.error = `No se pudieron cargar sucursales: ${e}`));
  }

  toggleRole(name: string): void {
    const idx = this.newUser.roles.indexOf(name);
    if (idx >= 0) {
      this.newUser.roles.splice(idx, 1);
    } else {
      this.newUser.roles.push(name);
    }
  }

  roleNames(user: User): string {
    return user.roles.map((r) => r.name).join(', ');
  }

  toggleEmployeeForm(userId: number): void {
    this.employeeFormFor = this.employeeFormFor === userId ? null : userId;
    this.employee = { first_name: '', last_name: '', branch_id: 0, hire_date: '' };
  }

  createUser(): void {
    this.loading = true;
    this.api('/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(this.newUser),
    })
      .then((r) => {
        if (!r.ok) {
          return r.json().then((b: { detail?: string }) => Promise.reject(b.detail ?? r.statusText));
        }
        return r.json();
      })
      .then(() => {
        this.newUser = { email: '', password: '', phone: '', roles: [] };
        this.loadUsers();
      })
      .catch((e) => (this.error = `No se pudo crear el usuario: ${e}`))
      .finally(() => (this.loading = false));
  }

  linkEmployee(userId: number): void {
    this.loading = true;
    this.api(`/users/${userId}/employee`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(this.employee),
    })
      .then((r) => {
        if (!r.ok) {
          return r.json().then((b: { detail?: string }) => Promise.reject(b.detail ?? r.statusText));
        }
        return r.json();
      })
      .then(() => (this.employeeFormFor = null))
      .catch((e) => (this.error = `No se pudo vincular el empleado: ${e}`))
      .finally(() => (this.loading = false));
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

  private json(path: string): Promise<any> {
    return this.api(path).then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)));
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