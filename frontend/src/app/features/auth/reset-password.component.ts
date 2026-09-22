import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { environment } from '@core/environments/environment';
import { UiButtonComponent } from '@shared/ui/button';
import { UiInputComponent } from '@shared/ui/input';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, FormsModule, UiButtonComponent, UiInputComponent],
  template: `
    <section class="login w-full max-w-md mx-auto mt-20 p-6">
      <h2 class="text-2xl font-semibold mb-6 text-center">Restablecer contraseña</h2>
      <form (ngSubmit)="onSubmit()" class="flex flex-col gap-4">
        <ui-input
          label="Token de recuperación"
          type="text"
          placeholder="Token recibido por email"
          [(ngModel)]="token"
          name="token"
          required
          [error]="error"
        />
        <ui-input
          label="Nueva contraseña"
          type="password"
          placeholder="••••••••"
          [(ngModel)]="password"
          name="password"
          required
          [error]="error"
        />
        <ui-button variant="primary" size="lg" class="w-full" type="submit" [loading]="loading">
          Restablecer
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
export class ResetPasswordComponent {
  private http = inject(HttpClient);
  private route = inject(ActivatedRoute);

  token = '';
  password = '';
  message = '';
  error = '';
  loading = false;

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['token']) {
        this.token = params['token'];
      }
    });
  }

  onSubmit(): void {
    this.error = '';
    this.message = '';
    this.loading = true;

    this.http
      .post<{ message: string }>(`${environment.apiUrl}/auth/reset-password`, {
        token: this.token,
        password: this.password,
      })
      .subscribe({
        next: (res) => {
          this.message = res.message;
          this.loading = false;
        },
        error: () => {
          this.error = 'Token inválido, expirado o ya utilizado.';
          this.loading = false;
        },
      });
  }
}