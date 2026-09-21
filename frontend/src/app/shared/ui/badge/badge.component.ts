import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ui-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="badge {{ variantClass }}">{{ label }}</span>
  `,
  styles: [`
    .badge {
      display: inline-flex;
      align-items: center;
      padding: var(--space-1) var(--space-2);
      font-size: var(--text-xs);
      font-weight: 600;
      border-radius: var(--radius-full);
      white-space: nowrap;
    }
    .badge-primary {
      background: var(--color-primary-light);
      color: var(--color-primary-dark);
    }
    .badge-success {
      background: var(--color-success-light);
      color: var(--color-success);
    }
    .badge-warning {
      background: var(--color-warning-light);
      color: var(--color-warning);
    }
    .badge-error {
      background: var(--color-error-light);
      color: var(--color-error);
    }
    .badge-info {
      background: var(--color-info-light);
      color: var(--color-info);
    }
    .badge-neutral {
      background: var(--color-surface-alt);
      color: var(--color-text-secondary);
      border: 1px solid var(--color-border);
    }
    .badge-dot {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
    }
    .badge-dot::before {
      content: "";
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: currentColor;
    }
  `]
})
export class UiBadgeComponent {
  label = input<string>('');
  variant = input<'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral'>('neutral');

  get variantClass(): string {
    return `badge-${this.variant()}`;
  }
}