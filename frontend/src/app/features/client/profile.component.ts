import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ClientService } from './client.service';

@Component({
  selector: 'app-client-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page">
      <h1 class="page-title">Mi perfil</h1>
      <p class="page-subtitle">Consulta y actualiza tu información personal.</p>

      @if (error) {
        <div class="alert alert-error">{{ error }}</div>
      }
      @if (success) {
        <div class="alert alert-success">{{ success }}</div>
      }

      <div class="card form">
        <div class="field">
          <label class="field-label">Nombre completo</label>
          <input type="text" class="input" [(ngModel)]="fullName" placeholder="Nombre y apellido" />
        </div>

        <div class="field">
          <label class="field-label">Email</label>
          <input type="email" class="input" [value]="email" disabled />
          <p class="hint">El email no puede modificarse.</p>
        </div>

        <div class="field">
          <label class="field-label">Teléfono</label>
          <input type="tel" class="input" [(ngModel)]="phone" placeholder="+591 70000000" />
        </div>

        <div class="field">
          <label class="field-label">Fecha de nacimiento</label>
          <input type="date" class="input" [(ngModel)]="birthDate" />
        </div>

        <div class="field" *ngIf="points !== null">
          <label class="field-label">Puntos del programa</label>
          <p class="points">⭐ {{ points }} puntos</p>
        </div>

        <button type="button" class="btn btn-primary" (click)="save()" [disabled]="saving">
          {{ saving ? 'Guardando...' : 'Guardar cambios' }}
        </button>
      </div>
    </div>
  `,
  styles: [
    `
      .page-title { margin-bottom: 4px; }
      .page-subtitle { color: var(--color-text-muted); margin-bottom: 1.25rem; }
      .form { max-width: 520px; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
      .field { display: flex; flex-direction: column; gap: 0.3rem; }
      .field-label { font-size: 0.82rem; color: var(--color-text-muted); }
      .hint { font-size: 0.78rem; color: var(--color-text-muted); }
      .points { font-weight: 600; color: var(--color-primary, #ff8c00); margin: 0; }
    `,
  ],
})
export class ProfileComponent implements OnInit {
  private api = inject(ClientService);

  fullName = '';
  email = '';
  phone = '';
  birthDate = '';
  points: number | null = null;

  saving = false;
  error = '';
  success = '';

  ngOnInit(): void {
    this.api.getMe().subscribe({
      next: (me: any) => {
        const u = me.user ?? me;
        this.fullName = u.full_name ?? u.name ?? (u.first_name ? `${u.first_name} ${u.last_name ?? ''}`.trim() : '');
        this.email = u.email ?? '';
        this.phone = u.phone ?? '';
        this.birthDate = u.birth_date ?? '';
        this.points = u.points ?? null;
      },
      error: () => {},
    });
    this.api.getClientProfile().subscribe({
      next: (p: any) => {
        const profile = p.user ?? p.profile ?? p;
        this.fullName = profile.full_name ?? profile.name ?? this.fullName;
        this.phone = profile.phone ?? this.phone;
        this.birthDate = profile.birth_date ?? this.birthDate;
        this.points = profile.points ?? this.points;
      },
      error: () => {},
    });
  }

  save(): void {
    if (!this.fullName.trim()) { this.error = 'El nombre completo es obligatorio.'; return; }
    this.saving = true;
    this.error = '';
    this.success = '';
    this.api.updateClientProfile({
      full_name: this.fullName,
      phone: this.phone || undefined,
      birth_date: this.birthDate || undefined,
    }).subscribe({
      next: () => {
        this.success = 'Perfil actualizado correctamente.';
        this.saving = false;
      },
      error: () => { this.error = 'No se pudo actualizar el perfil.'; this.saving = false; },
    });
  }
}