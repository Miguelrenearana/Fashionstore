import { Component, input, output, forwardRef, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormsModule } from '@angular/forms';

export type InputType = 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';

@Component({
  selector: 'ui-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => UiInputComponent),
    multi: true
  }],
  template: `
    <div class="form-field">
      @if (label()) {
        <label class="form-label" [for]="id()">{{ label() }}</label>
      }
      <div class="input-wrapper">
        @if (prefixIcon()) {
          <span class="prefix-icon">{{ prefixIcon() }}</span>
        }
        <input
          [id]="id()"
          [type]="type()"
          [placeholder]="placeholder()"
          [disabled]="disabled()"
          [readonly]="readonly()"
          [class]="computedClasses()"
          [value]="value()"
          (input)="onInput($event)"
          (blur)="onBlur()"
          (focus)="onFocus()"
          [attr.aria-label]="ariaLabel()"
          [attr.aria-describedby]="describedBy()"
          [attr.aria-invalid]="error() ? 'true' : 'false'"
        />
        @if (suffixIcon()) {
          <span class="suffix-icon">{{ suffixIcon() }}</span>
        }
      </div>
      @if (hint() && !error()) {
        <span class="form-hint">{{ hint() }}</span>
      }
      @if (error()) {
        <span class="form-error">{{ error() }}</span>
      }
    </div>
  `,
  styles: [`
    .input-wrapper { position: relative; display: flex; align-items: center; }
    .prefix-icon, .suffix-icon { position: absolute; color: var(--color-text-muted); pointer-events: none; }
    .prefix-icon { left: var(--space-3); }
    .suffix-icon { right: var(--space-3); }
    input { width: 100%; padding: var(--space-2) var(--space-3); font-size: var(--text-base); }
    input:focus { outline: none; border-color: var(--color-border-focus); box-shadow: var(--shadow-focus); }
    input[readonly] { background: var(--color-surface-alt); }
    .form-field { display: flex; flex-direction: column; gap: var(--space-1); }
    .form-label { font-size: var(--text-sm); font-weight: 500; color: var(--color-text); }
    .form-hint { font-size: var(--text-xs); color: var(--color-text-muted); }
    .form-error { font-size: var(--text-xs); color: var(--color-error); }
  `]
})
export class UiInputComponent implements ControlValueAccessor {
  // Inputs
  label = input<string>('');
  placeholder = input<string>('');
  type = input<InputType>('text');
  prefixIcon = input<string>('');
  suffixIcon = input<string>('');
  disabled = input(false);
  readonly = input(false);
  error = input<string>('');
  hint = input<string>('');
  ariaLabel = input<string>('');
  id = input<string>(`ui-input-${Math.random().toString(36).slice(2)}`);
  describedBy = input<string>('');

  // Internal
  value = signal('');
  focused = signal(false);
  private onChange = (v: string) => {};
  private onTouched = () => {};

  computedClasses = computed(() => {
    const base = 'form-input';
    const err = this.error() ? 'error' : '';
    const focus = this.focused() ? 'focus' : '';
    return [base, err, focus].filter(Boolean).join(' ');
  });

  onInput(event: Event) {
    const val = (event.target as HTMLInputElement).value;
    this.value.set(val);
    this.onChange(val);
  }

  onBlur() { this.focused.set(false); this.onTouched(); }
  onFocus() { this.focused.set(true); }

  writeValue(val: string): void { this.value.set(val ?? ''); }
  registerOnChange(fn: (v: string) => void): void { this.onChange = fn; }
  registerOnTouched(fn: () => void): void { this.onTouched = fn; }
  setDisabledState(disabled: boolean): void { this.disabled.set(disabled); }
}