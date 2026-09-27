import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface City {
  id: number;
  name: string;
  state: string;
  country: string;
  is_active: boolean;
  branches?: Branch[];
}

interface Branch {
  id: number;
  name: string;
  address: string;
  phone: string | null;
  is_active: boolean;
  city_id: number;
  city: { id: number; name: string; state: string } | null;
}

@Component({
  selector: 'app-admin-locations',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="locations">
      <h2>Ciudades y sucursales (CU-06)</h2>

      @if (error()) {
        <p class="alert error" role="alert">{{ error() }}</p>
      }
      @if (info()) {
        <p class="alert ok" role="status">{{ info() }}</p>
      }

      <div class="layout">
        <article class="panel">
          <h3>Registrar ciudad</h3>
          <form (ngSubmit)="createCity()" autocomplete="off">
            <label class="field">
              <span>Nombre</span>
              <input type="text" name="cityName" required [(ngModel)]="cityDraft.name" placeholder="Bogotá" />
            </label>
            <label class="field">
              <span>Estado / Departamento</span>
              <input type="text" name="cityState" required [(ngModel)]="cityDraft.state" placeholder="Cundinamarca" />
            </label>
            <label class="field">
              <span>País</span>
              <input type="text" name="cityCountry" required [(ngModel)]="cityDraft.country" placeholder="Colombia" />
            </label>
            <button class="btn btn-primary w-full" type="submit" [disabled]="busy()">Registrar ciudad</button>
          </form>
        </article>

        <article class="panel">
          <h3>Registrar sucursal</h3>
          <form (ngSubmit)="createBranch()" autocomplete="off">
            <label class="field">
              <span>Nombre</span>
              <input type="text" name="branchName" required [(ngModel)]="branchDraft.name" placeholder="Sucursal Norte" />
            </label>
            <label class="field">
              <span>Ciudad</span>
              <select name="branchCity" required [(ngModel)]="branchDraft.cityId">
                <option [ngValue]="null">Selecciona…</option>
                @for (c of cities(); track c.id) {
                  <option [ngValue]="c.id">{{ c.name }} — {{ c.state }}</option>
                }
              </select>
            </label>
            <label class="field">
              <span>Dirección</span>
              <input type="text" name="branchAddress" required [(ngModel)]="branchDraft.address" />
            </label>
            <label class="field">
              <span>Teléfono</span>
              <input type="tel" name="branchPhone" [(ngModel)]="branchDraft.phone" placeholder="Opcional" />
            </label>
            <button class="btn btn-primary w-full" type="submit" [disabled]="busy()">Registrar sucursal</button>
          </form>
        </article>
      </div>

      <article class="panel">
        <div class="panel-head">
          <h3>Ciudades ({{ cities().length }})</h3>
          <button class="btn" (click)="load()">Actualizar</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Ciudad</th>
                <th>Estado</th>
                <th>País</th>
                <th>Sucursales</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              @for (c of cities(); track c.id) {
                <tr>
                  <td>
                    @if (editingCity()?.id === c.id) {
                      <input type="text" [value]="editingCity()!.name" (input)="patchCity('name', $any($event.target).value)" />
                    } @else {
                      {{ c.name }}
                    }
                  </td>
                  <td>
                    @if (editingCity()?.id === c.id) {
                      <input type="text" [value]="editingCity()!.state" (input)="patchCity('state', $any($event.target).value)" />
                    } @else {
                      {{ c.state }}
                    }
                  </td>
                  <td>{{ c.country }}</td>
                  <td>{{ c.branches?.length ?? 0 }}</td>
                  <td>
                    <span class="badge" [class.on]="c.is_active">{{ c.is_active ? 'Activa' : 'Inactiva' }}</span>
                  </td>
                  <td class="actions">
                    @if (editingCity()?.id === c.id) {
                      <button class="link" (click)="saveCity(c.id)">Guardar</button>
                      <button class="link" (click)="editingCity.set(null)">Cancelar</button>
                    } @else {
                      <button class="link" (click)="startEditCity(c)">Editar</button>
                      <button class="link" (click)="toggleCity(c)">
                        {{ c.is_active ? 'Deshabilitar' : 'Habilitar' }}
                      </button>
                    }
                  </td>
                </tr>
              } @empty {
                <tr>
                  <td colspan="6" class="muted">No hay ciudades registradas.</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <h3>Sucursales ({{ branches().length }})</h3>
          <label class="inline">
            <input type="checkbox" [checked]="showInactive()" (change)="toggleShowInactive($event)" />
            <span>Mostrar inactivas</span>
          </label>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Sucursal</th>
                <th>Ciudad</th>
                <th>Dirección</th>
                <th>Teléfono</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              @for (b of branches(); track b.id) {
                <tr>
                  <td>
                    @if (editingBranch()?.id === b.id) {
                      <input type="text" [value]="editingBranch()!.name" (input)="patchBranch('name', $any($event.target).value)" />
                    } @else {
                      {{ b.name }}
                    }
                  </td>
                  <td>{{ b.city?.name ?? '—' }}</td>
                  <td>
                    @if (editingBranch()?.id === b.id) {
                      <input type="text" [value]="editingBranch()!.address" (input)="patchBranch('address', $any($event.target).value)" />
                    } @else {
                      {{ b.address }}
                    }
                  </td>
                  <td>{{ b.phone ?? '—' }}</td>
                  <td>
                    <span class="badge" [class.on]="b.is_active">{{ b.is_active ? 'Activa' : 'Inactiva' }}</span>
                  </td>
                  <td class="actions">
                    @if (editingBranch()?.id === b.id) {
                      <button class="link" (click)="saveBranch(b.id)">Guardar</button>
                      <button class="link" (click)="editingBranch.set(null)">Cancelar</button>
                    } @else {
                      <button class="link" (click)="startEditBranch(b)">Editar</button>
                      <button class="link" (click)="toggleBranch(b)">
                        {{ b.is_active ? 'Deshabilitar' : 'Habilitar' }}
                      </button>
                    }
                  </td>
                </tr>
              } @empty {
                <tr>
                  <td colspan="6" class="muted">No hay sucursales registradas.</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      </article>
    </section>
  `,
  styles: [
    `
      .locations {
        max-width: 1200px;
      }
      h2 {
        margin-top: 0;
      }
      .layout {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-bottom: 1.5rem;
      }
      .panel {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem;
        background: #fff;
        margin-bottom: 1.5rem;
      }
      .panel h3 {
        margin-top: 0;
      }
      .panel-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
      }
      .inline {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.85rem;
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
      .field select,
      td input {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        box-sizing: border-box;
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
      button {
        cursor: pointer;
      }
    `,
  ],
})
export class AdminLocationsComponent implements OnInit {
  private auth = inject(AuthService);

  readonly cities = signal<City[]>([]);
  readonly branches = signal<Branch[]>([]);
  readonly busy = signal(false);
  readonly error = signal('');
  readonly info = signal('');
  readonly showInactive = signal(false);
  readonly editingCity = signal<City | null>(null);
  readonly editingBranch = signal<Branch | null>(null);

  cityDraft = { name: '', state: '', country: '' };
  branchDraft = { name: '', cityId: null as number | null, address: '', phone: '' };

  ngOnInit(): void {
    this.load();
  }

  private headers(): Record<string, string> {
    return { 'Content-Type': 'application/json', Authorization: `Bearer ${this.auth.token()}` };
  }

  private api(path: string, init?: RequestInit): Promise<Response> {
    return fetch(`${environment.apiUrl}${path}`, { ...init, headers: this.headers() });
  }

  private fail(prefix: string, e: unknown): void {
    const detail = e instanceof Error ? e.message : String(e);
    this.error.set(`${prefix}: ${detail}`);
    this.info.set('');
  }

  load(): void {
    this.loadCities();
    this.loadBranches();
  }

  private loadCities(): void {
    this.api('/locations/cities')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: City[]) => this.cities.set(data))
      .catch((e) => this.fail('No se pudieron cargar las ciudades', e));
  }

  private loadBranches(): void {
    const qs = this.showInactive() ? '?include_inactive=true' : '';
    this.api(`/locations/branches${qs}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: Branch[]) => this.branches.set(data))
      .catch((e) => this.fail('No se pudieron cargar las sucursales', e));
  }

  toggleShowInactive(event: Event): void {
    this.showInactive.set((event.target as HTMLInputElement).checked);
    this.loadBranches();
  }

  createCity(): void {
    if (!this.cityDraft.name.trim() || !this.cityDraft.state.trim() || !this.cityDraft.country.trim()) {
      this.error.set('Nombre, estado y país son obligatorios.');
      return;
    }
    this.busy.set(true);
    this.error.set('');
    this.api('/locations/cities', {
      method: 'POST',
      body: JSON.stringify({
        name: this.cityDraft.name.trim(),
        state: this.cityDraft.state.trim(),
        country: this.cityDraft.country.trim(),
      }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then((c: City) => {
        this.cityDraft = { name: '', state: '', country: '' };
        this.info.set(`Ciudad ${c.name} registrada.`);
        this.loadCities();
      })
      .catch((e) => this.fail('No se pudo registrar la ciudad', e))
      .finally(() => this.busy.set(false));
  }

  createBranch(): void {
    if (!this.branchDraft.name.trim() || this.branchDraft.cityId === null || !this.branchDraft.address.trim()) {
      this.error.set('Nombre, ciudad y dirección son obligatorios.');
      return;
    }
    this.busy.set(true);
    this.error.set('');
    this.api('/locations/branches', {
      method: 'POST',
      body: JSON.stringify({
        name: this.branchDraft.name.trim(),
        city_id: this.branchDraft.cityId,
        address: this.branchDraft.address.trim(),
        phone: this.branchDraft.phone.trim() || null,
      }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then((b: Branch) => {
        this.branchDraft = { name: '', cityId: null, address: '', phone: '' };
        this.info.set(`Sucursal ${b.name} registrada.`);
        this.loadBranches();
      })
      .catch((e) => this.fail('No se pudo registrar la sucursal', e))
      .finally(() => this.busy.set(false));
  }

  startEditCity(c: City): void {
    this.editingCity.set({ ...c });
  }

  patchCity(field: 'name' | 'state', value: string): void {
    const cur = this.editingCity();
    if (cur) this.editingCity.set({ ...cur, [field]: value });
  }

  saveCity(id: number): void {
    const draft = this.editingCity();
    if (!draft) return;
    this.busy.set(true);
    this.api(`/locations/cities/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ name: draft.name.trim(), state: draft.state.trim() }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then(() => {
        this.editingCity.set(null);
        this.info.set('Ciudad actualizada.');
        this.loadCities();
      })
      .catch((e) => this.fail('No se pudo actualizar la ciudad', e))
      .finally(() => this.busy.set(false));
  }

  toggleCity(c: City): void {
    this.busy.set(true);
    this.api(`/locations/cities/${c.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: !c.is_active }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then(() => {
        this.info.set(`Ciudad ${c.name} ${c.is_active ? 'deshabilitada' : 'habilitada'}.`);
        this.loadCities();
      })
      .catch((e) => this.fail('No se pudo cambiar el estado de la ciudad', e))
      .finally(() => this.busy.set(false));
  }

  startEditBranch(b: Branch): void {
    this.editingBranch.set({ ...b });
  }

  patchBranch(field: 'name' | 'address', value: string): void {
    const cur = this.editingBranch();
    if (cur) this.editingBranch.set({ ...cur, [field]: value });
  }

  saveBranch(id: number): void {
    const draft = this.editingBranch();
    if (!draft) return;
    this.busy.set(true);
    this.api(`/locations/branches/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ name: draft.name.trim(), address: draft.address.trim() }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then(() => {
        this.editingBranch.set(null);
        this.info.set('Sucursal actualizada.');
        this.loadBranches();
      })
      .catch((e) => this.fail('No se pudo actualizar la sucursal', e))
      .finally(() => this.busy.set(false));
  }

  toggleBranch(b: Branch): void {
    this.busy.set(true);
    this.api(`/locations/branches/${b.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: !b.is_active }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then(() => {
        this.info.set(`Sucursal ${b.name} ${b.is_active ? 'deshabilitada' : 'habilitada'}.`);
        this.loadBranches();
      })
      .catch((e) => this.fail('No se pudo cambiar el estado de la sucursal', e))
      .finally(() => this.busy.set(false));
  }
}
