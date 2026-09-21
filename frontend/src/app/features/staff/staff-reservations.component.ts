import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface Reservation {
  id: number;
  client_id: number;
  branch_id: number;
  status: string;
  pickup_code: string;
  expires_at: string;
  total_amount: number;
  details: { id: number; variant_id: number; quantity: number; unit_price: number }[];
}

const NEXT_ACTIONS: Record<string, string[]> = {
  PENDING: ['PREPARED', 'CANCELLED'],
  PREPARED: ['IN_TRIAL', 'CANCELLED'],
  IN_TRIAL: ['COMPLETED', 'CANCELLED'],
};

@Component({
  selector: 'app-staff-reservations',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="staff">
      <h2>Recepción y atención de reservas (CU-17 · CU-18)</h2>

      @if (error) {
        <p class="error">{{ error }}</p>
      }

      <div class="filters">
        <button [class.active]="statusFilter()===''" (click)="setFilter('')">Todas</button>
        @for (s of statuses; track s) {
          <button [class.active]="statusFilter()===s" (click)="setFilter(s)">{{ s }}</button>
        }
      </div>

      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Código</th>
            <th>Sucursal</th>
            <th>Estado</th>
            <th>Total</th>
            <th>Vence</th>
            <th>Prendas</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          @for (r of filtered(); track r.id) {
            <tr>
              <td>{{ r.id }}</td>
              <td>{{ r.pickup_code }}</td>
              <td>{{ r.branch_id }}</td>
              <td><span class="badge">{{ r.status }}</span></td>
              <td>{{ r.total_amount }}</td>
              <td>{{ r.expires_at | date: 'short' }}</td>
              <td>
                @for (d of r.details; track d.id) {
                  <div class="detail">variante {{ d.variant_id }} × {{ d.quantity }}</div>
                }
              </td>
              <td>
                @for (action of actionsFor(r.status); track action) {
                  <button (click)="changeStatus(r, action)" [disabled]="loading">
                    {{ label(action) }}
                  </button>
                }
              </td>
            </tr>
          } @empty {
            <tr>
              <td colspan="8">No hay reservas.</td>
            </tr>
          }
        </tbody>
      </table>
    </section>
  `,
  styles: [
    `
      .staff {
        max-width: 1100px;
      }
      .error {
        color: #b00020;
      }
      .filters {
        display: flex;
        gap: 0.4rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
      }
      .filters button {
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        border: 1px solid #cbd5e1;
        background: #fff;
        cursor: pointer;
        font-size: 0.85rem;
      }
      .filters button.active {
        background: var(--color-primary);
        border-color: var(--color-primary);
        color: #fff;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
      }
      th,
      td {
        border: 1px solid #ddd;
        padding: 0.4rem 0.6rem;
        text-align: left;
      }
      .badge {
        display: inline-block;
        background: var(--color-primary-light, #fff3e0);
        color: var(--color-primary-dark, #cc7000);
        border-radius: 12px;
        padding: 0.15rem 0.55rem;
        font-size: 0.75rem;
        font-weight: 600;
      }
      .detail {
        font-size: 0.75rem;
        color: #64748b;
      }
      button {
        cursor: pointer;
        padding: 0.3rem 0.6rem;
        margin-right: 0.25rem;
        font-size: 0.8rem;
      }
      button:disabled {
        opacity: 0.5;
      }
    `,
  ],
})
export class StaffReservationsComponent implements OnInit {
  private auth = inject(AuthService);

  readonly reservations = signal<Reservation[]>([]);
  readonly statusFilter = signal('');
  readonly statuses = ['PENDING', 'PREPARED', 'IN_TRIAL', 'COMPLETED', 'CANCELLED', 'EXPIRED'];

  error = '';
  loading = false;
  selectedBranchId = 1;

  filtered() {
    const f = this.statusFilter();
    return this.reservations().filter((r) => !f || r.status === f);
  }

  actionsFor(status: string): string[] {
    return NEXT_ACTIONS[status] ?? [];
  }

  label(action: string): string {
    switch (action) {
      case 'PREPARED':
        return 'Marcar preparada';
      case 'IN_TRIAL':
        return 'Iniciar prueba';
      case 'COMPLETED':
        return 'Completar / entregar';
      case 'CANCELLED':
        return 'Cancelar';
      default:
        return action;
    }
  }

  ngOnInit(): void {
    this.load();
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.auth.token()) h['Authorization'] = `Bearer ${this.auth.token()}`;
    return h;
  }

  setFilter(s: string): void {
    this.statusFilter.set(s);
  }

  load(): void {
    fetch(`${environment.apiUrl}/reservations`, { headers: this.headers() })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: Reservation[]) => this.reservations.set(data))
      .catch((e) => (this.error = `No se pudieron cargar reservas: ${e}`));
  }

  changeStatus(r: Reservation, action: string): void {
    this.loading = true;
    this.error = '';
    fetch(`${environment.apiUrl}/reservations/${r.id}/status`, {
      method: 'PATCH',
      headers: this.headers(),
      body: JSON.stringify({ status: action }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const b = await res.json().catch(() => ({}));
          throw new Error(b.detail ?? res.statusText);
        }
        return res.json();
      })
      .then(() => this.load())
      .catch((e) => (this.error = e.message ?? String(e)))
      .finally(() => (this.loading = false));
  }
}