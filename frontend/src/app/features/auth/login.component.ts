import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';
import { UiButtonComponent } from '@shared/ui/button';
import { UiInputComponent } from '@shared/ui/input';
import { UiCardComponent } from '@shared/ui/card';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, UiButtonComponent, UiInputComponent, UiCardComponent],
  template: `
    <section class="login">
      <h2>Iniciar sesión</h2>
      <form (ngSubmit)="onSubmit()" class="flex flex-col gap-4">
        <ui-input
          label="Email"
          type="email"
          placeholder="usuario@fashionstore.dev"
          [(ngModel)]="email"
          name="email"
          required
        />
        <ui-input
          label="Contraseña"
          type="password"
          placeholder="••••••••"
          [(ngModel)]="password"
          name="password"
          required
        />
        <ui-button variant="primary" size="lg" type="submit" class="w-full" [loading]="loading">
          Entrar
        </ui-button>
      </form>
      @if (error) {
        <p class="form-error mt-3">{{ error }}</p>
      }
      <p class="text-center text-sm text-secondary mt-4">
        <a routerLink="/auth/forgot-password" class="text-primary hover:underline">¿Olvidé mi contraseña?</a>
      </p>
    </section>
  `,
  styles: [
    `
      .login {
        max-width: 380px;
        margin: 3rem auto;
        padding: 0 1rem;
      }
      h2 {
        text-align: center;
        margin-bottom: 1.5rem;
      }
    `,
  ],
})
export class LoginComponent {
  email = '';
  password = '';
  loading = false;
  error = '';

  constructor(private auth: AuthService, private router: Router) {}

  onSubmit(): void {
    if (!this.email || !this.password) return;
    this.loading = true;
    this.error = '';
    this.auth.login(this.email, this.password).subscribe({
      next: () => this.router.navigate([this.auth.homeRoute()]),
      error: (e) => {
        this.error = typeof e === 'string' ? e : 'Credenciales inválidas';
        this.loading = false;
      },
    });
  }
}
