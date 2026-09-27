import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface Role {
  id: number;
  name: string;
  description: string | null;
}

interface UserRow {
  id: number;
  email: string;
  phone: string | null;
  is_active: boolean;
  is_verified: boolean;
  full_name: string | null;
  roles: Role[];
}

interface BranchOption {
  id: number;
  name: string;
}

/** Etiquetas legibles para los roles reales del seed. */
const ROLE_LABELS: Record<string, string> = {
  ADMIN: 'Administrador (A2)',
  MANAGER: 'Encargado de sucursal (A3)',
  CASHIER: 'Cajero (A4)',
  CLIENT: 'Cliente (A1)',
  SUPPLIER: 'Proveedor (AS1)',
};

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="users-admin">
      <h2>Usuarios y roles (CU-04)</h2>

      @if (error()) {
        <p class="alert error" role="alert">{{ error() }}</p>
      }
      @if (info()) {
        <p class="alert ok" role="status">{{ info() }}</p>
      }

      <div class="layout">
        <article class="panel">
          <h3>Registrar usuario</h3>
          <form (ngSubmit)="createUser()" autocomplete="off">
            <label class="field">
              <span>Email</span>
              <input type="email" name="email" required [(ngModel)]="draft.email" placeholder="usuario@ejemplo.com" />
            </label>
            <label class="field">
              <span>Contraseña</span>
              <input
                type="password"
                name="password"
                required
                minlength="6"
                [(ngModel)]="draft.password"
                placeholder="Mínimo 6 caracteres"
              />
            </label>
            <label class="field">
              <span>Teléfono</span>
              <input type="tel" name="phone" [(ngModel)]="draft.phone" placeholder="Opcional" />
            </label>
            <div class="pair">
              <label class="field">
                <span>Nombre</span>
                <input type="text" name="firstName" [(ngModel)]="draft.firstName" placeholder="Del empleado" />
              </label>
              <label class="field">
                <span>Apellido</span>
                <input type="text" name="lastName" [(ngModel)]="draft.lastName" placeholder="Del empleado" />
              </label>
            </div>

            <fieldset class="roles">
              <legend>Roles</legend>
              @for (role of roles(); track role.id) {
                <label class="check">
                  <input
                    type="checkbox"
                    [value]="role.name"
                    [checked]="draft.roles.includes(role.name)"
                    (change)="toggleRole(role.name, $event)"
                  />
                  <span>{{ label(role.name) }}</span>
                </label>
              } @empty {
                <p class="muted">Cargando roles…</p>
              }
            </fieldset>

            <label class="field">
              <span>Sucursal (solo personal)</span>
              <select name="branch" [(ngModel)]="draft.branchId">
                <option [ngValue]="null">Sin asignar</option>
                @for (b of branches(); track b.id) {
                  <option [ngValue]="b.id">{{ b.name }}</option>
                }
              </select>
            </label>

            <button class="btn btn-primary w-full" type="submit" [disabled]="busy()">
              {{ busy() ? 'Guardando…' : 'Registrar usuario' }}
            </button>
          </form>
        </article>

        <article class="panel">
          <div class="panel-head">
            <h3>Consultar usuarios</h3>
            <input
              type="search"
              class="search"
              placeholder="Filtrar por email, nombre o rol"
              [value]="filter()"
              (input)="filter.set($any($event.target).value)"
            />
          </div>

          <p class="muted">{{ filtered().length }} de {{ users().length }} usuarios</p>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Roles</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                @for (u of filtered(); track u.id) {
                  <tr [class.inactive]="!u.is_active">
                    <td>
                      <strong>{{ u.full_name || '—' }}</strong>
                      <small>{{ u.email }}</small>
                      @if (u.phone) {
                        <small>{{ u.phone }}</small>
                      }
                    </td>
                    <td>
                      @for (r of u.roles; track r.id) {
                        <span class="chip">{{ label(r.name) }}</span>
                      } @empty {
                        <span class="muted">Sin roles</span>
                      }
                    </td>
                    <td>
                      <span class="badge" [class.on]="u.is_active">
                        {{ u.is_active ? 'Activo' : 'Deshabilitado' }}
                      </span>
                    </td>
                    <td class="actions">
                      <button type="button" class="link" (click)="startEdit(u)">Editar</button>
                      <button type="button" class="link" (click)="toggleActive(u)" [disabled]="busy()">
                        {{ u.is_active ? 'Deshabilitar' : 'Habilitar' }}
                      </button>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="4" class="muted">No hay usuarios que coincidan.</td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </article>
      </div>

      @if (editing(); as u) {
        <article class="panel edit">
          <h3>Actualizar usuario #{{ u.id }}</h3>
          <div class="edit-grid">
            <label class="field">
              <span>Teléfono</span>
              <input type="tel" [value]="edit.phone" (input)="edit.phone = $any($event.target).value" />
            </label>
            <div class="field">
              <span>Roles</span>
              @for (role of roles(); track role.id) {
                <label class="check">
                  <input
                    type="checkbox"
                    [checked]="edit.roles.includes(role.name)"
                    (change)="toggleEditRole(role.name, $event)"
                  />
                  <span>{{ label(role.name) }}</span>
                </label>
              }
            </div>
          </div>
          <div class="edit-actions">
            <button class="btn btn-primary" (click)="saveEdit()" [disabled]="busy()">Guardar cambios</button>
            <button class="btn" (click)="cancelEdit()">Cancelar</button>
          </div>
        </article>
      }
    </section>
  `,
  styles: [
    `
      .users-admin {
        max-width: 1200px;
      }
      h2 {
        margin-top: 0;
      }
      .layout {
        display: grid;
        grid-template-columns: 320px 1fr;
        gap: 1.5rem;
        align-items: start;
      }
      .panel {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem;
        background: #fff;
      }
      .panel h3 {
        margin-top: 0;
      }
      .panel-head {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
      }
      .search {
        padding: 0.45rem 0.6rem;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        min-width: 220px;
      }
      .field {
        display: block;
        margin-bottom: 0.75rem;
      }
      .field > span {
        display: block;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: #334155;
      }
      .field input,
      .field select {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        box-sizing: border-box;
      }
      .pair {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
      }
      .roles {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin: 0 0 0.75rem;
      }
      .roles legend {
        font-size: 0.8rem;
        font-weight: 600;
        color: #334155;
      }
      .check {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.85rem;
        margin: 0.15rem 0;
      }
      .table-wrap {
        overflow-x: auto;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
      }
      th,
      td {
        border-bottom: 1px solid #e2e8f0;
        padding: 0.5rem;
        text-align: left;
        vertical-align: top;
      }
      td small {
        display: block;
        color: #64748b;
      }
      tr.inactive {
        opacity: 0.55;
      }
      .chip {
        display: inline-block;
        background: #f1f5f9;
        border-radius: 999px;
        padding: 0.1rem 0.5rem;
        font-size: 0.72rem;
        margin: 0 0.25rem 0.25rem 0;
      }
      .badge {
        display: inline-block;
        border-radius: 999px;
        padding: 0.1rem 0.55rem;
        font-size: 0.75rem;
        background: #fee2e2;
        color: #991b1b;
      }
      .badge.on {
        background: #dcfce7;
        color: #166534;
      }
      .actions {
        white-space: nowrap;
      }
      .link {
        background: none;
        border: none;
        color: var(--color-primary-dark, #cc7000);
        cursor: pointer;
        padding: 0 0.35rem;
        text-decoration: underline;
      }
      .alert {
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        font-size: 0.85rem;
      }
      .alert.error {
        background: #fee2e2;
        color: #991b1b;
      }
      .alert.ok {
        background: #dcfce7;
        color: #166534;
      }
      .muted {
        color: #64748b;
        font-size: 0.85rem;
      }
      .edit {
        margin-top: 1.5rem;
      }
      .edit-grid {
        display: grid;
        grid-template-columns: 260px 1fr;
        gap: 1rem;
      }
      .edit-actions {
        display: flex;
        gap: 0.5rem;
      }
      button {
        cursor: pointer;
      }
      @media (max-width: 900px) {
        .layout,
        .edit-grid {
          grid-template-columns: 1fr;
        }
      }
    `,
  ],
})
export class AdminUsersComponent implements OnInit {
  private auth = inject(AuthService);

  readonly users = signal<UserRow[]>([]);
  readonly roles = signal<Role[]>([]);
  readonly branches = signal<BranchOption[]>([]);
  readonly busy = signal(false);
  readonly error = signal('');
  readonly info = signal('');
  readonly filter = signal('');
  readonly editing = signal<UserRow | null>(null);

  draft = {
    email: '',
    password: '',
    phone: '',
    firstName: '',
    lastName: '',
    roles: [] as string[],
    branchId: null as number | null,
  };
  edit = { phone: '', roles: [] as string[] };

  ngOnInit(): void {
    this.loadRoles();
    this.loadUsers();
    this.loadBranches();
  }

  label(role: string): string {
    return ROLE_LABELS[role] ?? role;
  }

  private headers(): Record<string, string> {
    return { 'Content-Type': 'application/json', Authorization: `Bearer ${this.auth.token()}` };
  }

  private api(path: string, init?: RequestInit): Promise<Response> {
    return fetch(`${environment.apiUrl}${path}`, { ...init, headers: this.headers() });
  }

  private json(path: string): Promise<any> {
    return this.api(path).then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)));
  }

  private fail(prefix: string, e: unknown): void {
    const detail = e instanceof Error ? e.message : String(e);
    this.error.set(`${prefix}: ${detail}`);
    this.info.set('');
  }

  loadRoles(): void {
    this.json('/users/roles')
      .then((data: Role[]) => this.roles.set(data))
      .catch((e) => this.fail('No se pudieron cargar los roles', e));
  }

  loadUsers(): void {
    this.json('/users?size=200')
      .then((data: UserRow[]) => this.users.set(data))
      .catch((e) => this.fail('No se pudieron cargar los usuarios', e));
  }

  loadBranches(): void {
    this.api('/locations/branches')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: BranchOption[]) => this.branches.set(data))
      .catch(() => this.branches.set([]));
  }

  filtered(): UserRow[] {
    const q = this.filter().trim().toLowerCase();
    if (!q) return this.users();
    return this.users().filter((u) => {
      const haystack = [
        u.email,
        u.full_name ?? '',
        u.phone ?? '',
        ...u.roles.map((r) => r.name),
      ]
        .join(' ')
        .toLowerCase();
      return haystack.includes(q);
    });
  }

  toggleRole(name: string, event: Event): void {
    const on = (event.target as HTMLInputElement).checked;
    this.draft.roles = on
      ? [...this.draft.roles, name]
      : this.draft.roles.filter((r) => r !== name);
  }

  toggleEditRole(name: string, event: Event): void {
    const on = (event.target as HTMLInputElement).checked;
    this.edit.roles = on ? [...this.edit.roles, name] : this.edit.roles.filter((r) => r !== name);
  }

  createUser(): void {
    if (!this.draft.email.trim() || !this.draft.password) {
      this.error.set('Email y contraseña son obligatorios.');
      return;
    }
    const wantsEmployee = this.draft.branchId !== null;
    if (wantsEmployee && (!this.draft.firstName.trim() || !this.draft.lastName.trim())) {
      this.error.set('Para asignar sucursal se requieren nombre y apellido del empleado.');
      return;
    }
    this.busy.set(true);
    this.error.set('');
    this.api('/users', {
      method: 'POST',
      body: JSON.stringify({
        email: this.draft.email.trim(),
        password: this.draft.password,
        phone: this.draft.phone.trim() || null,
        roles: this.draft.roles,
      }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then(async (created: UserRow) => {
        if (wantsEmployee) {
          await this.linkEmployee(created.id);
        }
        this.draft = {
          email: '',
          password: '',
          phone: '',
          firstName: '',
          lastName: '',
          roles: [],
          branchId: null,
        };
        this.info.set(`Usuario ${created.email} registrado.`);
        await this.loadUsers();
      })
      .catch((e) => this.fail('No se pudo registrar el usuario', e))
      .finally(() => this.busy.set(false));
  }

  private async linkEmployee(userId: number): Promise<void> {
    const res = await this.api(`/users/${userId}/employee`, {
      method: 'POST',
      body: JSON.stringify({
        first_name: this.draft.firstName.trim(),
        last_name: this.draft.lastName.trim(),
        branch_id: this.draft.branchId,
      }),
    });
    if (!res.ok) {
      const body = (await res.json().catch(() => ({}))) as { detail?: string };
      throw new Error(body.detail ?? res.statusText);
    }
  }

  startEdit(u: UserRow): void {
    this.editing.set(u);
    this.edit = { phone: u.phone ?? '', roles: u.roles.map((r) => r.name) };
    this.error.set('');
    this.info.set('');
  }

  cancelEdit(): void {
    this.editing.set(null);
  }

  saveEdit(): void {
    const u = this.editing();
    if (!u) return;
    this.busy.set(true);
    this.api(`/users/${u.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ phone: this.edit.phone.trim() || null, roles: this.edit.roles }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then(() => {
        this.info.set(`Usuario #${u.id} actualizado.`);
        this.editing.set(null);
        return this.loadUsers();
      })
      .catch((e) => this.fail('No se pudo actualizar el usuario', e))
      .finally(() => this.busy.set(false));
  }

  toggleActive(u: UserRow): void {
    this.busy.set(true);
    this.api(`/users/${u.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: !u.is_active }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then(() => {
        this.info.set(`Usuario ${u.email} ${u.is_active ? 'deshabilitado' : 'habilitado'}.`);
        return this.loadUsers();
      })
      .catch((e) => this.fail('No se pudo cambiar el estado', e))
      .finally(() => this.busy.set(false));
  }
}
