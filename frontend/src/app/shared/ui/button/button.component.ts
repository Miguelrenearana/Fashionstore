import { Component, input, output, HostBinding, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
export type ButtonSize = 'sm' | 'md' | 'lg' | 'icon';

@Component({
  selector: 'ui-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      [type]="type()"
      [disabled]="disabled() || loading()"
      [class]="computedClasses()"
      (click)="onClick($event)">
      @if (loading()) {
        <span class="spinner" aria-hidden="true"></span>
      } @else if (label() || icon()) {
        @if (icon()) { <span class="icon">{{ icon() }}</span> }
        @if (label()) { <span class="label">{{ label() }}</span> }
      } @else {
        <ng-content></ng-content>
      }
    </button>
  `,
  styles: [`
    :host { display: inline-flex; }
    button {
      display: inline-flex; align-items: center; justify-content: center;
      gap: var(--space-2); border: 1px solid transparent; border-radius: var(--radius-md);
      font-family: var(--font-sans); font-weight: 500; cursor: pointer;
      transition: all var(--transition-fast); text-decoration: none; white-space: nowrap;
    }
    button:disabled { opacity: 0.5; cursor: not-allowed; pointer-events: none; }
    .spinner { width: 16px; height: 16px; border: 2px solid currentColor; border-right-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .icon { font-size: 1.2em; line-height: 1; }
  `]
})
export class UiButtonComponent {
  // Inputs
  label = input<string>('');
  icon = input<string>('');
  variant = input<ButtonVariant>('primary');
  size = input<ButtonSize>('md');
  type = input<'button' | 'submit' | 'reset'>('button');
  disabled = input(false);
  loading = input(false);
  ariaLabel = input<string>('');

  // Output
  clicked = output<MouseEvent>();

  // Computed classes
  computedClasses = computed(() => {
    const base = 'btn';
    const v = `btn-${this.variant()}`;
    const s = this.size() !== 'md' ? `btn-${this.size()}` : '';
    const loading = this.loading() ? 'btn-loading' : '';
    return [base, v, s, loading].filter(Boolean).join(' ');
  });

  onClick(event: MouseEvent) {
    if (!this.disabled() && !this.loading()) {
      this.clicked.emit(event);
    }
  }
}