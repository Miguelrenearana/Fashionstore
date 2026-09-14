import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  birth_date?: string;
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule],
  template: `
    <section class="register">
      <h2>Crear cuenta de cliente</h2>
      <form (ngSubmit)="onSubmit()">
        <input type="email" [(ngModel)]="email" name="email" placeholder="Correo" required />
        <input type="password" [(ngModel)]="password" name="password" placeholder="Contraseña" required />
        <input type="text" [(ngModel)]="first_name" name="first_name" placeholder="Nombres" required />
        <input type="text" [(ngModel)]="last_name" name="last_name" placeholder="Apellidos" required />
        <input type="tel" [(ngModel)]="phone" name="phone" placeholder="Teléfono (opcional)" />
        <input type="date" [(ngModel)]="birth_date" name="birth_date" />
        <button type="submit">Registrarse</button>
      </form>
      <p>
        ¿Ya tienes cuenta?
        <a routerLink="/auth">Inicia sesión</a>
      </p>
      @if (error) {
        <p class="error">{{ error }}</p>
      }
    </section>
  `,
  styles: [
    `
      .register {
        max-width: 360px;
        margin: 3rem auto;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
      }
      input,
      button {
        padding: 0.625rem;
        border-radius: 6px;
        border: 1px solid #ccc;
      }
      button {
        background: var(--color-primary);
        color: #fff;
        border: none;
      }
      .error {
        color: #b00020;
      }
    `,
  ],
})
export class RegisterComponent {
  private http = inject(HttpClient);
  private router = inject(Router);
  private auth = inject(AuthService);

  email = '';
  password = '';
  first_name = '';
  last_name = '';
  phone = '';
  birth_date = '';
  error = '';

  onSubmit(): void {
    const payload: RegisterPayload = {
      email: this.email,
      password: this.password,
      first_name: this.first_name,
      last_name: this.last_name,
    };
    if (this.phone) {
      payload.phone = this.phone;
    }
    if (this.birth_date) {
      payload.birth_date = this.birth_date;
    }
    this.http
      .post<{ access_token: string }>(`${environment.apiUrl}/auth/register`, payload)
      .subscribe({
        next: (res) => {
          this.auth.storeToken(res.access_token);
          this.router.navigate(['/catalog']);
        },
        error: () => (this.error = 'No se pudo crear la cuenta. Verifique los datos.'),
      });
  }
}