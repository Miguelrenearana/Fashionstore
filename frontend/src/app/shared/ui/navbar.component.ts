import { Component, signal, HostListener } from '@angular/core';
import { RouterLink, RouterLinkActive, Router } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <a class="skip-link" href="#main-content">Saltar al contenido principal</a>

    <header class="navbar" role="banner">
      <div class="navbar-container container flex items-center justify-between">
        <a class="brand" routerLink="/catalog" aria-label="FashionStore - Inicio">
          <span class="brand-icon" aria-hidden="true">🛍️</span>
          <span class="brand-text">FashionStore</span>
        </a>

        <nav class="navbar-nav desktop-nav" aria-label="Navegación principal">
          <a routerLink="/catalog" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}" class="nav-link">Catálogo</a>
          <a routerLink="/cart" routerLinkActive="active" class="nav-link">Carrito</a>
          <a routerLink="/reservations" routerLinkActive="active" class="nav-link">Reservas</a>
        </nav>

        <div class="navbar-actions desktop-actions flex items-center gap-2">
          @if (!auth.isAuthenticated()) {
            <a routerLink="/auth" routerLinkActive="active" class="btn btn-ghost nav-link">Iniciar sesión</a>
          } @else {
            <a routerLink="/profile" routerLinkActive="active" class="btn btn-ghost nav-link">Perfil</a>
            <a routerLink="/branch" routerLinkActive="active" class="btn btn-ghost nav-link">Sucursales</a>
            <a routerLink="/admin" routerLinkActive="active" class="btn btn-ghost nav-link">Admin</a>
            <button (click)="logout()" class="btn btn-outline btn-sm" style="--color-primary: var(--color-text-on-nav); --color-border-focus: var(--color-text-on-nav); border-color: currentColor; color: var(--color-text-on-nav);">Salir</button>
          }
        </div>

        <button
          class="mobile-menu-btn"
          (click)="toggleMobileMenu()"
          [attr.aria-expanded]="mobileMenuOpen()"
          [attr.aria-controls]="mobileMenuOpen() ? 'mobile-nav' : null"
          aria-label="Abrir menú"
          type="button"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            @if (!mobileMenuOpen()) {
              <path d="M3 12h18M3 6h18M3 18h18" />
            } @else {
              <path d="M6 18L18 6M6 6l12 12" />
            }
          </svg>
        </button>
      </div>

      @if (mobileMenuOpen()) {
        <div class="mobile-nav-overlay" (click)="closeMobileMenu()" aria-hidden="true"></div>
        <nav id="mobile-nav" class="mobile-nav" role="navigation" aria-label="Menú móvil">
          <div class="mobile-nav-header">
            @if (auth.isAuthenticated()) {
              <div class="mobile-user">
                <div class="avatar avatar-lg" style="background: var(--color-primary-light); color: var(--color-primary-dark);">
                  {{ getInitials() }}
                </div>
                <div class="mobile-user-info">
                  <p class="font-medium">Usuario</p>
                  <p class="text-xs text-muted">Sesión activa</p>
                </div>
              </div>
            }
          </div>
          <ul class="mobile-nav-list">
            <li><a routerLink="/catalog" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}" class="mobile-nav-link" (click)="closeMobileMenu()">Catálogo</a></li>
            @if (auth.isAuthenticated()) {
              <li><a routerLink="/cart" routerLinkActive="active" class="mobile-nav-link" (click)="closeMobileMenu()">Carrito</a></li>
              <li><a routerLink="/reservations" routerLinkActive="active" class="mobile-nav-link" (click)="closeMobileMenu()">Reservas</a></li>
              <li><a routerLink="/profile" routerLinkActive="active" class="mobile-nav-link" (click)="closeMobileMenu()">Perfil</a></li>
              <li><a routerLink="/branch" routerLinkActive="active" class="mobile-nav-link" (click)="closeMobileMenu()">Sucursales</a></li>
              <li><a routerLink="/admin" routerLinkActive="active" class="mobile-nav-link" (click)="closeMobileMenu()">Admin</a></li>
            }
          </ul>
          <div class="mobile-nav-footer">
            @if (!auth.isAuthenticated()) {
              <a routerLink="/auth" class="btn btn-primary btn-block" (click)="closeMobileMenu()">Iniciar sesión</a>
            } @else {
              <button (click)="logout()" class="btn btn-danger btn-block">Cerrar sesión</button>
            }
          </div>
        </nav>
      }
    </header>
  `,
  styles: [`
    .navbar {
      position: sticky;
      top: 0;
      z-index: var(--z-sticky);
      background: var(--color-nav);
      border-bottom: 1px solid var(--color-border);
      box-shadow: var(--shadow-sm);
    }

    .navbar-container {
      height: 64px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      color: var(--color-text-on-nav);
      text-decoration: none;
      font-weight: 700;
      font-size: var(--text-xl);
      transition: opacity var(--transition-fast);
    }

    .brand:hover {
      opacity: 0.8;
      text-decoration: none;
    }

    .brand-icon {
      font-size: var(--text-2xl);
    }

    .brand-text {
      display: none;
    }

    @media (min-width: 480px) {
      .brand-text {
        display: inline;
      }
    }

    .navbar-nav {
      display: none;
      gap: var(--space-1);
    }

    @media (min-width: 768px) {
      .navbar-nav {
        display: flex;
      }
    }

    .nav-link {
      display: flex;
      align-items: center;
      height: 40px;
      padding: 0 var(--space-3);
      color: var(--color-text-on-nav);
      text-decoration: none;
      font-size: var(--text-sm);
      font-weight: 500;
      border-radius: var(--radius-md);
      opacity: 0.85;
      transition: all var(--transition-fast);
    }

    .nav-link:hover {
      opacity: 1;
      background: var(--color-nav-hover);
      text-decoration: none;
    }

    .nav-link.active {
      opacity: 1;
      background: var(--color-primary);
      color: var(--color-text-on-primary);
    }

    .navbar-actions {
      display: none;
      align-items: center;
      gap: var(--space-2);
    }

    @media (min-width: 768px) {
      .navbar-actions {
        display: flex;
      }
    }

    .mobile-menu-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      background: none;
      border: none;
      color: var(--color-text-on-nav);
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: background var(--transition-fast);
    }

    .mobile-menu-btn:hover {
      background: var(--color-nav-hover);
    }

    @media (min-width: 768px) {
      .mobile-menu-btn {
        display: none;
      }
    }

    /* Mobile Menu */
    .mobile-nav-overlay {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.5);
      z-index: var(--z-dropdown);
      animation: fadeIn var(--transition-fast);
    }

    .mobile-nav {
      position: fixed;
      top: 0;
      right: 0;
      bottom: 0;
      width: 300px;
      max-width: 100%;
      background: var(--color-surface);
      z-index: var(--z-modal);
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-lg);
      animation: slideInRight var(--transition-base);
      overflow-y: auto;
    }

    @keyframes slideInRight {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    .mobile-nav-header {
      padding: var(--space-4);
      border-bottom: 1px solid var(--color-border);
    }

    .mobile-user {
      display: flex;
      align-items: center;
      gap: var(--space-3);
    }

    .mobile-user-info p {
      margin: 0;
      line-height: 1.3;
    }

    .mobile-nav-list {
      flex: 1;
      padding: var(--space-3);
      display: flex;
      flex-direction: column;
      gap: var(--space-1);
    }

    .mobile-nav-link {
      display: flex;
      align-items: center;
      height: 48px;
      padding: 0 var(--space-3);
      color: var(--color-text);
      text-decoration: none;
      font-size: var(--text-base);
      font-weight: 500;
      border-radius: var(--radius-md);
      transition: background var(--transition-fast);
    }

    .mobile-nav-link:hover,
    .mobile-nav-link.active {
      background: var(--color-primary-light);
      color: var(--color-primary-dark);
      text-decoration: none;
    }

    .mobile-nav-footer {
      padding: var(--space-4);
      border-top: 1px solid var(--color-border);
      background: var(--color-surface-alt);
    }
  `],
})
export class NavbarComponent {
  mobileMenuOpen = signal(false);

  constructor(public auth: AuthService, private router: Router) {}

  @HostListener('document:keydown.escape')
  onEscape() {
    if (this.mobileMenuOpen()) {
      this.closeMobileMenu();
    }
  }

  toggleMobileMenu() {
    this.mobileMenuOpen.update(v => !v);
    if (this.mobileMenuOpen()) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }

  closeMobileMenu() {
    this.mobileMenuOpen.set(false);
    document.body.style.overflow = '';
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/catalog']);
    this.closeMobileMenu();
  }

  getInitials(): string {
    return 'U';
  }
}