import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ui-avatar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="avatar {{ initials ? '' : 'avatar-with-image' }} {{ size }}">
      @if (imageUrl) {
        <img [src]="imageUrl" [alt]="label()"/>
      } @else {
        {{ label() }}
      }
    </span>
  `,
  styles: [`
    .avatar {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--color-primary-light);
      color: var(--color-primary-dark);
      font-weight: 600;
      font-size: var(--text-sm);
      overflow: hidden;
    }
    .avatar-sm { width: 32px; height: 32px; font-size: var(--text-xs); }
    .avatar-lg { width: 56px; height: 56px; font-size: var(--text-base); }
    .avatar-xl { width: 80px; height: 80px; font-size: var(--text-xl); }
    .avatar img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  `]
})
export class UiAvatarComponent {
  label = input<string>('');
  imageUrl = input<string>('');
  initials = input<string>('');
  size = input<'sm' | 'lg' | 'xl'>('md');
}