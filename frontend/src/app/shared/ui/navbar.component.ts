import { Component, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <header class="navbar">
      <a class="brand" routerLink="/catalog">FashionStore</a>
      <nav class="links">
        <a routerLink="/catalog" routerLinkActive="active">Catálogo</a>
        <a routerLink="/cart" routerLinkActive="active">Carrito</a>
        <a routerLink="/reservations" routerLinkActive="active">Reservas</a>
        @if (!auth.isAuthenticated()) {
          <a routerLink="/auth" routerLinkActive="active">Iniciar sesión</a>
        } @else {
          <a routerLink="/profile" routerLinkActive="active">Perfil</a>
          <a routerLink="/branch" routerLinkActive="active">Sucursales</a>
          <a routerLink="/admin" routerLinkActive="active">Admin</a>
          <button (click)="auth.logout()">Salir</button>
        }
      </nav>
    </header>
  `,
  styles: [
    `
      .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1.5rem;
        background: var(--color-primary);
        color: #fff;
      }
      .brand {
        color: #fff;
        font-weight: 700;
        text-decoration: none;
        font-size: 1.25rem;
      }
      .links a {
        color: #fff;
        margin-left: 1rem;
        text-decoration: none;
        opacity: 0.85;
      }
      .links a.active {
        opacity: 1;
        font-weight: 700;
      }
      button {
        margin-left: 1rem;
        background: transparent;
        border: 1px solid #fff;
        color: #fff;
        border-radius: 4px;
        padding: 0.25rem 0.75rem;
      }
    `,
  ],
})
export class NavbarComponent {
  constructor(public auth: AuthService) {}
}