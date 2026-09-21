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
      <h2>Iniciar sesión</h2>
      <form (ngSubmit)="onSubmit()">
        <div class="form-field">
          <label class="form-label" for="email">Email</label>
          <input
            id="email"
            type="email"
            [(ngModel)]="email"
            placeholder="usuario@fashionstore.dev"
            required
          />
        </div>
        <div class="form-field">
          <label class="form-label" for="password">Contraseña</label>
          <input
            id="password"
            type="password"
            [(ngModel)]="password"
            placeholder="••••••••"
            required
          />
        </div>
        <button type="submit" class="btn btn-primary w-full">Entrar</button>
        <p class="text-center text-sm mt-4">
          <a routerLink="/auth/forgot-password" class="text-primary hover:underline">¿Olvidé mi contraseña?</a>
        </p>
      </form>
      @if (error) {
        <p class="form-error mt-3">{{ error }}</p>
      }
    </section>
  `,
  styles: []
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