import { Component, signal, HostListener } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';
import { environment } from '@core/environments/environment';

interface NotificationItem {
  id: number;
  type: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [RouterLink, DatePipe],
  template: `
    <div class="notif-wrap">
      <button
        type="button"
        class="notif-bell"
        (click)="toggle()"
        [attr.aria-expanded]="open()"
        aria-label="Notificaciones"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        @if (unread() > 0) {
          <span class="notif-badge">{{ unread() > 9 ? '9+' : unread() }}</span>
        }
      </button>

      @if (open()) {
        <div class="notif-panel" role="dialog" aria-label="Notificaciones">
          <div class="notif-header">
            <strong>Notificaciones</strong>
            <button type="button" class="btn btn-ghost btn-sm" (click)="markAllRead()">Marcar todas leídas</button>
          </div>
          <div class="notif-list">
            @for (n of items(); track n.id) {
              <button
                type="button"
                class="notif-item"
                [class.notif-unread]="!n.is_read"
                (click)="markRead(n)"
              >
                <span class="notif-title">{{ n.title }}</span>
                <span class="notif-body">{{ n.body }}</span>
                <time class="notif-time">{{ n.created_at | date:'short' }}</time>
              </button>
            } @empty {
              <p class="notif-empty">No tienes notificaciones.</p>
            }
          </div>
          <a routerLink="/notifications" class="notif-footer" (click)="open.set(false)">Ver todas</a>
        </div>
      }
    </div>
  `,
  styles: [
    `
    .notif-wrap { position: relative; display: flex; }
    .notif-bell {
      display: flex; align-items: center; justify-content: center;
      width: 40px; height: 40px; background: none; border: none;
      color: var(--color-text-on-nav); border-radius: var(--radius-md);
      cursor: pointer; transition: background var(--transition-fast); position: relative;
    }
    .notif-bell:hover { background: var(--color-nav-hover); }
    .notif-badge {
      position: absolute; top: 2px; right: 2px; min-width: 16px; height: 16px;
      display: flex; align-items: center; justify-content: center;
      background: #dc2626; color: #fff; font-size: 10px; font-weight: 700;
      border-radius: 999px; padding: 0 4px;
    }
    .notif-panel {
      position: absolute; top: 44px; right: 0; width: 320px; max-width: 90vw;
      background: var(--color-surface); border: 1px solid var(--color-border);
      border-radius: var(--radius-lg); box-shadow: var(--shadow-lg);
      z-index: var(--z-modal); overflow: hidden;
    }
    .notif-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: var(--space-3); border-bottom: 1px solid var(--color-border);
    }
    .notif-list { max-height: 320px; overflow-y: auto; }
    .notif-item {
      display: flex; flex-direction: column; gap: 2px; width: 100%;
      padding: var(--space-3); text-align: left; background: none; border: none;
      border-bottom: 1px solid var(--color-border); cursor: pointer;
      transition: background var(--transition-fast);
    }
    .notif-item:hover { background: var(--color-surface-alt); }
    .notif-unread { background: var(--color-primary-light); }
    .notif-title { font-weight: 600; font-size: var(--text-sm); color: var(--color-text); }
    .notif-body { font-size: var(--text-xs); color: var(--color-text-muted); }
    .notif-time { font-size: 11px; color: var(--color-text-muted); opacity: 0.8; }
    .notif-empty { padding: var(--space-4); text-align: center; color: var(--color-text-muted); }
    .notif-footer {
      display: block; padding: var(--space-3); text-align: center;
      font-size: var(--text-sm); font-weight: 600; border-top: 1px solid var(--color-border);
      color: var(--color-primary); text-decoration: none;
    }
    .notif-footer:hover { color: var(--color-primary-dark); }
  `],
})
export class NotificationsComponent {
  open = signal(false);
  items = signal<NotificationItem[]>([]);
  unread = signal(0);
  loading = false;

  constructor(private auth: AuthService) {}

  @HostListener('document:click', ['$event'])
  onDocClick(event: Event): void {
    if (this.open() && !(event.target as HTMLElement).closest('.notif-wrap')) {
      this.open.set(false);
    }
  }

  toggle(): void {
    this.open.update((v) => !v);
    if (this.open()) this.load();
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.auth.token()) h['Authorization'] = `Bearer ${this.auth.token()}`;
    return h;
  }

  load(): void {
    if (this.loading) return;
    this.loading = true;
    fetch(`${environment.apiUrl}/notifications?limit=10`, { headers: this.headers() })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: NotificationItem[]) => {
        this.items.set(data);
        this.unread.set(data.filter((n) => !n.is_read).length);
      })
      .catch(() => this.items.set([]))
      .finally(() => (this.loading = false));
  }

  markRead(n: NotificationItem): void {
    if (n.is_read) return;
    fetch(`${environment.apiUrl}/notifications/${n.id}/read`, {
      method: 'PATCH',
      headers: this.headers(),
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then(() => {
        this.items.update((list) =>
          list.map((x) => (x.id === n.id ? { ...x, is_read: true } : x))
        );
        this.unread.update((u) => Math.max(0, u - 1));
      })
      .catch(() => undefined);
  }

  markAllRead(): void {
    const pending = this.items().filter((n) => !n.is_read);
    for (const n of pending) this.markRead(n);
  }
}