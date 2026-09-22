import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';
import { UiButtonComponent } from '@shared/ui/button';

type ReportTab = 'consolidated' | 'sales' | 'top' | 'stock' | 'turnover' | 'audit';

@Component({
  selector: 'app-admin-reports',
  standalone: true,
  imports: [CommonModule, FormsModule, UiButtonComponent],
  template: `
    <section class="reports container py-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-semibold">Reportes e indicadores</h2>
        <span class="text-sm text-secondary">CU-33 · CU-34 · CU-35</span>
      </div>

      @if (error) {
        <div class="alert alert-error mb-4">{{ error }}</div>
      }

      <form class="filters mb-6" (ngSubmit)="loadIndicators()">
        <label>
          Desde
          <input class="form-input" type="date" [(ngModel)]="startDate" name="start" required />
        </label>
        <label>
          Hasta
          <input class="form-input" type="date" [(ngModel)]="endDate" name="end" required />
        </label>
        <label>
          Sucursal
          <select class="form-input" [(ngModel)]="branchId" name="branch">
            <option [ngValue]="0">Todas</option>
            @for (b of branches; track b.id) {
              <option [ngValue]="b.id">{{ b.name }}</option>
            }
          </select>
        </label>
        <ui-button variant="primary" type="submit" [disabled]="loading" [loading]="loading">
          {{ loading ? 'Consultando…' : 'Consultar' }}
        </ui-button>
      </form>

      @if (indicators(); as ind) {
        <section class="cards mb-6">
          @for (item of ind.indicators; track item.name) {
            <article class="kpi card p-4">
              <strong>{{ item.name }}</strong>
              <span>{{ item.value }} <small>{{ item.unit }}</small></span>
            </article>
          }
        </section>
      }

      <div class="tabs">
        @for (t of tabDefinitions(); track t.id) {
          <button
            type="button"
            class="tab"
            [class.active]="tab() === t.id"
            (click)="tab.set(t.id)"
          >{{ t.label }}</button>
        }
      </div>

      @switch (tab()) {
        @case ('consolidated') {
          <section>
            <div class="flex items-center gap-3 mb-4">
              <h3 class="text-lg font-semibold">Reporte consolidado (CU-35)</h3>
              <ui-button variant="primary" (click)="loadConsolidated()" [disabled]="loading">
                Cargar
              </ui-button>
            </div>
            @if (consolidated(); as c) {
              <p class="summary">
                Ventas: {{ c.total_sales }} · Ingresos: {{ c.total_revenue }} ·
                Órdenes: {{ c.total_orders }} · Stock: {{ c.total_stock }} ·
                Bajo stock: {{ c.low_stock_items }}
              </p>
              <div class="table-wrapper">
                <table class="table">
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
                    } @empty {
                      <tr><td colspan="6">Sin datos</td></tr>
                    }
                  </tbody>
                </table>
              </div>
            }
          </section>
        }
        @case ('sales') {
          <section>
            <div class="flex items-center gap-3 mb-4">
              <h3 class="text-lg font-semibold">Ventas por período (CU-33)</h3>
              <select class="form-input" [(ngModel)]="periodType" name="period_type">
                <option value="daily">Diario</option>
                <option value="weekly">Semanal</option>
                <option value="monthly">Mensual</option>
              </select>
              <ui-button variant="primary" (click)="loadSalesByPeriod()" [disabled]="loading">
                Cargar
              </ui-button>
            </div>
            @if (salesByPeriod(); as sp) {
              <div class="table-wrapper">
                <table class="table">
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
              </div>
            }
          </section>
        }
        @case ('top') {
          <section>
            <div class="flex items-center gap-3 mb-4">
              <h3 class="text-lg font-semibold">Productos más vendidos (CU-33)</h3>
              <ui-button variant="primary" (click)="loadTopProducts()" [disabled]="loading">
                Cargar
              </ui-button>
            </div>
            @if (topProducts(); as tp) {
              <div class="table-wrapper">
                <table class="table">
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
              </div>
            }
          </section>
        }
        @case ('stock') {
          <section>
            <div class="flex items-center gap-3 mb-4">
              <h3 class="text-lg font-semibold">Stock bajo y agotado (CU-28)</h3>
              <ui-button variant="primary" (click)="loadLowStock()" [disabled]="loading">
                Cargar
              </ui-button>
            </div>
            @if (lowStock(); as ls) {
              <p class="summary">Bajo stock: {{ ls.total_low_stock }} · Agotados: {{ ls.out_of_stock_count }}</p>
              <div class="table-wrapper">
                <table class="table">
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
              </div>
            }
          </section>
        }
        @case ('turnover') {
          <section>
            <div class="flex items-center gap-3 mb-4">
              <h3 class="text-lg font-semibold">Rotación de inventario</h3>
              <ui-button variant="primary" (click)="loadTurnover()" [disabled]="loading">
                Cargar
              </ui-button>
            </div>
            @if (turnover(); as tv) {
              <p class="summary">Rotación promedio: {{ tv.avg_turnover_rate }}</p>
              <div class="table-wrapper">
                <table class="table">
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
              </div>
            }
          </section>
        }
        @case ('audit') {
          <section>
            <div class="flex items-center gap-3 mb-4">
              <h3 class="text-lg font-semibold">Bitácora y trazabilidad (CU-34)</h3>
              <ui-button variant="primary" (click)="loadAuditLog()" [disabled]="loading">
                Cargar
              </ui-button>
            </div>
            @if (auditLog(); as al) {
              <p class="summary">{{ al.total }} registros</p>
              <div class="table-wrapper">
                <table class="table">
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
              </div>
            }
          </section>
        }
      }
    </section>
  `,
  styles: [
    `
      .filters {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: var(--space-3);
        align-items: flex-end;
        max-width: 720px;
      }
      .filters label {
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
        font-size: var(--text-sm);
        color: var(--color-text-secondary);
      }
      .cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: var(--space-3);
      }
      .kpi {
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
      }
      .kpi strong {
        font-size: var(--text-sm);
        color: var(--color-text-secondary);
        text-transform: capitalize;
      }
      .kpi span {
        font-weight: 700;
        font-size: 1.25rem;
      }
      .kpi small {
        font-weight: 400;
        color: var(--color-text-muted);
      }
      .tabs {
        display: flex;
        gap: var(--space-1);
        flex-wrap: wrap;
        margin-bottom: var(--space-4);
        border-bottom: 1px solid var(--color-border);
      }
      .tab {
        padding: var(--space-3) var(--space-4);
        font-size: var(--text-sm);
        font-weight: 500;
        color: var(--color-text-secondary);
        background: none;
        border: none;
        border-bottom: 2px solid transparent;
        cursor: pointer;
        transition: all var(--transition-fast);
        position: relative;
        bottom: -1px;
      }
      .tab:hover {
        color: var(--color-text);
      }
      .tab.active {
        color: var(--color-primary);
        border-bottom-color: var(--color-primary);
      }
      .summary {
        margin: 0 0 var(--space-3);
        font-size: var(--text-sm);
        color: var(--color-text-secondary);
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
  readonly tab = signal<ReportTab>('consolidated');

  tabDefinitions = (): { id: ReportTab; label: string }[] => [
    { id: 'consolidated', label: 'Consolidado' },
    { id: 'sales', label: 'Ventas por período' },
    { id: 'top', label: 'Más vendidos' },
    { id: 'stock', label: 'Stock bajo' },
    { id: 'turnover', label: 'Rotación' },
    { id: 'audit', label: 'Bitácora' },
  ];

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