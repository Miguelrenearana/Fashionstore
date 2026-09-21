import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ui-chip',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="chip {{ removable && 'chip-removable' }}">{{ label }}{{ removable ? ' ×' : '' }}</span>
  `,
  styles: [`
    .chip {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      padding: var(--space-1) var(--space-2);
      font-size: var(--text-xs);
      font-weight: 500;
      border-radius: var(--radius-full);
      background: var(--color-surface-alt);
      border: 1px solid var(--color-border);
      color: var(--color-text);
      transition: all var(--transition-fast);
    }
    .chip:hover {
      background: var(--color-border);
    }
    .chip-removable {
      cursor: default;
    }
    .chip-remove {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: none;
      border: none;
      color: inherit;
      opacity: 0.6;
      cursor: pointer;
      margin-left: var(--space-1);
      padding: 0;
    }
    .chip-remove:hover {
      opacity: 1;
      background: rgba(0, 0, 0, 0.1);
    }
  `]
})
export class UiChipComponent {
  label = input<string>('');
  removable = input(false);
}