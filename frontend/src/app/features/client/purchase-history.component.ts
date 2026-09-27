import { Component, ElementRef, inject, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ClientService, HistoryEntry, Receipt } from './client.service';

@Component({
  selector: 'app-client-purchase-history',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="page">
      <h1 class="page-title">Historial de compras</h1>
      <p class="page-subtitle">Tus compras, reservas y comprobantes de venta.</p>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      @if (loading) {
        <div class="loading">Cargando historial...</div>
      } @else if (entries.length === 0) {
        <div class="empty card">
          <p>No tienes compras ni reservas registradas.</p>
          <a routerLink="/client/catalog" class="btn btn-primary">Ir al catálogo</a>
        </div>
      } @else {
        <div class="list">
          @for (entry of entries; track entry.type + ':' + entry.id) {
            <div class="entry card">
              <div class="entry-head">
                <div>
                  <strong>{{ entry.type === 'sale' ? 'Compra' : 'Reserva' }} {{ entry.reference }}</strong>
                  <span class="badge-status" [class]="'st-' + entry.status.toLowerCase()">
                    {{ statusLabel(entry.status) }}
                  </span>
                </div>
                <span class="date">{{ entry.date | date:'dd/MM/yyyy HH:mm' }}</span>
              </div>

              <p class="meta">{{ entry.items_count }} artículo(s)</p>
              @if (entry.branch_name) {
                <p class="meta">Sucursal: {{ entry.branch_name }}</p>
              }

              <div class="entry-footer">
                <span class="total">Total: Bs {{ entry.total_amount | number:'1.2-2' }}</span>
                @if (entry.type === 'sale') {
                  @if (isPendingSale(entry)) {
                    <span class="receipt-notice">Comprobante disponible al confirmarse el pago</span>
                  } @else {
                    <button type="button" class="btn btn-outline btn-sm" (click)="viewReceipt(entry)" [disabled]="receiptLoading">
                      Ver comprobante
                    </button>
                  }
                }
              </div>
              @if (entry.type === 'sale' && receiptErrorSaleId === entry.id) {
                <div class="alert alert-error receipt-error" role="alert">{{ receiptError }}</div>
              }
            </div>
          }
        </div>

        @if (receipt) {
          <dialog #receiptDialog class="receipt-dialog" aria-labelledby="receipt-title"
            (cancel)="$event.preventDefault(); closeReceipt()"
            (click)="onReceiptBackdropClick($event)">
              <div class="receipt-dialog-head">
                <h2 id="receipt-title">Comprobante</h2>
                <button type="button" class="btn btn-outline btn-sm" autofocus (click)="closeReceipt()">Cerrar</button>
              </div>
              <div class="receipt">
                <h3>FashionStore</h3>
                <p class="meta">Comprobante #{{ receipt.id }}</p>
                <p class="meta">Venta: {{ receipt.invoice_number ?? receipt.sale_id }}</p>
                @if (receipt.rnc_or_cuf) {
                  <p class="meta">RNC/CUF: {{ receipt.rnc_or_cuf }}</p>
                }
                @if (receipt.branch_name) {
                  <p class="meta">Sucursal: {{ receipt.branch_name }}</p>
                }
                <hr />
                @if (receipt.items && receipt.items.length > 0) {
                  @for (item of receipt.items; track $index) {
                    <div class="r-row">
                      <span>
                        {{ item.garment_name ?? ('Variante ' + item.variant_id) }}
                        <span class="meta">{{ item.size_name }} {{ item.color_name }}</span>
                        <span class="meta">{{ item.quantity }} × Bs {{ item.unit_price | number:'1.2-2' }}</span>
                      </span>
                      <span>Bs {{ item.line_total | number:'1.2-2' }}</span>
                    </div>
                  }
                }
                <hr />
                <div class="r-row total-row"><strong>Total</strong><strong>Bs {{ receipt.total_amount | number:'1.2-2' }}</strong></div>
                <p class="meta" *ngIf="receipt.created_at">Emitido: {{ receipt.created_at | date:'dd/MM/yyyy HH:mm' }}</p>
              </div>
          </dialog>
        }
      }
    </div>
  `,
  styles: [
    `
      .page-title { margin-bottom: 4px; }
      .page-subtitle { color: var(--color-text-muted); margin-bottom: 1.25rem; }
      .list { display: flex; flex-direction: column; gap: 1rem; }
      .entry { padding: 1.25rem; }
      .entry-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
      .badge-status { font-size: 0.72rem; padding: 2px 10px; border-radius: 99px; margin-left: 0.5rem; }
      .st-completed, .st-paid, .st-confirmed { background: #dcfce7; color: #166534; }
      .st-refunded, .st-cancelled, .st-expired { background: #fee2e2; color: #991b1b; }
      .st-pending { background: #fef3c7; color: #92400e; }
      .date { color: var(--color-text-muted); font-size: 0.85rem; }
      .items { border-top: 1px solid var(--color-border); padding-top: 0.75rem; margin-bottom: 0.75rem; }
      .item-row { display: flex; gap: 0.5rem; padding: 0.2rem 0; font-size: 0.9rem; }
      .item-name { flex: 1; }
      .item-qty { color: var(--color-text-muted); }
      .item-price { font-weight: 500; min-width: 80px; text-align: right; }
      .entry-footer { display: flex; flex-wrap: wrap; gap: 0.75rem; justify-content: space-between; align-items: center; border-top: 1px solid var(--color-border); padding-top: 0.75rem; }
      .receipt-notice { color: var(--color-text-secondary, #64748b); font-size: 0.85rem; }
      .receipt-error { margin-top: 0.75rem; }
      .total { font-weight: 700; }
      .loading { text-align: center; color: var(--color-text-muted); padding: 4rem 0; }
      .empty { text-align: center; padding: 3rem 1rem; }
      .empty p { margin-bottom: 1rem; }
      .receipt-dialog {
        position: fixed;
        inset: 0;
        margin: auto;
        width: min(520px, calc(100vw - 2rem));
        max-width: calc(100vw - 2rem);
        max-height: calc(100vh - 2rem);
        max-height: calc(100dvh - 2rem);
        padding: 0;
        border: 1px solid var(--color-border, #cbd5e1);
        border-radius: 12px;
        background: var(--color-surface, #fff);
        color: var(--color-text, #1e293b);
        box-shadow: 0 24px 64px rgba(0, 0, 0, 0.3);
        overflow: hidden;
      }
      .receipt-dialog[open] { display: flex; flex-direction: column; }
      .receipt-dialog::backdrop { background: rgba(15, 23, 42, 0.65); }
      .receipt-dialog-head { display: flex; flex-shrink: 0; gap: 1rem; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid var(--color-border); }
      .receipt-dialog-head h2 { margin: 0; font-size: 1.25rem; }
      .receipt-dialog-head button { flex-shrink: 0; }
      .receipt { min-height: 0; overflow-y: auto; overscroll-behavior: contain; padding: 1rem; font-size: 0.9rem; overflow-wrap: anywhere; }
      .receipt .meta { color: var(--color-text-secondary, #64748b); }
      .receipt .r-row > :first-child { min-width: 0; }
      .receipt .r-row > :last-child { flex-shrink: 0; white-space: nowrap; }
      .receipt .r-row .meta { display: block; }
      .receipt h3 { margin: 0 0 4px; }
      .meta { color: var(--color-text-muted); font-size: 0.8rem; margin: 2px 0; }
      .r-row { display: flex; gap: 1rem; justify-content: space-between; padding: 0.4rem 0; }
      .total-row { border-top: 1px solid var(--color-border); margin-top: 0.5rem; padding-top: 0.5rem; }
    `,
  ],
})
export class PurchaseHistoryComponent implements OnInit {
  private api = inject(ClientService);
  private receiptDialog?: HTMLDialogElement;

  @ViewChild('receiptDialog')
  set receiptDialogRef(ref: ElementRef<HTMLDialogElement> | undefined) {
    this.receiptDialog = ref?.nativeElement;
    // The top layer keeps the dialog in the viewport even when the history is scrolled.
    if (this.receiptDialog && !this.receiptDialog.open) {
      this.receiptDialog.showModal();
    }
  }

  entries: HistoryEntry[] = [];
  receipt: Receipt | null = null;
  receiptLoading = false;
  receiptErrorSaleId: number | null = null;
  receiptError = '';
  loading = false;
  error = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.receiptErrorSaleId = null;
    this.receiptError = '';
    this.api.getHistory(1, 50).subscribe({
      next: (res) => {
        this.entries = res.items;
        this.loading = false;
      },
      error: () => { this.error = 'No se pudo cargar el historial.'; this.loading = false; },
    });
  }

  statusLabel(status: string): string {
    const map: Record<string, string> = {
      completed: 'Completada', paid: 'Pagada', pending: 'Pendiente',
      refunded: 'Reembolsada', cancelled: 'Cancelada', confirmed: 'Confirmada',
      in_process: 'En proceso', expired: 'Expirada',
    };
    return map[(status ?? '').toLowerCase()] ?? status ?? '—';
  }

  isPendingSale(entry: HistoryEntry): boolean {
    return entry.type === 'sale' && entry.status.trim().toLowerCase() === 'pending';
  }

  viewReceipt(entry: HistoryEntry): void {
    if (entry.type !== 'sale' || this.isPendingSale(entry) || this.receiptLoading) return;
    this.error = '';
    this.receiptErrorSaleId = null;
    this.receiptError = '';
    this.receipt = null;
    this.receiptLoading = true;
    this.api.getSaleReceipt(entry.id).subscribe({
      next: (receipt) => {
        this.receipt = receipt;
        this.receiptLoading = false;
      },
      error: (err) => {
        this.receiptLoading = false;
        this.receiptErrorSaleId = entry.id;
        this.receiptError = err.status === 404
          ? 'El comprobante de esta venta todavía no está disponible. Intenta nuevamente más tarde.'
          : 'No se pudo obtener el comprobante. Intenta nuevamente.';
      },
    });
  }

  closeReceipt(): void {
    this.receiptDialog?.close();
    this.receipt = null;
  }

  onReceiptBackdropClick(event: MouseEvent): void {
    if (event.target !== this.receiptDialog || !this.receiptDialog) return;
    const bounds = this.receiptDialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right ||
        event.clientY < bounds.top || event.clientY > bounds.bottom) {
      this.closeReceipt();
    }
  }
}
