import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@core/environments/environment';

interface Reservation {
  id: number;
  pickup_code: string;
  status: string;
  total_amount: number;
}

@Component({
  selector: 'app-reservations',
  standalone: true,
  template: `
    <section>
      <h2>Mis reservas</h2>
      @for (r of reservations(); track r.id) {
        <p>
          <strong>{{ r.pickup_code }}</strong> — {{ r.status }} — Bs {{ r.total_amount }}
        </p>
      } @empty {
        <p>No tienes reservas todavía.</p>
      }
    </section>
  `,
})
export class ReservationsComponent {
  private http = inject(HttpClient);
  readonly reservations = signal<Reservation[]>([]);

  constructor() {
    this.http
      .get<Reservation[]>(`${environment.apiUrl}/reservations/me`)
      .subscribe((res) => this.reservations.set(res));
  }
}