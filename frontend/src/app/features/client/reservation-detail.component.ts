import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ClientService } from './client.service';

@Component({
  selector: 'app-client-reservation-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="page">
      <a routerLink="/client/reservations" class="back-link">← Volver a mis reservas</a>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      @if (reservation) {
        <div class="card detail">
          <div class="head">
            <h1 class="title">Reserva #{{ reservation.id }}</h1>
            <span class="badge-status" [class]="'st-' + (reservation.status ?? '').toLowerCase()">
              {{ statusLabel(reservation.status) }}
            </span>
          </div>

          <div class="grid-2">
            <div class="info-block">
              <h3>Sucursal</h3>
              <p>{{ reservation.branch_name ?? 'Sucursal no disponible' }}</p>
            </div>
            <div class="info-block">
              <h3>Información</h3>
              <p>Registrada: {{ reservation.created_at | date:'dd/MM/yyyy HH:mm' }}</p>
              @if (reservation.reservation_code) {
                <p>Código de recogida: <code>{{ reservation.reservation_code }}</code></p>
              }
              @if (reservation.available_until) {
                <p>Disponible hasta: {{ reservation.available_until | date:'dd/MM/yyyy HH:mm' }}</p>
              }
            </div>
          </div>

          @if (reservation.items && reservation.items.length > 0) {
            <h3 class="items-title">Prendas reservadas</h3>
            <div class="items">
              @for (item of reservation.items; track $index) {
                <div class="item">
                  <div class="thumb" *ngIf="item.image_url">
                    <img [src]="item.image_url" [alt]="''" />
                  </div>
                  <div class="item-info">
                    <p class="item-name">{{ item.product_name }}</p>
                    <p class="item-meta">
                      {{ item.size_name || 'Talla única' }} · {{ item.color_name || '' }} · ×{{ item.quantity }}
                    </p>
                  </div>
                  <p class="item-price">Bs {{ (item.unit_price ?? 0) * (item.quantity ?? 1) | number:'1.2-2' }}</p>
                </div>
              }
            </div>
          }

          <div class="footer">
            <p class="total">Total: Bs {{ reservation.total_amount ?? 0 | number:'1.2-2' }}</p>

            <div class="timeline">
              <div class="step done"><span class="dot"></span> Reserva creada</div>
              <div class="step" [class.done]="['PREPARED', 'IN_TRIAL', 'COMPLETED'].includes(reservation.status)">
                <span class="dot"></span> Prendas preparadas
              </div>
              <div class="step" [class.done]="['IN_TRIAL', 'COMPLETED'].includes(reservation.status)">
                <span class="dot"></span> Prueba en tienda
              </div>
            </div>

            @if (canCancel) {
              <button type="button" class="btn btn-danger" (click)="cancel()">
                {{ cancelling ? 'Cancelando...' : 'Cancelar reserva' }}
              </button>
            }
          </div>
        </div>
      } @else if (loading) {
        <div class="loading">Cargando reserva...</div>
      }
    </div>
  `,
  styles: [
    `
      .back-link { display: inline-block; margin-bottom: 1rem; color: var(--color-text-muted); text-decoration: none; }
      .back-link:hover { color: var(--color-primary, #ff8c00); }
      .detail { padding: 1.5rem; }
      .head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
      .title { margin: 0; }
      .badge-status { font-size: 0.8rem; padding: 3px 12px; border-radius: 99px; }
      .st-pending, .st-confirmed { background: #fef3c7; color: #92400e; }
      .st-prepared, .st-in_trial { background: #dcfce7; color: #166534; }
      .st-cancelled, .st-expired { background: #fee2e2; color: #991b1b; }
      .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
      @media (max-width: 600px) { .grid-2 { grid-template-columns: 1fr; } }
      .info-block { background: var(--color-surface-variant, #f8fafc); padding: 1rem; border-radius: 10px; }
      .info-block h3 { margin: 0 0 0.5rem; font-size: 0.9rem; }
      .info-block p { margin: 0.15rem 0; }
      .meta { color: var(--color-text-muted); font-size: 0.85rem; }
      .items-title { margin: 1.25rem 0 0.75rem; }
      .items { display: flex; flex-direction: column; gap: 0.75rem; }
      .item { display: flex; gap: 1rem; align-items: center; padding: 0.75rem; border: 1px solid var(--color-border); border-radius: 10px; }
      .thumb { width: 56px; height: 56px; border-radius: 8px; overflow: hidden; flex-shrink: 0; background: var(--color-surface-variant, #f3f4f6); }
      .thumb img { width: 100%; height: 100%; object-fit: cover; }
      .item-info { flex: 1; }
      .item-name { margin: 0 0 3px; font-weight: 500; }
      .item-meta { margin: 0; font-size: 0.82rem; color: var(--color-text-muted); }
      .item-price { font-weight: 600; }
      .footer { margin-top: 1.5rem; }
      .total { font-size: 1.1rem; font-weight: 700; }
      .timeline { display: flex; gap: 1.5rem; margin: 1rem 0; flex-wrap: wrap; }
      .step { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; color: var(--color-text-muted); }
      .step .dot { width: 12px; height: 12px; border-radius: 50%; background: var(--color-border); }
      .step.done { color: var(--color-text); }
      .step.done .dot { background: var(--color-success, #16a34a); }
      .btn-danger { background: var(--color-error, #ef4444); color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 8px; cursor: pointer; font-weight: 600; }
      .btn-danger:hover { background: #dc2626; }
      .loading { text-align: center; color: var(--color-text-muted); padding: 4rem 0; }
    `,
  ],
})
export class ReservationDetailComponent implements OnInit {
  private api = inject(ClientService);
  private route = inject(ActivatedRoute);

  reservation: any = null;
  loading = false;
  error = '';
  cancelling = false;
  canCancel = false;

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id) return;
    this.loading = true;
    this.api.getReservation(id).subscribe({
      next: (res: any) => {
        this.reservation = res.reservation ?? res.data ?? res;
        const st = (this.reservation.status ?? '').toLowerCase();
        this.canCancel = ['pending', 'prepared', 'in_trial'].includes(st);
        this.loading = false;
      },
      error: () => { this.error = 'No se pudo cargar la reserva.'; this.loading = false; },
    });
  }

  cancel(): void {
    if (!this.canCancel || this.cancelling) return;
    if (!confirm('¿Seguro que deseas cancelar esta reserva?')) return;
    this.cancelling = true;
    this.error = '';
    this.api.cancelReservation(this.reservation.id).subscribe({
      next: (updated: any) => {
        this.reservation.status = updated.status;
        this.canCancel = false;
        this.cancelling = false;
      },
      error: () => { this.error = 'No se pudo cancelar la reserva. Vuelve a cargar la reserva para consultar su estado.'; this.cancelling = false; },
    });
  }

  statusLabel(status: string): string {
    const map: Record<string, string> = {
      pending: 'Pendiente', prepared: 'Preparada', in_trial: 'En prueba',
      cancelled: 'Cancelada', expired: 'Expirada', completed: 'Completada',
    };
    return map[(status ?? '').toLowerCase()] ?? status ?? 'Desconocido';
  }
}