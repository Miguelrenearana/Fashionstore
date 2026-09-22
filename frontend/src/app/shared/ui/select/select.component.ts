import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ui-select',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="form-select">
      <select>
        <option *ngFor="let option of options(); track option.value" [value]="option.value">{{ option.label }}</option>
      </select>
    </div>
  `,
  styles: [`
    .form-select {
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right var(--space-3) center;
      padding-right: var(--space-10);
    }
  `]
})
export class UiSelectComponent {
  options = input<Array<{label: string, value: string}>>([]);
}