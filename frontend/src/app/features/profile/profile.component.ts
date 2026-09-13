import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@core/environments/environment';

@Component({
  selector: 'app-profile',
  standalone: true,
  template: `
    <section>
      <h2>Mi perfil</h2>
      @if (user) {
        <p><strong>Email:</strong> {{ user.email }}</p>
      }
    </section>
  `,
})
export class ProfileComponent {
  private http = inject(HttpClient);
  user: { email: string } | null = null;

  constructor() {
    this.http.get<{ email: string }>(`${environment.apiUrl}/users/me`).subscribe((u) => {
      this.user = u;
    });
  }
}