import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="admin-users">
      <h2>Usuarios</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card p-4">
          <h3 class="text-lg font-semibold mb-3">Crear usuario</h3>
          <div class="form-field mb-2">
            <label class="form-label">Nombre</label>
            <input type="text" class="form-input" placeholder="Nombre completo" />
          </div>
          <div class="form-field mb-2">
            <label class="form-label">Email</label>
            <input type="email" class="form-input" placeholder="usuario@ejemplo.com" />
          </div>
          <div class="form-field mb-2">
            <label class="form-label">Rol</label>
            <select class="form-select">
              <option>ADMIN</option>
              <option>MANAGER</option>
              <option>STAFF</option>
            </select>
          </div>
          <button class="btn btn-primary w-full mt-3">Crear</button>
        </div>

        <div class="card p-4">
          <h3 class="text-lg font-semibold mb-3">Lista de usuarios</h3>
          <p>Lista de usuarios...</p>
        </div>
      </div>
    </section>
  `,
  styles: []
})
export class AdminUsersComponent {}