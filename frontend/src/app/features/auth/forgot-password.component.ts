import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '@core/environments/environment';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [FormsModule],
  template: `
    <section class="forgot">
      <h2>Recuperar contraseña</h2>
      <form (ngSubmit)="onSubmit()">
        <input type="email" [(ngModel)]="email" name="email" placeholder="usuario@fashionstore.dev" required />
        <button type="submit">Enviar token</button>
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
      .forgot {
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
export class ForgotPasswordComponent {
  private http = inject(HttpClient);

  email = '';
  message = '';
  error = '';

  onSubmit(): void {
    this.http
      .post<{ message: string }>(`${environment.apiUrl}/auth/forgot-password`, {
        email: this.email,
      })
      .subscribe({
        next: (res) => {
          this.message = res.message;
          this.error = '';
        },
        error: () => (this.error = 'No se pudo procesar la solicitud.'),
      });
  }
}