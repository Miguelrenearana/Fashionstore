import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

@Component({
  selector: 'app-admin-reports',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="reports">
      <h2>Reportes e indicadores (CU-33 · CU-34 · CU-35)</h2>

      @if (error) {
        <p class="error">{{ error }}</p>
      }

      <form class="filters" (ngSubmit)="loadIndicators()">
        <label>
          Desde
          <input type="date" [(ngModel)]="startDate" name="start" required />
        </label>
        <label>
          Hasta
          <input type="date" [(ngModel)]="endDate" name="end" required />
        </label>
        <label>
          Sucursal
          <select [(ngModel)]="branchId" name="branch">
            <option [ngValue]="0">Todas</option>
            @for (b of branches; track b.id) {
              <option [ngValue]="b.id">{{ b.name }}</option>
            }
          </select>
        </label>
        <button type="submit" [disabled]="loading">Consultar</button>
      </form>

      @if (indicators(); as ind) {
        <section class="cards">
          @for (item of ind.indicators; track item.name) {
            <article class="kpi">
              <strong>{{ item.name }}</strong>
              <span>{{ item.value }} <small>{{ item.unit }}</small></span>
            </article>
          }
        </section>
      }

      <div class="tabs">
        <button [class.active]="tab()==='consolidated'" (click)="tab.set('consolidated')">Consolidado</button>
        <button [class.active]="tab()==='sales'" (click)="tab.set('sales')">Ventas por período</button>
        <button [class.active]="tab()==='top'" (click)="tab.set('top')">Productos más vendidos</button>
        <button [class.active]="tab()==='stock'" (click)="tab.set('stock')">Stock bajo</button>
        <button [class.active]="tab()==='turnover'" (click)="tab.set('turnover')">Rotación</button>
        <button [class.active]="tab()==='audit'" (click)="tab.set('audit')">Bitácora</button>
      </div>

      @switch (tab()) {
        @case ('consolidated') {
          <section>
            <h3>Reporte consolidado (CU-35)</h3>
            <button (click)="loadConsolidated()" [disabled]="loading">Cargar</button>
            @if (consolidated(); as c) {
              <p class="summary">Ventas: {{ c.total_sales }} · Ingresos: {{ c.total_revenue }} · Órdenes: {{ c.total_orders }} · Stock: {{ c.total_stock }} · Bajo stock: {{ c.low_stock_items }}</p>
              <table>
                <thead>
                  <tr><th>Sucursal</th><th>Ventas</th><th>Órdenes</th><th>Ingresos</th><th>Stock</th><th>Bajo</th></tr>
                </thead>
                <tbody>
                  @for (b of c.branches; track b.branch_id) {
                    <tr>
                      <td>{{ b.branch_name }}</td>
                      <td>{{ b.total_sales }}</td>
                      <td>{{ b.total_orders }}</td>
                      <td>{{ b.total_revenue }}</td>
                      <td>{{ b.total_stock }}</td>
                      <td>{{ b.low_stock_items }}</td>
                    </tr>
                  }
                </tbody>
              </table>
            }
          </section>
        }
        @case ('sales') {
          <section>
            <h3>Ventas por período (CU-33)</h3>
            <select [(ngModel)]="periodType" name="period_type">
              <option value="daily">Diario</option>
              <option value="weekly">Semanal</option>
              <option value="monthly">Mensual</option>
            </select>
            <button (click)="loadSalesByPeriod()" [disabled]="loading">Cargar</button>
            @if (salesByPeriod(); as sp) {
              <table>
                <thead>
                  <tr><th>Período</th><th>Ventas</th><th>Órdenes</th><th>Ticket promedio</th></tr>
                </thead>
                <tbody>
                  @for (row of sp.data; track row.period) {
                    <tr>
                      <td>{{ row.period }}</td>
                      <td>{{ row.total_sales }}</td>
                      <td>{{ row.order_count }}</td>
                      <td>{{ row.avg_ticket }}</td>
                    </tr>
                  } @empty {
                    <tr><td colspan="4">Sin datos</td></tr>
                  }
                </tbody>
              </table>
            }
          </section>
        }
        @case ('top') {
          <section>
            <h3>Productos más vendidos</h3>
            <button (click)="loadTopProducts()" [disabled]="loading">Cargar</button>
            @if (topProducts(); as tp) {
              <table>
                <thead>
                  <tr><th>Prenda</th><th>SKU</th><th>Talla</th><th>Color</th><th>Cantidad</th><th>Ingresos</th></tr>
                </thead>
                <tbody>
                  @for (row of tp.items; track row.variant_id) {
                    <tr>
                      <td>{{ row.garment_name }}</td>
                      <td>{{ row.variant_sku }}</td>
                      <td>{{ row.size_name }}</td>
                      <td>{{ row.color_name }}</td>
                      <td>{{ row.total_quantity }}</td>
                      <td>{{ row.total_revenue }}</td>
                    </tr>
                  } @empty {
                    <tr><td colspan="6">Sin datos</td></tr>
                  }
                </tbody>
              </table>
            }
          </section>
        }
        @case ('stock') {
          <section>
            <h3>Stock bajo y agotado (CU-28)</h3>
            <button (click)="loadLowStock()" [disabled]="loading">Cargar</button>
            @if (lowStock(); as ls) {
              <p class="summary">Bajo stock: {{ ls.total_low_stock }} · Agotados: {{ ls.out_of_stock_count }}</p>
              <table>
                <thead>
                  <tr><th>Sucursal</th><th>Prenda</th><th>SKU</th><th>Talla</th><th>Color</th><th>Disponible</th><th>Reservado</th></tr>
                </thead>
                <tbody>
                  @for (row of ls.items; track $index) {
                    <tr>
                      <td>{{ row.branch_name }}</td>
                      <td>{{ row.garment_name }}</td>
                      <td>{{ row.variant_sku }}</td>
                      <td>{{ row.size_name }}</td>
                      <td>{{ row.color_name }}</td>
                      <td>{{ row.available }}</td>
                      <td>{{ row.reserved_quantity }}</td>
                    </tr>
                  } @empty {
                    <tr><td colspan="7">Sin datos</td></tr>
                  }
                </tbody>
              </table>
            }
          </section>
        }
        @case ('turnover') {
          <section>
            <h3>Rotación de inventario</h3>
            <button (click)="loadTurnover()" [disabled]="loading">Cargar</button>
            @if (turnover(); as tv) {
              <p class="summary">Rotación promedio: {{ tv.avg_turnover_rate }}</p>
              <table>
                <thead>
                  <tr><th>Sucursal</th><th>Prenda</th><th>SKU</th><th>Venta diaria</th><th>Stock</th><th>Días de stock</th><th>Tasa</th></tr>
                </thead>
                <tbody>
                  @for (row of tv.items; track row.variant_id) {
                    <tr>
                      <td>{{ row.branch_name }}</td>
                      <td>{{ row.garment_name }}</td>
                      <td>{{ row.variant_sku }}</td>
                      <td>{{ row.avg_daily_sales }}</td>
                      <td>{{ row.current_stock }}</td>
                      <td>{{ row.days_of_stock }}</td>
                      <td>{{ row.turnover_rate }}</td>
                    </tr>
                  } @empty {
                    <tr><td colspan="7">Sin datos</td></tr>
                  }
                </tbody>
              </table>
            }
          </section>
        }
        @case ('audit') {
          <section>
            <h3>Bitácora y trazabilidad (CU-34)</h3>
            <button (click)="loadAuditLog()" [disabled]="loading">Cargar</button>
            @if (auditLog(); as al) {
              <p class="summary">{{ al.total }} registros</p>
              <table>
                <thead>
                  <tr><th>#</th><th>Usuario</th><th>Acción</th><th>Entidad</th><th>Fecha</th></tr>
                </thead>
                <tbody>
                  @for (row of al.items; track row.id) {
                    <tr>
                      <td>{{ row.id }}</td>
                      <td>{{ row.user_email }}</td>
                      <td>{{ row.action }}</td>
                      <td>{{ row.entity }} {{ row.entity_id }}</td>
                      <td>{{ row.created_at | date: 'short' }}</td>
                    </tr>
                  } @empty {
                    <tr><td colspan="5">Sin datos</td></tr>
                  }
                </tbody>
              </table>
            }
          </section>
        }
      }
    </section>
  `,
  styles: [
    `
      .reports {
        max-width: 1100px;
      }
      .filters {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        align-items: flex-end;
        margin-bottom: 1.25rem;
      }
      .filters label {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        font-size: 0.8rem;
      }
      .filters input,
      .filters select {
        padding: 0.4rem;
      }
      .error {
        color: #b00020;
      }
      .cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 0.75rem;
        margin-bottom: 1.5rem;
      }
      .kpi {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.9rem;
        background: #fff;
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
      }
      .kpi strong {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: capitalize;
      }
      .kpi span {
        font-weight: 700;
        font-size: 1.2rem;
      }
      .kpi small {
        font-weight: 400;
        color: #94a3b8;
      }
      .tabs {
        display: flex;
        gap: 0.4rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
      }
      .tabs button {
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        border: 1px solid #cbd5e1;
        background: #fff;
        cursor: pointer;
      }
      .tabs button.active {
        background: var(--color-primary);
        border-color: var(--color-primary);
        color: #fff;
      }
      .summary {
        margin: 0 0 0.75rem;
        font-size: 0.9rem;
        color: #475569;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
      }
      th,
      td {
        border: 1px solid #ddd;
        padding: 0.35rem 0.5rem;
        text-align: left;
      }
      button {
        cursor: pointer;
      }
    `,
  ],
})
export class AdminReportsComponent implements OnInit {
  private auth = inject(AuthService);
  readonly indicators = signal<any | null>(null);
  readonly consolidated = signal<any | null>(null);
  readonly salesByPeriod = signal<any | null>(null);
  readonly topProducts = signal<any | null>(null);
  readonly lowStock = signal<any | null>(null);
  readonly turnover = signal<any | null>(null);
  readonly auditLog = signal<any | null>(null);
  readonly tab = signal('consolidated');

  error = '';
  loading = false;
  startDate = '';
  endDate = '';
  branchId = 0;
  periodType = 'monthly';
  branches: { id: number; name: string }[] = [];

  ngOnInit(): void {
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 1);
    this.startDate = start.toISOString().slice(0, 10);
    this.endDate = end.toISOString().slice(0, 10);
    this.loadBranches();
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.auth.token()) h['Authorization'] = `Bearer ${this.auth.token()}`;
    return h;
  }

  private async get(path: string): Promise<any> {
    const r = await fetch(`${environment.apiUrl}${path}`, { headers: this.headers() });
    if (!r.ok) {
      const b = await r.json().catch(() => ({}));
      throw new Error(b.detail ?? r.statusText);
    }
    return r.json();
  }

  private run(fn: () => Promise<void>): void {
    this.loading = true;
    this.error = '';
    fn()
      .catch((e) => (this.error = e.message ?? String(e)))
      .finally(() => (this.loading = false));
  }

  private qs(): string {
    const p = new URLSearchParams();
    p.set('start_date', `${this.startDate}T00:00:00`);
    p.set('end_date', `${this.endDate}T23:59:59`);
    if (this.branchId) p.set('branch_id', String(this.branchId));
    return p.toString();
  }

  loadBranches(): void {
    fetch(`${environment.apiUrl}/locations/branches`, { headers: this.headers() })
      .then((r) => r.json())
      .then((data) => (this.branches = data))
      .catch(() => undefined);
  }

  loadIndicators(): void {
    this.run(async () => (this.indicators.set(await this.get(`/reports/indicators?${this.qs()}`))));
  }

  loadConsolidated(): void {
    this.run(async () => (this.consolidated.set(await this.get(`/reports/consolidated?${this.qs()}`))));
  }

  loadSalesByPeriod(): void {
    this.run(async () => {
      const p = new URLSearchParams(this.qs());
      p.set('period_type', this.periodType);
      this.salesByPeriod.set(await this.get(`/reports/sales-by-period?${p.toString()}`));
    });
  }

  loadTopProducts(): void {
    this.run(async () => {
      const p = new URLSearchParams(this.qs());
      p.set('limit', '10');
      this.topProducts.set(await this.get(`/reports/top-products?${p.toString()}`));
    });
  }

  loadLowStock(): void {
    this.run(async () => {
      let path = '/reports/low-stock';
      if (this.branchId) path += `?branch_id=${this.branchId}`;
      this.lowStock.set(await this.get(path));
    });
  }

  loadTurnover(): void {
    this.run(async () => (this.turnover.set(await this.get(`/reports/inventory-turnover?${this.qs()}`))));
  }

  loadAuditLog(): void {
    this.run(async () => {
      let path = '/reports/audit-log?page=1&size=50';
      if (this.startDate) path += `&start_date=${this.startDate}T00:00:00`;
      if (this.endDate) path += `&end_date=${this.endDate}T23:59:59`;
      this.auditLog.set(await this.get(path));
    });
  }
}