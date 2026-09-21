import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ui-skeleton',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="skeleton" [ngClass]="shapeClass">
      @if (showText) {
        <span class="skeleton-text"></span>
      } @else {
        <span class="skeleton-avatar" *ngIf="showAvatar"></span>
        <div class="skeleton-card" *ngIf="showCard"></div>
      }
    </div>
  `,
  styles: [`
    .skeleton {
      background: linear-gradient(
        90deg,
        var(--color-surface-alt) 25%,
        var(--color-border) 50%,
        var(--color-surface-alt) 75%
      );
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      border-radius: var(--radius-md);
    }
    @keyframes shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }
    .skeleton-text {
      height: 1rem;
      border-radius: var(--radius-sm);
    }
    .skeleton-title {
      height: 1.5rem;
      width: 60%;
      border-radius: var(--radius-sm);
    }
    .skeleton-avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
    }
    .skeleton-card {
      height: 200px;
      border-radius: var(--radius-lg);
    }
  `]
})
export class UiSkeletonComponent {
  shape = input<'text' | 'avatar' | 'card'>('text');
  showText = computed(() => this.shape() === 'text');
  showAvatar = computed(() => this.shape() === 'avatar');
  showCard = computed(() => this.shape() === 'card');
}