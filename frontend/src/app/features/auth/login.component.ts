import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  template: `
    <section class="login">
      <h2>Iniciar sesiÃ³n</h2>
      <form (ngSubmit)="onSubmit()">
        <input
          type="email"
          name="email"
          [(ngModel)]="email"
          placeholder="usuario@fashionstore.dev"
          required
        />
        <input
          type="password"
          name="password"
          [(ngModel)]="password"
          placeholder="ContraseÃ±a"
          required
        />
        <button type="submit">Entrar</button>
      </form>
      <p>
        <a routerLink="/auth/forgot-password">Olvidé mi contraseña</a>
      </p>
      @if (error) {
        <p class="error">{{ error }}</p>
      }
    </section>
  `,
  styles: [
    `
      .login {
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
export class LoginComponent {
  email = '';
  password = '';
  error = '';

  constructor(private auth: AuthService, private router: Router) {}

  onSubmit(): void {
    this.auth.login(this.email, this.password).subscribe({
      next: () => this.router.navigate([this.auth.homeRoute()]),
      error: () => (this.error = 'Credenciales inválidas'),
    });
  }
}