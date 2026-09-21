import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ui-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="modal-overlay" (click)="onOverlayClick($event)">
      <div class="modal" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <ng-content select>[modal-header]</ng-content>
          <button class="modal-close" (click)="onClose()">
            <span aria-hidden="true">×</span>
          </button>
        </div>
        <div class="modal-body">
          <ng-content select>[modal-body]</ng-content>
        </div>
        <div class="modal-footer">
          <ng-content select>[modal-footer]</ng-content>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: var(--space-4);
      z-index: var(--z-modal);
      animation: fadeIn var(--transition-fast);
    }
    .modal {
      background: var(--color-surface);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-lg);
      max-width: 500px;
      width: 100%;
      max-height: 90vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      animation: slideUp var(--transition-base);
    }
    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: var(--space-4);
      border-bottom: 1px solid var(--color-border);
    }
    .modal-title {
      font-size: var(--text-lg);
      font-weight: 600;
    }
    .modal-close {
      background: none;
      border: none;
      color: var(--color-text-muted);
      cursor: pointer;
      padding: var(--space-1);
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .modal-close:hover {
      background: var(--color-surface-alt);
      color: var(--color-text);
    }
    .modal-body {
      padding: var(--space-4);
      overflow-y: auto;
    }
    .modal-footer {
      display: flex;
      justify-content: flex-end;
      gap: var(--space-3);
      padding: var(--space-4);
      border-top: 1px solid var(--color-border);
      background: var(--color-surface-alt);
    }
  `]
})
export class UiModalComponent {
  onClose() { /* emitir salida si es necesario */ }
  onOverlayClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      this.onClose();
    }
  }
}