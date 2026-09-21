import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ui-table',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th *ngFor="let column of columns()">{{ column.header }}</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let item of items(); trackBy: trackByItem">
            <td *ngFor="let column of columns()">
              <ng-content [selector]="column.cellSelector || '.cell'">{{ item[column.property] }}</ng-content>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
  styles: [`
    .table-wrapper {
      overflow-x: auto;
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
    }
    .table {
      width: 100%;
      border-collapse: collapse;
      font-size: var(--text-sm);
    }
    .table th,
    .table td {
      padding: var(--space-3) var(--space-4);
      text-align: left;
      border-bottom: 1px solid var(--color-border);
    }
    .table th {
      background: var(--color-surface-alt);
      font-weight: 600;
      color: var(--color-text-secondary);
      white-space: nowrap;
    }
    .table tbody tr {
      transition: background var(--transition-fast);
    }
    .table tbody tr:hover {
      background: var(--color-surface-alt);
    }
    .table tbody tr:last-child td {
      border-bottom: none;
    }
    @media (max-width: 640px) {
      .table-responsive thead { display: none; }
      .table-responsive tbody,
      .table-responsive tr,
      .table-responsive td { display: block; width: 100%; }
      .table-responsive tr { padding: var(--space-4); border-bottom: 1px solid var(--color-border); }
      .table-responsive td { display: flex; justify-content: space-between; padding: var(--space-1) 0; border: none; }
      .table-responsive td::before { content: attr(data-label); font-weight: 500; color: var(--color-text-secondary); }
    }
  `]
})
export class UiTableComponent {
  columns = input<Array<{header: string, property: string, cellSelector?: string}>>([]);
  items = input<Array<any>>([]);
  trackByItem = (_: number, item: any) => item?.id || item?._id || item?.$index || 0;
}