import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface City {
  id: number;
  name: string;
  state: string;
}

interface Branch {
  id: number;
  name: string;
  address: string;
  phone?: string;
  city: { id: number; name: string; state: string } | null;
}

interface InventoryRow {
  id: number;
  branch_id: number;
  variant_id: number;
  quantity: number;
  reserved_quantity: number;
  available: number;
  variant: {
    id: number;
    sku: string;
    price: number;
    size_name?: string;
    color_name?: string;
    garment?: { id: number; name: string } | null;
  } | null;
}

@Component({
  selector: 'app-branch',
  standalone: true,
  imports: [FormsModule],
  template: `
    <section class="branch">
      <h2>Sucursales</h2>
      <div class="grid">
        @for (b of branches(); track b.id) {
          <article class="card">
            <h3>{{ b.name }}</h3>
            <p>{{ b.city?.name }} · {{ b.city?.state }}</p>
            <p>{{ b.address }}</p>
            @if (b.phone) {
              <p>Tel: {{ b.phone }}</p>
            }
          </article>
        } @empty {
          <p>No hay sucursales registradas.</p>
        }
      </div>

      <form class="card-new" (ngSubmit)="createBranch()">
        <h3>Nueva sucursal</h3>
        <input [(ngModel)]="form.name" name="name" placeholder="Nombre" required />
        <input [(ngModel)]="form.address" name="address" placeholder="Dirección" required />
        <select [(ngModel)]="form.city_id" name="city_id" required>
          <option [ngValue]="0" disabled>Ciudad...</option>
          @for (city of cities(); track city.id) {
            <option [ngValue]="city.id">{{ city.name }} ({{ city.state }})</option>
          }
        </select>
        <input [(ngModel)]="form.phone" name="phone" placeholder="Teléfono (opcional)" />
        <button type="submit" [disabled]="saving()">Crear sucursal</button>
        <p class="msg">{{ message() }}</p>
      </form>

      <section class="inventory">
        <h3>Inventario por sucursal</h3>
        <select (change)="loadInventory($event)">
          <option value="">Selecciona sucursal...</option>
          @for (b of branches(); track b.id) {
            <option [value]="b.id">{{ b.name }}</option>
          }
        </select>
        <table>
          <thead>
            <tr>
              <th>Producto</th>
              <th>SKU</th>
              <th>Talla</th>
              <th>Color</th>
              <th>Stock</th>
              <th>Reservado</th>
              <th>Disponible</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            @for (row of rows(); track row.id) {
              <tr>
                <td>{{ row.variant?.garment?.name }}</td>
                <td>{{ row.variant?.sku }}</td>
                <td>{{ row.variant?.size_name }}</td>
                <td>{{ row.variant?.color_name }}</td>
                <td>{{ row.quantity }}</td>
                <td>{{ row.reserved_quantity }}</td>
                <td>{{ row.available }}</td>
                <td>
                  <button (click)="adjust(row, 1)">+1</button>
                  <button (click)="adjust(row, -1)" [disabled]="row.available <= 0">-1</button>
                </td>
              </tr>
            } @empty {
              <tr>
                <td colspan="8">Selecciona una sucursal.</td>
              </tr>
            }
          </tbody>
        </table>
      </section>
    </section>
  `,
  styles: [
    `
      .branch {
        padding: 1.5rem;
        max-width: 960px;
        margin: 0 auto;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
      }
      .card,
      .card-new {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        background: #fff;
      }
      .card h3,
      .card-new h3 {
        margin-top: 0;
      }
      .card-new {
        max-width: 420px;
      }
      .card-new input,
      .card-new select {
        display: block;
        width: 100%;
        box-sizing: border-box;
        margin-bottom: 0.5rem;
        padding: 0.4rem;
      }
      button {
        padding: 0.5rem 1rem;
        background: var(--color-primary);
        color: #fff;
        border: none;
        border-radius: 6px;
        cursor: pointer;
      }
      button:disabled {
        opacity: 0.6;
      }
      .msg {
        margin: 0.5rem 0 0;
        font-size: 0.85rem;
      }
      .inventory {
        margin-top: 2rem;
      }
      .inventory select {
        margin-bottom: 1rem;
        padding: 0.4rem;
      }
      .inventory table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
      }
      .inventory th,
      .inventory td {
        border: 1px solid #ddd;
        padding: 0.35rem 0.5rem;
        text-align: left;
      }
    `,
  ],
})
export class BranchComponent implements OnInit {
  private auth = inject(AuthService);
  readonly branches = signal<Branch[]>([]);
  readonly cities = signal<City[]>([]);
  readonly rows = signal<InventoryRow[]>([]);
  readonly saving = signal(false);
  readonly message = signal('');

  form = { name: '', address: '', city_id: 0, phone: '' };

  ngOnInit(): void {
    fetch(`${environment.apiUrl}/locations/branches`)
      .then((r) => r.json())
      .then((data: Branch[]) => this.branches.set(data));
    fetch(`${environment.apiUrl}/locations/cities`)
      .then((r) => r.json())
      .then((data: City[]) => this.cities.set(data));
  }

  createBranch(): void {
    this.saving.set(true);
    this.message.set('');
    fetch(`${environment.apiUrl}/locations/branches`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.auth.token()}`,
      },
      body: JSON.stringify(this.form),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json()) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then((branch: Branch) => {
        this.branches.set([...this.branches(), branch]);
        this.form = { name: '', address: '', city_id: 0, phone: '' };
        this.message.set('Sucursal creada.');
      })
      .catch((e) => this.message.set(`Error: ${e.message}`))
      .finally(() => this.saving.set(false));
  }

  loadInventory(event: Event): void {
    const branchId = (event.target as HTMLSelectElement).value;
    if (!branchId) {
      this.rows.set([]);
      return;
    }
    this.fetchInventory(Number(branchId));
  }

  private fetchInventory(branchId: number): void {
    fetch(`${environment.apiUrl}/inventory?branch_id=${branchId}`, {
      headers: { Authorization: `Bearer ${this.auth.token()}` },
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: InventoryRow[]) => this.rows.set(data))
      .catch((e) => this.message.set(`Inventario: ${e}`));
  }

  adjust(row: InventoryRow, delta: number): void {
    this.saving.set(true);
    fetch(
      `${environment.apiUrl}/inventory/${row.branch_id}/${row.variant_id}/adjust`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.auth.token()}`,
        },
        body: JSON.stringify({ quantity: delta, reason: 'ajuste manual' }),
      }
    )
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json()) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then(() => this.fetchInventory(row.branch_id))
      .catch((e) => this.message.set(`Ajuste: ${e.message}`))
      .finally(() => this.saving.set(false));
  }
}