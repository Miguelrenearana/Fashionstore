import { Routes } from '@angular/router';
import { AuthGuard, NegAuthGuard } from '@core/guards/auth.guard';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'catalog' },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.routes').then((m) => m.AUTH_ROUTES),
    canActivate: [NegAuthGuard],
  },
  {
    path: 'catalog',
    loadChildren: () =>
      import('./features/catalog/catalog.routes').then((m) => m.CATALOG_ROUTES),
  },
  {
    path: 'cart',
    loadChildren: () => import('./features/cart/cart.routes').then((m) => m.CART_ROUTES),
    canActivate: [AuthGuard],
  },
  {
    path: 'reservations',
    loadChildren: () =>
      import('./features/reservations/reservations.routes').then((m) => m.RESERVATIONS_ROUTES),
    canActivate: [AuthGuard],
  },
  {
    path: 'profile',
    loadChildren: () =>
      import('./features/profile/profile.routes').then((m) => m.PROFILE_ROUTES),
    canActivate: [AuthGuard],
  },
  {
    path: 'admin',
    loadChildren: () => import('./features/admin/admin.routes').then((m) => m.ADMIN_ROUTES),
    canActivate: [AuthGuard],
  },
  {
    path: 'branch',
    loadChildren: () =>
      import('./features/branch/branch.routes').then((m) => m.BRANCH_ROUTES),
    canActivate: [AuthGuard],
  },
  {
    path: 'pos',
    loadChildren: () => import('./features/pos/pos.routes').then((m) => m.POS_ROUTES),
    canActivate: [AuthGuard],
  },
  { path: '**', redirectTo: 'catalog' },
];