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
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="users">
      <h2>Usuarios y roles (CU-04)</h2>

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
    </section>
  `,
  styles: [
    `
      .users {
        max-width: 960px;
      }
      .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        max-width: 520px;
      }
      .card input {
        display: block;
        margin-bottom: 0.5rem;
        padding: 0.4rem;
        width: 100%;
        box-sizing: border-box;
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
export class AdminUsersComponent implements OnInit {
  private auth = inject(AuthService);

  users: User[] = [];
  roles: Role[] = [];
  branches: Branch[] = [];
  error = '';
  loading = false;
  employeeFormFor: number | null = null;

  newUser = { email: '', password: '', phone: '', roles: [] as string[] };
  employee = { first_name: '', last_name: '', branch_id: 0, hire_date: '' };

  ngOnInit(): void {
    this.loadUsers();
    this.loadRoles();
    this.loadBranches();
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
}