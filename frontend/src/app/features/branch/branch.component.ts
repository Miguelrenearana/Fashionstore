import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface City {
  id: number;
  name: string;
  state: string;
}

interface Branch {
  id: number;
  name: string;
  address: string;
  phone?: string;
  city: { id: number; name: string; state: string } | null;
}

@Component({
  selector: 'app-branch',
  standalone: true,
  imports: [FormsModule],
  template: `
    <section class="branch">
      <h2>Sucursales</h2>
      <div class="grid">
        @for (b of branches(); track b.id) {
          <article class="card">
            <h3>{{ b.name }}</h3>
            <p>{{ b.city?.name }} · {{ b.city?.state }}</p>
            <p>{{ b.address }}</p>
            @if (b.phone) {
              <p>Tel: {{ b.phone }}</p>
            }
          </article>
        } @empty {
          <p>No hay sucursales registradas.</p>
        }
      </div>

      <form class="card-new" (ngSubmit)="createBranch()">
        <h3>Nueva sucursal</h3>
        <input [(ngModel)]="form.name" name="name" placeholder="Nombre" required />
        <input [(ngModel)]="form.address" name="address" placeholder="Dirección" required />
        <select [(ngModel)]="form.city_id" name="city_id" required>
          <option [ngValue]="0" disabled>Ciudad...</option>
          @for (city of cities(); track city.id) {
            <option [ngValue]="city.id">{{ city.name }} ({{ city.state }})</option>
          }
        </select>
        <input [(ngModel)]="form.phone" name="phone" placeholder="Teléfono (opcional)" />
        <button type="submit" [disabled]="saving()">Crear sucursal</button>
        <p class="msg">{{ message() }}</p>
      </form>
    </section>
  `,
  styles: [
    `
      .branch {
        padding: 1.5rem;
        max-width: 960px;
        margin: 0 auto;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
      }
      .card,
      .card-new {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        background: #fff;
      }
      .card h3,
      .card-new h3 {
        margin-top: 0;
      }
      .card-new {
        max-width: 420px;
      }
      .card-new input,
      .card-new select {
        display: block;
        width: 100%;
        box-sizing: border-box;
        margin-bottom: 0.5rem;
        padding: 0.4rem;
      }
      button {
        padding: 0.5rem 1rem;
        background: var(--color-primary);
        color: #fff;
        border: none;
        border-radius: 6px;
        cursor: pointer;
      }
      button:disabled {
        opacity: 0.6;
      }
      .msg {
        margin: 0.5rem 0 0;
        font-size: 0.85rem;
      }
    `,
  ],
})
export class BranchComponent implements OnInit {
  private auth = inject(AuthService);
  readonly branches = signal<Branch[]>([]);
  readonly cities = signal<City[]>([]);
  readonly saving = signal(false);
  readonly message = signal('');

  form = { name: '', address: '', city_id: 0, phone: '' };

  ngOnInit(): void {
    fetch(`${environment.apiUrl}/locations/branches`)
      .then((r) => r.json())
      .then((data: Branch[]) => this.branches.set(data));
    fetch(`${environment.apiUrl}/locations/cities`)
      .then((r) => r.json())
      .then((data: City[]) => this.cities.set(data));
  }

  createBranch(): void {
    this.saving.set(true);
    this.message.set('');
    fetch(`${environment.apiUrl}/locations/branches`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.auth.token()}`,
      },
      body: JSON.stringify(this.form),
    })
      .then(async (r) => {
        if (!r.ok) {
          const body = (await r.json()) as { detail?: string };
          throw new Error(body.detail ?? r.statusText);
        }
        return r.json();
      })
      .then((branch: Branch) => {
        this.branches.set([...this.branches(), branch]);
        this.form = { name: '', address: '', city_id: 0, phone: '' };
        this.message.set('Sucursal creada.');
      })
      .catch((e) => this.message.set(`Error: ${e.message}`))
      .finally(() => this.saving.set(false));
  }
}