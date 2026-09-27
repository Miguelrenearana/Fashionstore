import { Component, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet, Router } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';

@Component({
  selector: 'app-client-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <div class="shell">
      <aside class="sidebar">
        <a routerLink="/client/catalog" class="brand">
          <span class="brand-dot"></span>
          <span class="brand-text">FashionStore</span>
        </a>

        <nav class="nav" aria-label="Navegación del cliente">
          <a routerLink="/client/catalog" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }" class="nav-link">
            🛍️ Catálogo
          </a>
          <a routerLink="/client/reservations" routerLinkActive="active" class="nav-link">
            📦 Mis reservas
          </a>
          <a routerLink="/client/cart" routerLinkActive="active" class="nav-link">
            🛒 Carrito
            @if (cartCount > 0) {
              <span class="badge badge-cart">{{ cartCount }}</span>
            }
          </a>
          <a routerLink="/client/recommendations" routerLinkActive="active" class="nav-link">
            ✨ Recomendados (IA)
          </a>
          <a routerLink="/client/chat" routerLinkActive="active" class="nav-link">
            💬 Asistente IA
          </a>
          <a routerLink="/client/history" routerLinkActive="active" class="nav-link">
            📋 Historial de compras
          </a>
          <a routerLink="/client/notifications" routerLinkActive="active" class="nav-link">
            🔔 Notificaciones
            @if (notifCount > 0) {
              <span class="badge badge-notif">{{ notifCount }}</span>
            }
          </a>
          <a routerLink="/client/profile" routerLinkActive="active" class="nav-link">
            👤 Mi perfil
          </a>
        </nav>

        <div class="user-box">
          <div class="user-name">{{ userName }}</div>
          <button type="button" class="btn-logout" (click)="logout()">Cerrar sesión</button>
        </div>
      </aside>

      <main class="content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [
    `
      .shell {
        display: grid;
        grid-template-columns: 250px 1fr;
        min-height: 100vh;
      }
      .sidebar {
        background: var(--color-nav, #1a2332);
        color: var(--color-text-on-nav, #fff);
        padding: 1rem 0.75rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        position: sticky;
        top: 0;
        height: 100vh;
      }
      .brand {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-decoration: none;
        color: inherit;
        padding: 0.25rem 0.5rem;
      }
      .brand-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: var(--color-primary, #ff8c00);
      }
      .brand-text {
        font-weight: 700;
        font-size: 1.1rem;
      }
      .nav {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
      }
      .nav-link {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.6rem 0.75rem;
        border-radius: 8px;
        color: inherit;
        text-decoration: none;
        font-size: 0.9rem;
        opacity: 0.85;
        position: relative;
      }
      .nav-link:hover {
        opacity: 1;
        background: var(--color-nav-hover, rgba(255, 255, 255, 0.08));
      }
      .nav-link.active {
        opacity: 1;
        background: var(--color-primary, #ff8c00);
        color: var(--color-text-on-primary, #fff);
      }
      .badge {
        margin-left: auto;
        min-width: 18px;
        height: 18px;
        border-radius: 9px;
        text-align: center;
        font-size: 0.7rem;
        line-height: 18px;
        padding: 0 5px;
        background: var(--color-error, #ef4444);
        color: #fff;
      }
      .user-box {
        margin-top: auto;
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        padding-top: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
      }
      .user-name {
        font-size: 0.85rem;
        opacity: 0.9;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .btn-logout {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: inherit;
        padding: 0.4rem 0.7rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.75rem;
        white-space: nowrap;
      }
      .btn-logout:hover {
        background: var(--color-error, #ef4444);
        border-color: transparent;
      }
      .content {
        padding: 2rem;
      }
      @media (max-width: 768px) {
        .shell {
          grid-template-columns: 1fr;
        }
        .sidebar {
          position: static;
          height: auto;
        }
        .nav {
          flex-direction: row;
          flex-wrap: wrap;
        }
        .user-box {
          margin-top: 0.5rem;
        }
      }
    `,
  ],
})
export class ClientShellComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  userName = 'Cliente';
  cartCount = 0;
  notifCount = 0;

  constructor() {
    this.updateAuthState();
  }

  private updateAuthState(): void {
    const token = localStorage.getItem('fs_token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
        this.userName = payload.full_name || payload.name || payload.email || 'Cliente';
      } catch {
        this.userName = 'Cliente';
      }
    }
  }

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/']);
  }
}