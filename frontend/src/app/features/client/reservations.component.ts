import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ClientService } from './client.service';

@Component({
  selector: 'app-client-reservations',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="page">
      <h1 class="page-title">Mis reservas</h1>
      <p class="page-subtitle">Reservas de prendas para probar en tienda.</p>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      @if (loading) {
        <div class="loading">Cargando reservas...</div>
      } @else if (reservations.length === 0) {
        <div class="empty card">
          <p>No tienes reservas registradas.</p>
          <a routerLink="/client/catalog" class="btn btn-primary">Explorar el catálogo</a>
        </div>
      } @else {
        <div class="list">
          @for (r of reservations; track r.id) {
            <a class="reservation card" [routerLink]="['/client/reservations', r.id]">
              <div class="res-head">
                <strong>Reserva #{{ r.id }}</strong>
                <span class="badge-status" [class]="'st-' + (r.status ?? '').toLowerCase()">
                  {{ statusLabel(r.status) }}
                </span>
              </div>
              <div class="res-row">
                <span class="meta">Sucursal:</span>
                <span>{{ r.branch?.name ?? 'Sucursal principal' }}</span>
              </div>
              @if (r.reservation_code) {
                <div class="res-row">
                  <span class="meta">Código de recogida:</span>
                  <code>{{ r.reservation_code }}</code>
                </div>
              }
              <div class="res-row">
                <span class="meta">Fecha:</span>
                <span>{{ r.created_at | date:'dd/MM/yyyy HH:mm' }}</span>
              </div>
              @if (r.items && r.items.length > 0) {
                <div class="res-row">
                  <span class="meta">Prendas:</span>
                  <span>{{ itemsLabel(r.items) }}</span>
                </div>
              }
              <div class="res-row total">
                <span class="meta">Total:</span>
                <span>S/{{ r.total ?? 0 | number:'1.2-2' }}</span>
              </div>
            </a>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      .page-title { margin-bottom: 4px; }
      .page-subtitle { color: var(--color-text-muted); margin-bottom: 1.25rem; }
      .list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
      .reservation { padding: 1.25rem; text-decoration: none; color: inherit; display: block; transition: transform 0.15s, box-shadow 0.15s; }
      .reservation:hover { transform: translateY(-3px); box-shadow: 0 6px 18px rgba(0,0,0,0.1); }
      .res-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
      .res-row { display: flex; gap: 0.5rem; padding: 0.2rem 0; font-size: 0.9rem; }
      .res-row .meta { color: var(--color-text-muted); }
      .res-row.total { border-top: 1px solid var(--color-border); margin-top: 0.5rem; padding-top: 0.6rem; font-weight: 600; }
      .badge-status { font-size: 0.75rem; padding: 2px 10px; border-radius: 99px; }
      .st-pending, .st-confirmed { background: #fef3c7; color: #92400e; }
      .st-ready, .st-pickedup { background: #dcfce7; color: #166534; }
      .st-cancelled, .st-expired { background: #fee2e2; color: #991b1b; }
      .loading { text-align: center; color: var(--color-text-muted); padding: 4rem 0; }
      .empty { text-align: center; padding: 3rem 1rem; }
      .empty p { margin-bottom: 1rem; }
    `,
  ],
})
export class ReservationsComponent implements OnInit {
  private api = inject(ClientService);

  reservations: any[] = [];
  loading = false;
  error = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.api.getMyReservations().subscribe({
      next: (res: any) => {
        this.reservations = Array.isArray(res) ? res : (res?.items ?? []);
        this.loading = false;
      },
      error: () => { this.error = 'No se pudieron cargar las reservas.'; this.loading = false; },
    });
  }

  statusLabel(status: string): string {
    const map: Record<string, string> = {
      pending: 'Pendiente', confirmed: 'Confirmada', ready: 'Lista para recoger',
      picked_up: 'Recogida', pickedup: 'Recogida', cancelled: 'Cancelada', expired: 'Expirada',
    };
    return map[(status ?? '').toLowerCase()] ?? status ?? 'Desconocido';
  }

  itemsLabel(items: any[]): string {
    return items.map((i) => `${i.product_name ?? 'Producto'} ×${i.quantity}`).join(', ');
  }
}