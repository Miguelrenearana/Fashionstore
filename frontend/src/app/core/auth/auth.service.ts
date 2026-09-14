import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { environment } from '@core/environments/environment';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

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

  logout(): void {
    localStorage.removeItem('fs_token');
    this.token.set(null);
    this.router.navigate(['/catalog']);
  }

  isAuthenticated(): boolean {
    return this.token() !== null;
  }

  storeToken(access_token: string): void {
    localStorage.setItem('fs_token', access_token);
    this.token.set(access_token);
  }
}