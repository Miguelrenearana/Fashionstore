import { Component, inject, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ClientService, NotificationItem } from './client.service';

@Component({
  selector: 'app-client-notifications',
  standalone: true,
  imports: [DatePipe],
  template: `
    <div class="page">
      <h1 class="page-title">Notificaciones</h1>
      <p class="page-subtitle">Avisos sobre tus reservas, compras y novedades.</p>

      <div class="toolbar">
        <button type="button" class="btn btn-outline btn-sm" (click)="markAllRead()" [disabled]="items.length === 0">
          Marcar todas leídas
        </button>
        <button type="button" class="btn btn-ghost btn-sm" (click)="load()">Actualizar</button>
      </div>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }

      @if (loading) {
        <div class="loading">Cargando notificaciones...</div>
      } @else if (items.length === 0) {
        <div class="empty card">
          <p>No tienes notificaciones.</p>
        </div>
      } @else {
        <div class="list">
          @for (n of items; track n.id) {
            <article class="notif" [class.unread]="!isRead(n)" (click)="markRead(n)">
              <div class="icon" [class]="'ic-' + ((n.type || 'default')).toLowerCase()">
                {{ iconFor(n.type) }}
              </div>
              <div class="body">
                <strong>{{ n.title }}</strong>
                <p class="text">{{ n.body }}</p>
                <time class="time">{{ n.created_at | date:'dd/MM/yyyy HH:mm' }}</time>
              </div>
              @if (!isRead(n)) {
                <span class="dot"></span>
              }
            </article>
          }
        </div>
      }
    </div>
  `,
  styles: [
    `
      .page-title { margin-bottom: 4px; }
      .page-subtitle { color: var(--color-text-muted); margin-bottom: 1.25rem; }
      .toolbar { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
      .list { display: flex; flex-direction: column; gap: 0.85rem; }
      .notif { display: flex; gap: 0.85rem; align-items: flex-start; background: var(--color-surface, #fff); border: 1px solid var(--color-border); border-radius: 12px; padding: 1rem; cursor: pointer; }
      .notif.unread { border-left: 4px solid var(--color-primary, #ff8c00); background: var(--color-primary-light, #fff7ed); }
      .icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; background: var(--color-surface-variant, #f3f4f6); flex-shrink: 0; }
      .body { flex: 1; }
      .text { margin: 4px 0; font-size: 0.9rem; }
      .time { font-size: 0.78rem; color: var(--color-text-muted); }
      .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--color-primary, #ff8c00); margin-top: 0.5rem; flex-shrink: 0; }
      .loading { text-align: center; color: var(--color-text-muted); padding: 4rem 0; }
      .empty { text-align: center; padding: 3rem 1rem; }
    `,
  ],
})
export class NotificationsComponent implements OnInit {
  private api = inject(ClientService);

  items: NotificationItem[] = [];
  loading = false;
  error = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.api.getNotifications(200).subscribe({
      next: (data) => {
        this.items = Array.isArray(data) ? data : ((data as any)?.items ?? []);
        this.loading = false;
      },
      error: () => { this.error = 'No se pudieron cargar las notificaciones.'; this.loading = false; },
    });
  }

  isRead(n: NotificationItem): boolean {
    return !!(n.is_read ?? n.read);
  }

  markRead(n: NotificationItem): void {
    if (this.isRead(n)) return;
    this.api.markNotificationRead(n.id).subscribe({
      next: () => { n.is_read = true; n.read = true; },
      error: () => {},
    });
  }

  markAllRead(): void {
    for (const n of this.items.filter((x) => !this.isRead(x))) this.markRead(n);
  }

  iconFor(type: string): string {
    const map: Record<string, string> = {
      RESERVATION: '📦', STOCK: '📊', PROMOTION: '🏷️', SALE: '🧾',
      password_reset: '🔒', default: '🔔',
    };
    return map[(type ?? 'default').toUpperCase()] ?? map['default'];
  }
}