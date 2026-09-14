import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { environment } from '@core/environments/environment';

interface ClientProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  birth_date: string | null;
  points: number;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [FormsModule],
  template: `
    <section class="profile">
      <h2>Mi perfil</h2>
      @if (profile) {
        <form (ngSubmit)="save()">
          <label>
            Correo
            <input type="email" [value]="profile.email" disabled />
          </label>
          <label>
            Nombres
            <input type="text" [(ngModel)]="profile.first_name" name="first_name" required />
          </label>
          <label>
            Apellidos
            <input type="text" [(ngModel)]="profile.last_name" name="last_name" required />
          </label>
          <label>
            Teléfono
            <input type="tel" [(ngModel)]="profile.phone" name="phone" />
          </label>
          <label>
            Fecha de nacimiento
            <input type="date" [(ngModel)]="profile.birth_date" name="birth_date" />
          </label>
          <p class="points">Puntos: {{ profile.points }}</p>
          <button type="submit">Guardar cambios</button>
        </form>
        @if (saved) {
          <p class="ok">Perfil actualizado.</p>
        }
        @if (error) {
          <p class="error">{{ error }}</p>
        }
      }
    </section>
  `,
  styles: [
    `
      .profile {
        max-width: 420px;
        margin: 2rem auto;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
      }
      label {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }
      input,
      button {
        padding: 0.5rem;
        border-radius: 6px;
        border: 1px solid #ccc;
      }
      button {
        background: var(--color-primary);
        color: #fff;
        border: none;
      }
      .points {
        color: #666;
      }
      .error {
        color: #b00020;
      }
      .ok {
        color: #1a7f37;
      }
    `,
  ],
})
export class ProfileComponent {
  private http = inject(HttpClient);
  profile: ClientProfile | null = null;
  saved = false;
  error = '';

  constructor() {
    this.http
      .get<ClientProfile>(`${environment.apiUrl}/clients/me`)
      .subscribe({
        next: (p) => {
          this.profile = p;
          if (!p.phone) {
            this.profile.phone = '';
          }
          if (!p.birth_date) {
            this.profile.birth_date = '';
          }
        },
        error: () => (this.error = 'No se pudo cargar el perfil.'),
      });
  }

  save(): void {
    if (!this.profile) {
      return;
    }
    this.http
      .patch<ClientProfile>(`${environment.apiUrl}/clients/me`, {
        first_name: this.profile.first_name,
        last_name: this.profile.last_name,
        phone: this.profile.phone || null,
        birth_date: this.profile.birth_date || null,
      })
      .subscribe({
        next: () => (this.saved = true),
        error: () => (this.error = 'No se pudo guardar el perfil.'),
      });
  }
}