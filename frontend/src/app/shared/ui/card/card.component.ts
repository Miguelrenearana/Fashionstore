import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ui-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card">
      <ng-content></ng-content>
    </div>
  `,
  styles: [`
    .card {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
      transition: box-shadow var(--transition-base), transform var(--transition-base);
    }
    .card:hover {
      box-shadow: var(--shadow-md);
    }
    .card-interactive {
      cursor: pointer;
    }
    .card-interactive:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }
    .card-header {
      padding: var(--space-4);
      border-bottom: 1px solid var(--color-border);
    }
    .card-body {
      padding: var(--space-4);
    }
    .card-footer {
      padding: var(--space-4);
      border-top: 1px solid var(--color-border);
      background: var(--color-surface-alt);
      border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    }
  `]
})
export class UiCardComponent {
}