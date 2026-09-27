import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ClientService } from './client.service';

@Component({
  selector: 'app-client-purchase-history',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="page">
      <h1 class="page-title">Historial de compras</h1>
      <p class="page-subtitle">Todas tus compras y sus comprobantes.</p>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      @if (loading) {
        <div class="loading">Cargando historial...</div>
      } @else if (entries.length === 0) {
        <div class="empty card">
          <p>No tienes compras registradas.</p>
          <a routerLink="/client/catalog" class="btn btn-primary">Ir al catálogo</a>
        </div>
      } @else {
        <div class="list">
          @for (entry of entries; track entry.id) {
            <div class="entry card">
              <div class="entry-head">
                <div>
                  <strong>{{ entry.type === 'sale' ? 'Pedido' : 'Reserva' }} #{{ entry.id }}</strong>
                  <span class="badge-status" [class]="'st-' + (entry.status ?? '').toLowerCase()">
                    {{ statusLabel(entry.status) }}
                  </span>
                </div>
                <span class="date">{{ entry.created_at | date:'dd/MM/yyyy HH:mm' }}</span>
              </div>

              @if (entry.items && entry.items.length > 0) {
                <div class="items">
                  @for (item of entry.items; track $index) {
                    <div class="item-row">
                      <span class="item-name">{{ item.product_name }}</span>
                      <span class="item-qty">×{{ item.quantity }}</span>
                      <span class="item-price">S/{{ (item.price ?? 0) * (item.quantity ?? 1) | number:'1.2-2' }}</span>
                    </div>
                  }
                </div>
              }

              <div class="entry-footer">
                <span class="total">Total: S/{{ entry.total ?? 0 | number:'1.2-2' }}</span>
                @if (entry.id) {
                  <button type="button" class="btn btn-outline btn-sm" (click)="viewReceipt(entry)">
                    Ver comprobante
                  </button>
                }
              </div>
            </div>
          }
        </div>

        @if (receipt) {
          <div class="modal-backdrop" (click)="closeReceipt()">
            <div class="modal card" (click)="$event.stopPropagation()">
              <div class="modal-head">
                <h2>Comprobante</h2>
                <button type="button" class="btn btn-ghost btn-sm" (click)="closeReceipt()">✕</button>
              </div>
              <div class="receipt">
                <h3>FashionStore</h3>
                <p class="meta">RUC: 123456789012</p>
                <p class="meta">Comprobante #{{ receipt.id ?? receipt.number ?? '—' }}</p>
                <hr />
                @if (receipt.items && receipt.items.length > 0) {
                  @for (item of receipt.items; track $index) {
                    <div class="r-row">
                      <span>{{ item.product_name ?? item.name }}</span>
                      <span>S/{{ (item.price ?? item.unit_price ?? 0) * (item.quantity ?? 1) | number:'1.2-2' }}</span>
                    </div>
                  }
                }
                <hr />
                @if (receipt.amount || receipt.total) {
                  <div class="r-row total-row"><strong>Total</strong><strong>S/{{ (receipt.amount ?? receipt.total) | number:'1.2-2' }}</strong></div>
                }
                <p class="meta" *ngIf="receipt.created_at">Emitido: {{ receipt.created_at | date:'dd/MM/yyyy HH:mm' }}</p>
              </div>
            </div>
          </div>
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
      .entry-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--color-border); padding-top: 0.75rem; }
      .total { font-weight: 700; }
      .loading { text-align: center; color: var(--color-text-muted); padding: 4rem 0; }
      .empty { text-align: center; padding: 3rem 1rem; }
      .empty p { margin-bottom: 1rem; }
      .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 200; }
      .modal { max-width: 420px; width: 90%; padding: 1.5rem; }
      .modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
      .modal-head h2 { margin: 0; }
      .receipt { border: 1px dashed var(--color-border); padding: 1rem; font-size: 0.9rem; }
      .receipt h3 { margin: 0 0 4px; }
      .meta { color: var(--color-text-muted); font-size: 0.8rem; margin: 2px 0; }
      .r-row { display: flex; justify-content: space-between; padding: 0.2rem 0; }
      .total-row { border-top: 1px solid var(--color-border); margin-top: 0.5rem; padding-top: 0.5rem; }
    `,
  ],
})
export class PurchaseHistoryComponent implements OnInit {
  private api = inject(ClientService);

  entries: any[] = [];
  receipt: any = null;
  loading = false;
  error = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.api.getHistory(1, 50).subscribe({
      next: (res: any) => {
        const data = res.items ?? res.data ?? (Array.isArray(res) ? res : []);
        this.entries = Array.isArray(data) ? data : [];
        this.loading = false;
        if (this.entries.length === 0) this.loadReceipts();
      },
      error: () => { this.error = 'No se pudo cargar el historial.'; this.loading = false; },
    });
  }

  loadReceipts(): void {
    this.api.getReceipts(1, 50).subscribe({
      next: (res: any) => {
        const data = res.items ?? res.data ?? (Array.isArray(res) ? res : []);
        if (Array.isArray(data) && data.length) {
          this.entries = data.map((r: any) => ({
            id: r.id,
            created_at: r.created_at,
            total: r.amount ?? r.total,
            status: r.status ?? 'completed',
            type: 'sale',
            items: r.items ?? [],
          }));
        }
      },
      error: () => {},
    });
  }

  statusLabel(status: string): string {
    const map: Record<string, string> = {
      completed: 'Completada', paid: 'Pagada', pending: 'Pendiente',
      refunded: 'Reembolsada', cancelled: 'Cancelada', confirmed: 'Confirmada',
      in_process: 'En proceso',
    };
    return map[(status ?? '').toLowerCase()] ?? status ?? '—';
  }

  viewReceipt(entry: any): void {
    this.api.getReceipt(entry.id).subscribe({
      next: (res: any) => (this.receipt = res.receipt ?? res.data ?? res),
      error: () => {
        this.api.getSale(entry.id).subscribe({
          next: (sale: any) => {
            const s = sale.sale ?? sale.data ?? sale;
            this.receipt = {
              id: s.id,
              amount: s.total,
              created_at: s.created_at,
              items: s.items ?? [],
            };
          },
          error: () => (this.error = 'No se pudo obtener el comprobante.'),
        });
      },
    });
  }

  closeReceipt(): void {
    this.receipt = null;
  }
}