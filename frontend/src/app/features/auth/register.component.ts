import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';
import { UiButtonComponent } from '@shared/ui/button';
import { UiInputComponent } from '@shared/ui/input';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, UiButtonComponent, UiInputComponent],
  template: `
    <section class="login">
      <h2>Crear cuenta</h2>
      <p class="text-center text-sm text-secondary mb-4">
        Regístrate para reservar prendas y comprar en línea.
      </p>
      <form (ngSubmit)="onSubmit()" class="flex flex-col gap-4">
        <div class="grid gap-4 sm:grid-cols-2">
          <ui-input
            label="Nombre"
            type="text"
            placeholder="Nombre"
            [(ngModel)]="first_name"
            name="first_name"
            required
            [error]="errors.first_name"
          />
          <ui-input
            label="Apellido"
            type="text"
            placeholder="Apellido"
            [(ngModel)]="last_name"
            name="last_name"
            required
            [error]="errors.last_name"
          />
        </div>
        <ui-input
          label="Email"
          type="email"
          placeholder="usuario@example.com"
          [(ngModel)]="email"
          name="email"
          required
          [error]="errors.email"
        />
        <ui-input
          label="Teléfono"
          type="tel"
          placeholder="+591 ..."
          [(ngModel)]="phone"
          name="phone"
        />
        <ui-input
          label="Fecha de nacimiento"
          type="date"
          [(ngModel)]="birth_date"
          name="birth_date"
        />
        <ui-input
          label="Contraseña"
          type="password"
          placeholder="Mínimo 8 caracteres"
          [(ngModel)]="password"
          name="password"
          required
          [error]="errors.password"
        />
        <ui-button variant="primary" size="lg" type="submit" class="w-full" [loading]="loading">
          Registrarme
        </ui-button>
      </form>
      @if (error) {
        <p class="form-error mt-3 text-center">{{ error }}</p>
      }
      <p class="text-center text-sm text-secondary mt-4">
        ¿Ya tienes cuenta?
        <a routerLink="/auth" class="text-primary hover:underline">Inicia sesión</a>
      </p>
    </section>
  `,
  styles: [
    `
      .login {
        max-width: 440px;
        margin: 3rem auto;
        padding: 0 1rem;
      }
      h2 {
        text-align: center;
        margin-bottom: 0.5rem;
      }
    `,
  ],
})
export class RegisterComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  email = '';
  password = '';
  first_name = '';
  last_name = '';
  phone = '';
  birth_date = '';
  loading = false;
  error = '';
  errors: Record<string, string> = {};

  onSubmit(): void {
    this.error = '';
    this.errors = {};

    if (!this.first_name.trim() || this.first_name.trim().length < 2) {
      this.errors.first_name = 'Ingresa un nombre válido.';
    }
    if (!this.last_name.trim() || this.last_name.trim().length < 2) {
      this.errors.last_name = 'Ingresa un apellido válido.';
    }
    if (!this.email.trim()) {
      this.errors.email = 'El email es obligatorio.';
    }
    if (!this.password || this.password.length < 8) {
      this.errors.password = 'La contraseña debe tener al menos 8 caracteres.';
    }
    if (Object.keys(this.errors).length) return;

    this.loading = true;
    this.auth.registerClient({
      email: this.email.trim(),
      password: this.password,
      first_name: this.first_name.trim(),
      last_name: this.last_name.trim(),
      phone: this.phone.trim() || undefined,
      birth_date: this.birth_date || undefined,
    }).subscribe({
      next: () => {
        this.router.navigate([this.auth.homeRoute()]);
      },
      error: (e) => {
        this.error = typeof e === 'string' ? e : 'No se pudo crear la cuenta.';
        this.loading = false;
      },
    });
  }
}