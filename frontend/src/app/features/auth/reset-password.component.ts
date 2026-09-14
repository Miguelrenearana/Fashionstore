import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '@core/environments/environment';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [FormsModule],
  template: `
    <section class="reset">
      <h2>Restablecer contraseña</h2>
      <form (ngSubmit)="onSubmit()">
        <input type="text" [(ngModel)]="token" name="token" placeholder="Token de recuperación" required />
        <input type="password" [(ngModel)]="password" name="password" placeholder="Nueva contraseña" required />
        <button type="submit">Restablecer</button>
      </form>
      @if (message) {
        <p class="ok">{{ message }}</p>
      }
      @if (error) {
        <p class="error">{{ error }}</p>
      }
      <p>
        <a routerLink="/auth">Volver al inicio de sesión</a>
      </p>
    </section>
  `,
  styles: [
    `
      .reset {
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
      .ok {
        color: #1a7f37;
      }
    `,
  ],
})
export class ResetPasswordComponent {
  private http = inject(HttpClient);

  token = '';
  password = '';
  message = '';
  error = '';

  onSubmit(): void {
    this.http
      .post<{ message: string }>(`${environment.apiUrl}/auth/reset-password`, {
        token: this.token,
        password: this.password,
      })
      .subscribe({
        next: (res) => {
          this.message = res.message;
          this.error = '';
        },
        error: () => (this.error = 'Token inválido, expirado o ya utilizado.'),
      });
  }
}