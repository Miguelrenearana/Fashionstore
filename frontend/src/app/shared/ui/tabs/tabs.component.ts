import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ui-tabs',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="tabs">
      @for (tab of tabs(); track tab.id) {
        <button class="tab" (click)="selectTab(tab.id)">{{ tab.label }}</button>
      }
    </div>
    <div class="tab-panel">
      <ng-content></ng-content>
    </div>
  `,
  styles: [`
    .tabs {
      display: flex;
      border-bottom: 1px solid var(--color-border);
      gap: var(--space-1);
    }
    .tab {
      padding: var(--space-3) var(--space-4);
      font-size: var(--text-sm);
      font-weight: 500;
      color: var(--color-text-secondary);
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      cursor: pointer;
      transition: all var(--transition-fast);
      position: relative;
      bottom: -1px;
    }
    .tab:hover {
      color: var(--color-text);
    }
    .tab.active {
      color: var(--color-primary);
      border-bottom-color: var(--color-primary);
    }
    .tab-panel {
      padding: var(--space-4) 0;
    }
  `]
})
export class UiTabsComponent {
  tabs = input<Array<{label: string, id: string}>>([]);
  selected = output<string>();

  selectTab(id: string) {
    this.selected.emit(id);
  }
}