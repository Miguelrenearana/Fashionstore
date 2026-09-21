import { Routes } from '@angular/router';
import { StaffShellComponent } from './staff-shell.component';
import { StaffReservationsComponent } from './staff-reservations.component';

export const STAFF_ROUTES: Routes = [
  {
    path: '',
    component: StaffShellComponent,
    children: [
      { path: '', redirectTo: 'reservations', pathMatch: 'full' },
      { path: 'reservations', component: StaffReservationsComponent },
    ],
  },
];