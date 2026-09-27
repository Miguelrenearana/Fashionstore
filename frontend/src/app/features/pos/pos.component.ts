import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface Branch {
  id: number;
  name: string;
}

interface VariantOption {
  id: number;
  sku: string;
  price: number;
  size_name?: string;
  color_name?: string;
  garment?: { id: number; name: string } | null;
}

interface StockRow {
  variant_id: number;
  available: number;
}

interface CartLine {
  variant_id: number;
  label: string;
  unit_price: number;
  quantity: number;
}

interface Sale {
  id: number;
  invoice_number: string;
  total_amount: number;
  status: string | null;
  paid_at: string | null;
}

interface Receipt {
  id: number;
  type: string;
  rnc_or_cuf: string | null;
  document_url: string | null;
  created_at: string;
  total_amount: number;
  status: string;
  branch_name: string | null;
  items: {
    variant_id: number;
    garment_name: string | null;
    size_name: string | null;
    color_name: string | null;
    quantity: number;
    unit_price: number;
    line_total: number;
  }[];
}

/** CU-24: métodos de pago aceptados en caja. */
const PAYMENT_METHODS = [
  { value: 'cash', label: 'Efectivo' },
  { value: 'card', label: 'Tarjeta' },
  { value: 'qr', label: 'QR / Transferencia' },
];

@Component({
  selector: 'app-pos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="pos">
      <h2>Punto de venta (CU-23 · CU-24)</h2>

      @if (error()) {
        <p class="alert error" role="alert">{{ error() }}</p>
      }
      @if (info()) {
        <p class="alert ok" role="status">{{ info() }}</p>
      }

      <div class="layout">
        <article class="panel">
          <h3>Agregar prenda</h3>

          <label class="field">
            <span>Sucursal *</span>
            <select [(ngModel)]="branchId" (ngModelChange)="onBranchChange()">
              <option [ngValue]="null">Selecciona…</option>
              @for (b of branches(); track b.id) {
                <option [ngValue]="b.id">{{ b.name }}</option>
              }
            </select>
          </label>

          <label class="field">
            <span>Prenda *</span>
            <select [ngModel]="variantId" (ngModelChange)="onVariantChange($event)">
              <option [ngValue]="null">Selecciona…</option>
              @for (v of variants(); track v.id) {
                <option [ngValue]="v.id" [disabled]="stockFor(v.id) <= 0">
                  {{ v.sku }} — {{ v.garment?.name }} {{ v.size_name }} {{ v.color_name }}
                  @if (stockFor(v.id) > 0) {
                    (disp. {{ stockFor(v.id) }})
                  } @else {
                    (sin stock)
                  }
                </option>
              }
            </select>
          </label>

          <label class="field">
            <span>Cantidad</span>
            <input type="number" min="1" [max]="maxQty()" [(ngModel)]="quantity" />
          </label>

          @if (selectedVariant(); as v) {
            <p class="muted">Precio unitario: {{ v.price | currency: 'USD' }}</p>
          }

          <button class="btn btn-primary w-full" (click)="addToCart()" [disabled]="!canAdd()">
            Agregar al carrito
          </button>
        </article>

        <article class="panel">
          <h3>Carrito ({{ count() }} prendas)</h3>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Prenda</th>
                  <th>Cant.</th>
                  <th>Unitario</th>
                  <th>Subtotal</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                @for (line of cart(); track line.variant_id) {
                  <tr>
                    <td>{{ line.label }}</td>
                    <td>{{ line.quantity }}</td>
                    <td>{{ line.unit_price | currency: 'USD' }}</td>
                    <td>{{ line.unit_price * line.quantity | currency: 'USD' }}</td>
                    <td>
                      <button class="link" (click)="removeLine(line.variant_id)">Quitar</button>
                    </td>
                  </tr>
                } @empty {
                  <tr>
                    <td colspan="5" class="muted">El carrito está vacío.</td>
                  </tr>
                }
              </tbody>
              <tfoot>
                <tr>
                  <th colspan="3">Total</th>
                  <th>{{ total() | currency: 'USD' }}</th>
                  <th></th>
                </tr>
              </tfoot>
            </table>
          </div>
        </article>
      </div>

      <article class="panel">
        <h3>Cobrar</h3>
        <div class="pay-row">
          <label class="field">
            <span>Método de pago *</span>
            <select [(ngModel)]="paymentMethod">
              @for (m of methods; track m.value) {
                <option [value]="m.value">{{ m.label }}</option>
              }
            </select>
          </label>

          @if (paymentMethod === 'cash') {
            <label class="field">
              <span>Efectivo recibido</span>
              <input type="number" min="0" step="0.01" [(ngModel)]="cashReceived" />
            </label>
            <p class="muted">Cambio: {{ change() | currency: 'USD' }}</p>
          }

          <button class="btn btn-primary" (click)="checkout()" [disabled]="busy() || !cart().length || !branchId">
            {{ busy() ? 'Procesando…' : 'Finalizar compra' }}
          </button>
        </div>
      </article>

      @if (sale(); as s) {
        <article class="panel receipt">
          <h3>Comprobante</h3>
          @if (receipt(); as r) {
            <p><strong>Factura:</strong> {{ r.rnc_or_cuf ?? s.invoice_number }}</p>
            <p><strong>Tipo:</strong> {{ r.type === 'credit_note' ? 'Nota de crédito' : 'Factura' }}</p>
            <p><strong>Estado:</strong> {{ r.status }}</p>
            <p><strong>Total:</strong> {{ r.total_amount | currency: 'USD' }}</p>
            <p><strong>Emitido:</strong> {{ r.created_at | date: 'medium' }}</p>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Prenda</th>
                    <th>Talla</th>
                    <th>Color</th>
                    <th>Cant.</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  @for (i of r.items; track i.variant_id) {
                    <tr>
                      <td>{{ i.garment_name ?? '—' }}</td>
                      <td>{{ i.size_name ?? '—' }}</td>
                      <td>{{ i.color_name ?? '—' }}</td>
                      <td>{{ i.quantity }}</td>
                      <td>{{ i.line_total | currency: 'USD' }}</td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
            @if (r.document_url) {
              <a [href]="r.document_url" target="_blank" rel="noopener">Ver documento</a>
            }
          } @else {
            <p class="muted">Venta #{{ s.id }} registrada. Esperando confirmación del pago…</p>
            <button class="btn" (click)="loadReceipt(s.id)" [disabled]="busy()">Consultar comprobante</button>
          }
        </article>
      }
    </section>
  `,
  styles: [
    `
      .pos {
        max-width: 1200px;
        padding: 2rem;
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
        margin-bottom: 1.5rem;
      }
      .panel h3 {
        margin-top: 0;
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
      .pay-row {
        display: flex;
        gap: 1rem;
        align-items: flex-end;
        flex-wrap: wrap;
      }
      .pay-row .field {
        min-width: 180px;
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
      tfoot th {
        font-size: 0.95rem;
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
      @media (max-width: 900px) {
        .layout {
          grid-template-columns: 1fr;
        }
      }
    `,
  ],
})
export class PosComponent implements OnInit {
  private auth = inject(AuthService);

  readonly branches = signal<Branch[]>([]);
  readonly variants = signal<VariantOption[]>([]);
  readonly stock = signal<StockRow[]>([]);
  readonly cart = signal<CartLine[]>([]);
  readonly sale = signal<Sale | null>(null);
  readonly receipt = signal<Receipt | null>(null);
  readonly selectedVariant = signal<VariantOption | null>(null);
  readonly busy = signal(false);
  readonly error = signal('');
  readonly info = signal('');

  readonly methods = PAYMENT_METHODS;
  branchId: number | null = null;
  variantId: number | null = null;
  quantity = 1;
  paymentMethod = 'cash';
  cashReceived: number | null = null;

  ngOnInit(): void {
    this.loadBranches();
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
      .then((data: Branch[]) => {
        this.branches.set(data);
        if (data.length && this.branchId === null) {
          this.branchId = data[0].id;
          this.onBranchChange();
        }
      })
      .catch((e) => this.fail('No se pudieron cargar las sucursales', e));
  }

  onBranchChange(): void {
    this.cart.set([]);
    this.selectedVariant.set(null);
    this.variantId = null;
    this.stock.set([]);
    if (this.branchId === null) return;

    this.api('/products?size=200')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((garments: { id: number }[]) =>
        Promise.all(
          garments
            .filter((g) => g.id)
            .map((g) =>
              this.api(`/products/${g.id}/variants`)
                .then((r) => (r.ok ? r.json() : []))
                .catch(() => [] as VariantOption[])
            )
        ).then((chunks) => chunks.flat())
      )
      .then((all: VariantOption[]) => this.variants.set(all))
      .catch(() => this.variants.set([]));

    this.loadStock();
  }

  private loadStock(): void {
    if (this.branchId === null) return;
    this.api(`/inventory?branch_id=${this.branchId}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((rows: StockRow[]) => this.stock.set(rows.map((r) => ({ variant_id: r.variant_id, available: r.available }))))
      .catch(() => this.stock.set([]));
  }

  stockFor(variantId: number): number {
    return this.stock().find((s) => s.variant_id === variantId)?.available ?? 0;
  }

  onVariantChange(event: Event): void {
    const id = (event.target as HTMLSelectElement).value;
    this.variantId = id ? Number(id) : null;
    this.selectedVariant.set(this.variants().find((v) => v.id === this.variantId) ?? null);
  }

  maxQty(): number {
    return this.variantId === null ? 0 : this.stockFor(this.variantId);
  }

  canAdd(): boolean {
    return (
      this.branchId !== null &&
      this.variantId !== null &&
      this.quantity > 0 &&
      this.quantity <= this.maxQty()
    );
  }

  addToCart(): void {
    const variantId = this.variantId;
    if (!this.canAdd() || variantId === null) return;
    const v = this.selectedVariant();
    const label = `${v?.garment?.name ?? ''} ${v?.size_name ?? ''} ${v?.color_name ?? ''}`.trim();
    const existing = this.cart().find((l) => l.variant_id === variantId);
    if (existing) {
      if (existing.quantity + this.quantity > this.maxQty()) {
        this.error.set('No hay stock suficiente para esa cantidad.');
        return;
      }
      this.cart.update((l) =>
        l.map((line) =>
          line.variant_id === variantId ? { ...line, quantity: line.quantity + this.quantity } : line
        )
      );
    } else {
      this.cart.update((l) => [
        ...l,
        { variant_id: variantId, label, unit_price: v?.price ?? 0, quantity: this.quantity },
      ]);
    }
    this.error.set('');
    this.quantity = 1;
  }

  removeLine(variantId: number): void {
    this.cart.update((l) => l.filter((line) => line.variant_id !== variantId));
  }

  count(): number {
    return this.cart().reduce((acc, l) => acc + l.quantity, 0);
  }

  total(): number {
    return this.cart().reduce((acc, l) => acc + l.unit_price * l.quantity, 0);
  }

  change(): number {
    if (this.paymentMethod !== 'cash' || this.cashReceived === null) return 0;
    return Math.max(0, this.cashReceived - this.total());
  }

  checkout(): void {
    if (!this.cart().length || this.branchId === null) return;
    if (this.paymentMethod === 'cash' && (this.cashReceived === null || this.cashReceived < this.total())) {
      this.error.set('El efectivo recibido no cubre el total.');
      return;
    }

    this.busy.set(true);
    this.error.set('');
    const items = this.cart().map((l) => ({ variant_id: l.variant_id, quantity: l.quantity }));

    this.api('/sales', {
      method: 'POST',
      body: JSON.stringify({
        branch_id: this.branchId,
        items,
        payment_method: this.paymentMethod,
      }),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return (await r.json()) as Sale;
      })
      .then((sale) => {
        this.sale.set(sale);
        this.receipt.set(null);
        this.cart.set([]);
        this.cashReceived = null;
        this.info.set(`Venta ${sale.invoice_number} registrada (${sale.status}).`);
        this.loadStock();
        return this.pay(sale);
      })
      .catch((e) => this.fail('No se pudo registrar la venta', e))
      .finally(() => this.busy.set(false));
  }

  private async pay(sale: Sale): Promise<void> {
    const res = await this.api(`/payments/initiate?sale_id=${sale.id}&method=${this.paymentMethod}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const body = (await res.json().catch(() => ({}))) as { detail?: string };
      throw new Error(body.detail ?? res.statusText);
    }
    const payment = (await res.json()) as { gateway_reference: string };
    await this.api('/payments/confirm', {
      method: 'POST',
      body: JSON.stringify({ gateway_reference: payment.gateway_reference }),
    });
    await this.loadReceipt(sale.id);
  }

  async loadReceipt(saleId: number): Promise<void> {
    try {
      const r = await this.api(`/sales/${saleId}/receipt`);
      if (!r.ok) {
        this.info.set(`Venta #${saleId} registrada. Aún no hay comprobante emitido.`);
        return;
      }
      this.receipt.set((await r.json()) as Receipt);
    } catch (e) {
      this.fail('No se pudo consultar el comprobante', e);
    }
  }
}
