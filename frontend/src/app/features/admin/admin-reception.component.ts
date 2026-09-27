import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface Branch {
  id: number;
  name: string;
}

interface Supplier {
  id: number;
  company_name: string;
  is_active: boolean;
}

interface VariantOption {
  id: number;
  sku: string;
  size_name?: string;
  color_name?: string;
  garment?: { id: number; name: string } | null;
}

interface Line {
  variant_id: number | null;
  quantity: number;
  cost_price: number | null;
}

interface Movement {
  id: number;
  variant_id: number;
  branch_id: number;
  movement_type: string;
  quantity: number;
  reason: string | null;
  created_at: string;
}

@Component({
  selector: 'app-admin-reception',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="reception">
      <h2>Recepción de productos (CU-29) · Movimientos (CU-28)</h2>

      @if (error()) {
        <p class="alert error" role="alert">{{ error() }}</p>
      }
      @if (info()) {
        <p class="alert ok" role="status">{{ info() }}</p>
      }

      <article class="panel">
        <h3>Nueva recepción</h3>
        <form (ngSubmit)="submit()" autocomplete="off">
          <div class="grid">
            <label class="field">
              <span>Sucursal *</span>
              <select name="branch" required [(ngModel)]="form.branchId">
                <option [ngValue]="null">Selecciona…</option>
                @for (b of branches(); track b.id) {
                  <option [ngValue]="b.id">{{ b.name }}</option>
                }
              </select>
            </label>
            <label class="field">
              <span>Proveedor *</span>
              <select name="supplier" required [(ngModel)]="form.supplierId">
                <option [ngValue]="null">Selecciona…</option>
                @for (s of suppliers(); track s.id) {
                  <option [ngValue]="s.id">{{ s.company_name }}</option>
                }
              </select>
            </label>
            <label class="field">
              <span>Referencia de orden</span>
              <input type="text" name="po" [(ngModel)]="form.purchaseOrderRef" placeholder="OC-0001" />
            </label>
            <label class="field">
              <span>Notas</span>
              <input type="text" name="notes" [(ngModel)]="form.notes" placeholder="Opcional" />
            </label>
          </div>

          <h4>Prendas recibidas</h4>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Variante (SKU)</th>
                  <th>Cantidad</th>
                  <th>Costo unitario</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                @for (line of lines(); track $index) {
                  <tr>
                    <td>
                      <select
                        [value]="line.variant_id"
                        (change)="patchLine($index, 'variant_id', +$any($event.target).value)"
                      >
                        <option [ngValue]="null">Selecciona…</option>
                        @for (v of variants(); track v.id) {
                          <option [ngValue]="v.id">
                            {{ v.sku }} — {{ v.garment?.name }} {{ v.size_name }} {{ v.color_name }}
                          </option>
                        }
                      </select>
                    </td>
                    <td>
                      <input
                        type="number"
                        min="1"
                        [value]="line.quantity"
                        (input)="patchLine($index, 'quantity', +$any($event.target).value)"
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        [value]="line.cost_price"
                        (input)="patchLine($index, 'cost_price', +$any($event.target).value)"
                      />
                    </td>
                    <td>
                      <button type="button" class="link" (click)="removeLine($index)">Quitar</button>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="4" class="muted">Agrega al menos una prenda.</td>
                  </tr>
                }
              </tbody>
            </table>
          </div>

          <div class="actions">
            <button type="button" class="btn" (click)="addLine()">+ Agregar prenda</button>
            <button class="btn btn-primary" type="submit" [disabled]="busy()">
              {{ busy() ? 'Registrando…' : 'Registrar recepción' }}
            </button>
          </div>
        </form>
      </article>

      <article class="panel">
        <div class="panel-head">
          <h3>Movimientos de inventario</h3>
          <div class="filters">
            <select [value]="form.branchId ?? ''" (change)="onMovementBranch($event)">
              <option value="">Todas las sucursales</option>
              @for (b of branches(); track b.id) {
                <option [value]="b.id">{{ b.name }}</option>
              }
            </select>
            <button class="btn" (click)="loadMovements()">Actualizar</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Variante</th>
                <th>Sucursal</th>
                <th>Tipo</th>
                <th>Cantidad</th>
                <th>Motivo</th>
              </tr>
            </thead>
            <tbody>
              @for (m of movements(); track m.id) {
                <tr>
                  <td>{{ m.created_at | date: 'short' }}</td>
                  <td>#{{ m.variant_id }}</td>
                  <td>#{{ m.branch_id }}</td>
                  <td><span class="chip">{{ m.movement_type }}</span></td>
                  <td [class.neg]="m.quantity < 0">{{ m.quantity }}</td>
                  <td>{{ m.reason ?? '—' }}</td>
                </tr>
              } @empty {
                <tr>
                  <td colspan="6" class="muted">Sin movimientos registrados.</td>
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
      .reception {
        max-width: 1200px;
      }
      h2 {
        margin-top: 0;
      }
      h4 {
        margin: 1.25rem 0 0.5rem;
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
      .filters {
        display: flex;
        gap: 0.5rem;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.75rem;
      }
      .field {
        display: block;
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
      td input,
      td select {
        width: 100%;
        padding: 0.45rem;
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
        padding: 0.45rem;
        text-align: left;
      }
      .chip {
        display: inline-block;
        background: #f1f5f9;
        border-radius: 999px;
        padding: 0.1rem 0.5rem;
        font-size: 0.72rem;
      }
      .neg {
        color: #991b1b;
        font-weight: 600;
      }
      .actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
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
      .link {
        background: none;
        border: none;
        color: var(--color-primary-dark, #cc7000);
        cursor: pointer;
        text-decoration: underline;
      }
      button {
        cursor: pointer;
      }
    `,
  ],
})
export class AdminReceptionComponent implements OnInit {
  private auth = inject(AuthService);

  readonly branches = signal<Branch[]>([]);
  readonly suppliers = signal<Supplier[]>([]);
  readonly variants = signal<VariantOption[]>([]);
  readonly movements = signal<Movement[]>([]);
  readonly lines = signal<Line[]>([{ variant_id: null, quantity: 1, cost_price: null }]);
  readonly busy = signal(false);
  readonly error = signal('');
  readonly info = signal('');

  form = {
    branchId: null as number | null,
    supplierId: null as number | null,
    purchaseOrderRef: '',
    notes: '',
  };

  ngOnInit(): void {
    this.loadBranches();
    this.loadSuppliers();
    this.loadVariants();
    this.loadMovements();
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

  loadBranches(): void {
    this.api('/locations/branches')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: Branch[]) => this.branches.set(data))
      .catch(() => this.branches.set([]));
  }

  loadSuppliers(): void {
    this.api('/suppliers')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: Supplier[]) => this.suppliers.set(data.filter((s) => s.is_active)))
      .catch(() => this.suppliers.set([]));
  }

  loadVariants(): void {
    this.api('/products?size=200')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((garments: { id: number }[]) => {
        const active = garments.filter((g) => g.id);
        return Promise.all(
          active.map((g) =>
            this.api(`/products/${g.id}/variants`)
              .then((r) => (r.ok ? r.json() : []))
              .catch(() => [] as VariantOption[])
          )
        ).then((chunks) => chunks.flat());
      })
      .then((data: VariantOption[]) => this.variants.set(data))
      .catch(() => this.variants.set([]));
  }

  loadMovements(): void {
    const qs = this.form.branchId !== null ? `?branch_id=${this.form.branchId}` : '';
    this.api(`/inventory/movements${qs}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: Movement[]) => this.movements.set(data))
      .catch((e) => this.fail('No se pudieron cargar los movimientos', e));
  }

  onMovementBranch(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    this.form.branchId = value ? Number(value) : null;
    this.loadMovements();
  }

  addLine(): void {
    this.lines.update((l) => [...l, { variant_id: null, quantity: 1, cost_price: null }]);
  }

  removeLine(index: number): void {
    this.lines.update((l) => l.filter((_, i) => i !== index));
  }

  patchLine(index: number, field: keyof Line, value: number | null): void {
    this.lines.update((l) => l.map((line, i) => (i === index ? { ...line, [field]: value } : line)));
  }

  submit(): void {
    if (this.form.branchId === null || this.form.supplierId === null) {
      this.error.set('Sucursal y proveedor son obligatorios.');
      return;
    }
    const items = this.lines()
      .filter((l) => l.variant_id !== null && l.quantity > 0)
      .map((l) => ({
        variant_id: l.variant_id as number,
        quantity: l.quantity,
        cost_price: l.cost_price ?? 0,
      }));
    if (!items.length) {
      this.error.set('Agrega al menos una prenda con cantidad mayor a cero.');
      return;
    }

    this.busy.set(true);
    this.error.set('');
    this.api('/receptions', {
      method: 'POST',
      body: JSON.stringify({
        supplier_id: this.form.supplierId,
        branch_id: this.form.branchId,
        purchase_order_ref: this.form.purchaseOrderRef.trim() || null,
        notes: this.form.notes.trim() || null,
        items,
      }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return (await r.json()) as { id: number };
      })
      .then((created) => {
        this.form = { branchId: this.form.branchId, supplierId: null, purchaseOrderRef: '', notes: '' };
        this.lines.set([{ variant_id: null, quantity: 1, cost_price: null }]);
        this.info.set(`Recepción #${created.id} registrada.`);
        this.loadMovements();
      })
      .catch((e) => this.fail('No se pudo registrar la recepción', e))
      .finally(() => this.busy.set(false));
  }
}
