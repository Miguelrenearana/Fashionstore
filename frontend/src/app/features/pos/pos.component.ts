import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '@core/environments/environment';

interface Sale {
  id: number;
  invoice_number: string;
  branch_id: number;
  total_amount: number;
  status: string;
}

interface Receipt {
  id: number;
  type: string;
  rnc_or_cuf: string | null;
  document_url: string | null;
}

@Component({
  selector: 'app-pos',
  standalone: true,
  imports: [FormsModule],
  template: `
    <section class="pos">
      <h2>Punto de venta (POS)</h2>

      <form class="card" (ngSubmit)="registerSale()">
        <h3>Registrar venta presencial</h3>
        <label>
          Variante (ID)
          <input type="number" [(ngModel)]="variantId" name="variant_id" required />
        </label>
        <label>
          Cantidad
          <input type="number" [(ngModel)]="quantity" name="quantity" value="1" required />
        </label>
        <label>
          Sucursal
          <input type="number" [(ngModel)]="branchId" name="branch_id" value="1" required />
        </label>
        <button type="submit" [disabled]="loading">Registrar venta (Bs {{ sale()?.total_amount ?? '...' }})</button>
      </form>

      @if (sale()) {
        <div class="card">
          <h3>Venta {{ sale()?.invoice_number }}</h3>
          <p>Total: Bs {{ sale()?.total_amount }} · Estado: {{ sale()?.status }}</p>
          @if (sale()?.status === 'PENDING') {
            <button class="primary" (click)="charge()" [disabled]="loading">Cobrar en caja</button>
          }
        </div>
      }

      @if (receipt()) {
        <div class="receipt">
          <h3>Comprobante emitido</h3>
          <p>Tipo: {{ receipt()?.type }}</p>
          <p>Número/CUF: {{ receipt()?.rnc_or_cuf }}</p>
          @if (receipt()?.document_url) {
            <p><a [href]="receipt()?.document_url" target="_blank">Descargar comprobante</a></p>
          }
        </div>
      }

      @if (error) {
        <p class="error">{{ error }}</p>
      }
    </section>
  `,
  styles: [
    `
      .pos {
        max-width: 640px;
        margin: 0 auto;
        padding: 1.5rem;
      }
      .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
      }
      label {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        align-items: center;
      }
      input {
        padding: 0.4rem;
        width: 120px;
      }
      button {
        cursor: pointer;
        padding: 0.5rem 1rem;
      }
      .primary {
        background: var(--color-primary);
        color: #fff;
        border: none;
      }
      .receipt {
        background: #f6fff0;
        border: 1px solid #97c960;
        border-radius: 8px;
        padding: 1rem;
      }
      .error {
        color: #b00020;
      }
    `,
  ],
})
export class PosComponent {
  private http = inject(HttpClient);
  readonly sale = signal<Sale | null>(null);
  readonly receipt = signal<Receipt | null>(null);
  loading = false;
  error = '';
  variantId: number | null = null;
  quantity: number = 1;
  branchId: number = 1;

  registerSale(): void {
    if (!this.variantId) {
      this.error = 'Indique un ID de variante.';
      return;
    }
    this.loading = true;
    this.error = '';
    this.receipt.set(null);
    this.http
      .post<Sale>(`${environment.apiUrl}/sales`, {
        branch_id: this.branchId,
        items: [{ variant_id: this.variantId, quantity: this.quantity }],
        payment_method: 'cash',
      })
      .subscribe({
        next: (sale) => this.sale.set(sale),
        error: (e) => (this.error = e.error?.detail ?? 'No se pudo registrar la venta.'),
      })
      .add(() => (this.loading = false));
  }

  charge(): void {
    const sale = this.sale();
    if (!sale) {
      return;
    }
    this.loading = true;
    this.error = '';
    this.http
      .post<{ gateway_reference: string }>(
        `${environment.apiUrl}/payments/initiate`,
        null,
        { params: { sale_id: String(sale.id), method: 'cash' } }
      )
      .subscribe({
        next: (payment) => this.confirm(payment.gateway_reference),
        error: (e) => (this.error = e.error?.detail ?? 'No se pudo iniciar el cobro.'),
      })
      .add(() => (this.loading = false));
  }

  private confirm(gateway_reference: string): void {
    this.http
      .post<{ status: string }>(`${environment.apiUrl}/payments/confirm`, { gateway_reference })
      .subscribe({
        next: () => this.loadReceipt(),
        error: (e) => (this.error = e.error?.detail ?? 'No se pudo confirmar el pago.'),
      });
  }

  private loadReceipt(): void {
    const sale = this.sale();
    if (!sale) {
      return;
    }
    this.http
      .get<Receipt>(`${environment.apiUrl}/sales/${sale.id}/receipt`)
      .subscribe({
        next: (receipt) => {
          this.receipt.set(receipt);
          this.http
            .get<Sale>(`${environment.apiUrl}/sales/${sale.id}`)
            .subscribe((s) => this.sale.set(s));
        },
        error: (e) => (this.error = e.error?.detail ?? 'No se pudo generar el comprobante.'),
      });
  }
}