import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';

@Component({
  selector: 'app-admin-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <div class="shell">
      <aside class="sidebar">
        <h2 class="title">Administración</h2>
        <nav class="nav" aria-label="Navegación de administración">
          <a routerLink="users" routerLinkActive="active" class="nav-link">Usuarios y roles</a>
          <a routerLink="catalog" routerLinkActive="active" class="nav-link">Catálogo (tallas, colores…)</a>
          <a routerLink="products" routerLinkActive="active" class="nav-link">Productos</a>
          <a routerLink="inventory" routerLinkActive="active" class="nav-link">Inventario</a>
          <a routerLink="reports" routerLinkActive="active" class="nav-link">Reportes</a>
          <a routerLink="reports/ai" routerLinkActive="active" class="nav-link">Reportes IA</a>
        </nav>
        <p class="role">{{ auth.roles().join(', ') || 'Sin rol' }}</p>
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
        grid-template-columns: 240px 1fr;
        min-height: calc(100vh - 64px);
      }
      .sidebar {
        background: var(--color-nav, #1a2b3a);
        color: var(--color-text-on-nav, #fff);
        padding: 1.25rem 0.75rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
      }
      .title {
        margin: 0 0.75rem;
        font-size: 1.1rem;
      }
      .nav {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }
      .nav-link {
        display: block;
        padding: 0.6rem 0.75rem;
        border-radius: 8px;
        color: inherit;
        text-decoration: none;
        font-size: 0.9rem;
        opacity: 0.85;
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
      .role {
        margin: auto 0.75rem 0;
        font-size: 0.75rem;
        opacity: 0.7;
      }
      .content {
        padding: 2rem;
      }
      @media (max-width: 768px) {
        .shell {
          grid-template-columns: 1fr;
        }
        .sidebar {
          position: sticky;
          top: 64px;
        }
        .nav {
          flex-direction: row;
          flex-wrap: wrap;
        }
      }
    `,
  ],
})
export class AdminShellComponent {
  constructor(public auth: AuthService) {}
}