import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

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
  selector: 'app-admin-inventory',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="inventory-admin">
      <h2>Inventario (CU-27 · CU-28 · CU-29)</h2>

      @if (message()) {
        <p class="msg">{{ message() }}</p>
      }

      <section class="inventory">
        <h3>Stock por sucursal</h3>
        <select (change)="loadInventory($event)" [value]="selectedBranch() || ''">
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

      <section class="branches">
        <h3>Sucursales ({{ branches().length }})</h3>
        <div class="grid">
          @for (b of branches(); track b.id) {
            <article class="card">
              <h4>{{ b.name }}</h4>
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
      </section>
    </section>
  `,
  styles: [
    `
      .inventory-admin {
        max-width: 1100px;
      }
      .msg {
        font-size: 0.85rem;
        color: var(--color-primary-dark, #cc7000);
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
      .branches {
        margin-top: 2rem;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 1rem;
      }
      .card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        background: #fff;
      }
      .card h4 {
        margin-top: 0;
      }
      .card p {
        margin: 0.25rem 0;
        color: #475569;
        font-size: 0.9rem;
      }
      button {
        cursor: pointer;
      }
    `,
  ],
})
export class AdminInventoryComponent implements OnInit {
  private auth = inject(AuthService);
  readonly branches = signal<Branch[]>([]);
  readonly rows = signal<InventoryRow[]>([]);
  readonly saving = signal(false);
  readonly message = signal('');
  readonly selectedBranch = signal<number | null>(null);

  ngOnInit(): void {
    fetch(`${environment.apiUrl}/locations/branches`, {
      headers: this.authHeaders(),
    })
      .then((r) => r.json())
      .then((data: Branch[]) => this.branches.set(data));
  }

  private authHeaders(): Record<string, string> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.auth.token()) headers['Authorization'] = `Bearer ${this.auth.token()}`;
    return headers;
  }

  loadInventory(event: Event): void {
    const branchId = (event.target as HTMLSelectElement).value;
    if (!branchId) {
      this.selectedBranch.set(null);
      this.rows.set([]);
      return;
    }
    this.selectedBranch.set(Number(branchId));
    this.fetchInventory(Number(branchId));
  }

  private fetchInventory(branchId: number): void {
    fetch(`${environment.apiUrl}/inventory?branch_id=${branchId}`, {
      headers: this.authHeaders(),
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
        headers: this.authHeaders(),
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