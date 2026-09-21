import { Routes } from '@angular/router';
import { AdminShellComponent } from './admin-shell.component';
import { AdminUsersComponent } from './admin-users.component';
import { AdminCatalogComponent } from './admin-catalog.component';
import { AdminProductsComponent } from './admin-products.component';
import { AdminInventoryComponent } from './admin-inventory.component';
import { AdminReportsComponent } from './admin-reports.component';
import { AdminAiReportsComponent } from './admin-ai-reports.component';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    component: AdminShellComponent,
    children: [
      { path: '', redirectTo: 'users', pathMatch: 'full' },
      { path: 'users', component: AdminUsersComponent },
      { path: 'catalog', component: AdminCatalogComponent },
      { path: 'products', component: AdminProductsComponent },
      { path: 'inventory', component: AdminInventoryComponent },
      { path: 'reports', component: AdminReportsComponent },
      { path: 'reports/ai', component: AdminAiReportsComponent },
    ],
  },
];