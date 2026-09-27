import { Routes } from '@angular/router';
import { StaffShellComponent } from './staff-shell.component';
import { StaffReservationsComponent } from './staff-reservations.component';
import { AdminInventoryComponent } from '../admin/admin-inventory.component';
import { AdminReceptionComponent } from '../admin/admin-reception.component';

export const STAFF_ROUTES: Routes = [
  {
    path: '',
    component: StaffShellComponent,
    children: [
      { path: '', redirectTo: 'reservations', pathMatch: 'full' },
      { path: 'reservations', component: StaffReservationsComponent },
      { path: 'inventory', component: AdminInventoryComponent },
      { path: 'reception', component: AdminReceptionComponent },
      { path: 'pos', loadComponent: () => import('../pos/pos.component').then((m) => m.PosComponent) },
    ],
  },
];