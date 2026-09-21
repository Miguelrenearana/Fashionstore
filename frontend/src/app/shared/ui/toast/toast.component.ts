import { Component, inject, OnInit } from '@angular/core';
import { ToastService } from './toast.service';

@Component({
  selector: 'ui-toast',
  standalone: true,
  providers: [ToastService],
  template: `
    <div class="toast-container">
      @for (toast of toasts(); track toast.id) {
        <div class="alert {{ toast.type }}" role="alert">
          <div class="alert-content">
            <div class="alert-title">{{ toast.type | titlecase }}</div>
            <div class="alert-message">{{ toast.message }}</div>
            <button class="alert-dismiss" (click)="dismiss(toast)" aria-label="Close">&times;</button>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .toast-container {
      pointer-events: none;
      position: fixed;
      bottom: var(--space-4);
      right: var(--space-4);
      display: flex;
      flex-direction: column;
      gap: var(--space-2);
      z-index: var(--z-toast);
    }
    .alert {
      pointer-events: auto;
      min-width: 250px;
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-md);
      padding: var(--space-3) var(--space-4);
      display: flex;
      align-items: flex-start;
      gap: var(--space-3);
      animation: slideIn var(--transition-fast);
      opacity: 0;
      transform: translateY(20px);
    }
    .alert.success { border-color: var(--color-success); }
    .alert.error { border-color: var(--color-error); }
    .alert.info { border-color: var(--color-info); }
    .alert.warning { border-color: var(--color-warning); }
    .alert-icon {
      flex-shrink: 0;
      margin-top: 2px;
      width: 16px;
      height: 16px;
    }
    .alert-content {
      flex: 1;
    }
    .alert-title {
      font-weight: 600;
      margin-bottom: var(--space-1);
    }
    .alert-message {
      font-size: var(--text-sm);
    }
    .alert-dismiss {
      flex-shrink: 0;
      background: none;
      border: none;
      color: inherit;
      opacity: 0.6;
      cursor: pointer;
      padding: var(--space-1);
    }
    .alert-dismiss:hover {
      opacity: 1;
    }
    @keyframes slideIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class UiToastComponent implements OnInit {
  private service = inject(ToastService);
  toasts = this.service.toasts;

  ngOnInit() {
    // Escuchar toasts añadidos globalmente (simple polling / event)
    // En la práctica se suscribe al service observable en producción
  }

  dismiss(toast: any) {
    this.service.dismiss(toast as HTMLElement);
  }
}