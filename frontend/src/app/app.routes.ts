import { Routes } from '@angular/router';
import { AuthGuard, NegAuthGuard, RoleGuard } from '@core/guards/auth.guard';
import { LandingComponent } from './features/landing/landing.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', component: LandingComponent },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.routes').then((m) => m.AUTH_ROUTES),
    canActivate: [NegAuthGuard],
  },
  {
    path: 'admin',
    loadChildren: () => import('./features/admin/admin.routes').then((m) => m.ADMIN_ROUTES),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ADMIN', 'MANAGER'] },
  },
  {
    path: 'staff',
    loadChildren: () => import('./features/staff/staff.routes').then((m) => m.STAFF_ROUTES),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ADMIN', 'MANAGER', 'BRANCH_MANAGER', 'CASHIER'] },
  },
  {
    path: 'pos',
    loadChildren: () => import('./features/pos/pos.routes').then((m) => m.POS_ROUTES),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ADMIN', 'MANAGER', 'BRANCH_MANAGER', 'CASHIER'] },
  },
  { path: '**', redirectTo: '' },
];