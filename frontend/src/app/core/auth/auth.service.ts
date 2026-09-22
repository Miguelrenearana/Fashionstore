import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { environment } from '@core/environments/environment';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  birth_date?: string;
}

const STAFF_ROLES = ['ADMIN', 'MANAGER', 'CASHIER', 'BRANCH_MANAGER'];

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly token = signal<string | null>(localStorage.getItem('fs_token'));

  constructor(private http: HttpClient, private router: Router) {}

  login(email: string, password: string): Observable<LoginResponse> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);

    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/login`, body.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .pipe(
        tap((res) => {
          localStorage.setItem('fs_token', res.access_token);
          this.token.set(res.access_token);
        })
      );
  }

  registerClient(payload: RegisterPayload): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/register`, payload)
      .pipe(
        tap((res) => {
          localStorage.setItem('fs_token', res.access_token);
          this.token.set(res.access_token);
        })
      );
  }

  logout(): void {
    localStorage.removeItem('fs_token');
    this.token.set(null);
    this.router.navigate(['/']);
  }

  isAuthenticated(): boolean {
    return this.token() !== null;
  }

  storeToken(access_token: string): void {
    localStorage.setItem('fs_token', access_token);
    this.token.set(access_token);
  }

  /** Roles del JWT (claim `roles`), sin dependencia del servidor. */
  roles(): string[] {
    const token = this.token();
    if (!token) return [];
    try {
      const payloadPart = token.split('.')[1];
      if (!payloadPart) return [];
      const json = atob(payloadPart.replace(/-/g, '+').replace(/_/g, '/'));
      const payload = JSON.parse(json) as { roles?: string[] };
      return payload.roles ?? [];
    } catch {
      return [];
    }
  }

  hasAnyRole(...roles: string[]): boolean {
    const mine = new Set(this.roles());
    return roles.some((r) => mine.has(r));
  }

  /** ¿Es personal autorizado para la consola web (admin/staff/pos)? */
  isStaff(): boolean {
    return this.hasAnyRole(...STAFF_ROLES);
  }

  /** Ruta de inicio según rol tras iniciar sesión. */
  homeRoute(): string {
    if (this.hasAnyRole('ADMIN', 'MANAGER')) return '/admin';
    if (this.hasAnyRole('BRANCH_MANAGER', 'CASHIER')) return '/staff';
    return '/';
  }
}