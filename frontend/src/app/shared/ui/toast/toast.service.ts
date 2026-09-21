import { Injectable, inject } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ToastService {
  private toasts: HTMLElement[] = [];

  show(message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info', duration: number = 3000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.role = 'alert';
    toast.innerHTML = `
      <div class="alert-icon"></div>
      <div class="alert-content">
        <div class="alert-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
        <div class="alert-message">${message}</div>
      </div>
      <button class="alert-dismiss" aria-label="Close">&times;</button>
    `;

    document.body.appendChild(toast);
    this.toasts.push(toast);

    setTimeout(() => {
      this.dismiss(toast);
    }, duration);
  }

  dismiss(toast: HTMLElement) {
    if (this.toasts.includes(toast)) {
      toast.style.transition = 'opacity 0.3s ease';
      toast.style.opacity = '0';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
        this.toasts = this.toasts.filter(t => t !== toast);
      }, 300);
    }
  }
}