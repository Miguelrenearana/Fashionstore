import { Component, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
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
  selector: 'app-notifications-page',
  standalone: true,
  imports: [DatePipe],
  template: `
    <div class="container page">
      <h1 class="page-title">Mis notificaciones</h1>
      <p class="page-subtitle">Todos los avisos para tu cuenta.</p>

      <div class="toolbar">
        <button
          type="button"
          class="btn btn-outline btn-sm"
          (click)="markAllRead()"
          [disabled]="items().length === 0"
        >
          Marcar todas leídas
        </button>
        <button type="button" class="btn btn-ghost btn-sm" (click)="load()">Actualizar</button>
      </div>

      @if (error()) {
        <div class="alert alert-error" role="alert">{{ error() }}</div>
      }

      @if (items().length === 0 && !loading()) {
        <p class="empty">No tienes notificaciones.</p>
      }

      <div class="notif-list">
        @for (n of items(); track n.id) {
          <article class="notif-card" [class.notif-unread]="!n.is_read">
            <div class="notif-card-head">
              <strong>{{ n.title }}</strong>
              <time class="notif-time">{{ n.created_at | date:'short' }}</time>
            </div>
            <p class="notif-body">{{ n.body }}</p>
            @if (!n.is_read) {
              <button type="button" class="btn btn-ghost btn-sm" (click)="markRead(n)">
                Marcar como leída
              </button>
            }
          </article>
        }
      </div>
    </div>
  `,
  styles: [
    `
    .page { max-width: 720px; }
    .page-title { font-size: var(--text-3xl); font-weight: 700; margin-bottom: 4px; }
    .page-subtitle { color: var(--color-text-muted); margin-bottom: var(--space-5); }
    .toolbar { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); }
    .empty { color: var(--color-text-muted); padding: var(--space-8) 0; text-align: center; }
    .notif-list { display: flex; flex-direction: column; gap: var(--space-3); }
    .notif-card {
      border: 1px solid var(--color-border); border-radius: var(--radius-lg);
      padding: var(--space-4); background: var(--color-surface);
    }
    .notif-unread { border-left: 4px solid var(--color-primary); background: var(--color-primary-light); }
    .notif-card-head {
      display: flex; align-items: center; justify-content: space-between; gap: var(--space-3);
    }
    .notif-time { font-size: 12px; color: var(--color-text-muted); white-space: nowrap; }
    .notif-body { margin: var(--space-2) 0 var(--space-3); color: var(--color-text); }
  `],
})
export class NotificationsPageComponent {
  items = signal<NotificationItem[]>([]);
  error = signal('');
  loading = signal(false);

  constructor(private auth: AuthService) {}

  ngOnInit(): void {
    this.load();
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.auth.token()) h['Authorization'] = `Bearer ${this.auth.token()}`;
    return h;
  }

  load(): void {
    if (this.loading()) return;
    this.loading.set(true);
    this.error.set('');
    fetch(`${environment.apiUrl}/notifications?limit=200`, { headers: this.headers() })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText)))
      .then((data: NotificationItem[]) => this.items.set(data))
      .catch(() => this.error.set('No se pudieron cargar las notificaciones.'))
      .finally(() => this.loading.set(false));
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
      })
      .catch(() => this.error.set('No se pudo marcar la notificación.'));
  }

  markAllRead(): void {
    for (const n of this.items().filter((x) => !x.is_read)) this.markRead(n);
  }
}