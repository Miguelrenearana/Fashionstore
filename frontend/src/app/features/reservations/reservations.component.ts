import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DatePipe } from '@angular/common';
import { environment } from '@core/environments/environment';

interface Reservation {
  id: number;
  pickup_code: string;
  status: string;
  total_amount: number;
  expires_at: string;
}

@Component({
  selector: 'app-reservations',
  standalone: true,
  imports: [DatePipe],
  template: `
    <section>
      <h2>Mis reservas</h2>
      @if (error) {
        <p class="error">{{ error }}</p>
      }
      @for (r of reservations(); track r.id) {
        <div class="reservation">
          <p>
            <strong>{{ r.pickup_code }}</strong> — {{ label(r.status) }} — Bs {{ r.total_amount }}
            — vence {{ r.expires_at | date : 'short' }}
          </p>
          @if (r.status === 'PENDING') {
            <button class="link" (click)="cancel(r.id)">Cancelar reserva</button>
          }
        </div>
      } @empty {
        <p>No tienes reservas todavía.</p>
      }
    </section>
  `,
  styles: [
    `
      section {
        padding: 1.5rem;
        max-width: 640px;
        margin: 0 auto;
      }
      .reservation {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
      }
      .link {
        background: none;
        border: none;
        color: #b00020;
        text-decoration: underline;
        cursor: pointer;
      }
      .error {
        color: #b00020;
      }
    `,
  ],
})
export class ReservationsComponent {
  private http = inject(HttpClient);
  readonly reservations = signal<Reservation[]>([]);
  error = '';

  constructor() {
    this.load();
  }

  load(): void {
    this.http
      .get<Reservation[]>(`${environment.apiUrl}/reservations/me`)
      .subscribe((res) => this.reservations.set(res));
  }

  cancel(id: number): void {
    this.error = '';
    this.http
      .patch<Reservation>(`${environment.apiUrl}/reservations/${id}/status`, {
        status: 'CANCELLED',
        comment: 'Cancelada por el cliente',
      })
      .subscribe({
        next: () => this.load(),
        error: (e) => (this.error = e.error?.detail ?? 'No se pudo cancelar la reserva.'),
      });
  }

  label(status: string): string {
    const map: Record<string, string> = {
      PENDING: 'Pendiente',
      PREPARED: 'Preparada',
      IN_TRIAL: 'En probador',
      COMPLETED: 'Completada',
      CANCELLED: 'Cancelada',
      EXPIRED: 'Vencida',
    };
    return map[status] ?? status;
  }
}