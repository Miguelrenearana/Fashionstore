import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '@core/environments/environment';
import { UiButtonComponent } from '@shared/ui/button';
import { UiInputComponent } from '@shared/ui/input';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, UiButtonComponent, UiInputComponent],
  template: `
    <section class="login w-full max-w-md mx-auto mt-20 p-6">
      <h2 class="text-2xl font-semibold mb-6 text-center">Recuperar contraseña</h2>
      <form (ngSubmit)="onSubmit()" class="flex flex-col gap-4">
        <ui-input
          label="Email"
          type="email"
          placeholder="usuario@fashionstore.dev"
          [(ngModel)]="email"
          name="email"
          required
          [error]="error"
        />
        <ui-button variant="primary" size="lg" class="w-full" type="submit" [loading]="loading">
          Enviar token
        </ui-button>
      </form>
      @if (message) {
        <p class="form-ok text-center">{{ message }}</p>
      }
      @if (error) {
        <p class="form-error text-center">{{ error }}</p>
      }
      <p class="text-center text-sm text-text-muted mt-4">
        <a routerLink="/auth" class="text-primary hover:underline">Volver al inicio de sesión</a>
      </p>
    </section>
  `,
  styles: []
})
export class ForgotPasswordComponent {
  private http = inject(HttpClient);

  email = '';
  message = '';
  error = '';
  loading = false;

  onSubmit(): void {
    this.error = '';
    this.message = '';
    this.loading = true;

    this.http
      .post<{ message: string }>(`${environment.apiUrl}/auth/forgot-password`, {
        email: this.email,
      })
      .subscribe({
        next: (res) => {
          this.message = res.message;
          this.loading = false;
        },
        error: () => {
          this.error = 'No se pudo procesar la solicitud.';
          this.loading = false;
        },
      });
  }
}