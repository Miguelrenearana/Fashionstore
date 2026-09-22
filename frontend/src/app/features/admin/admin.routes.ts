import { Routes } from '@angular/router';
import { AdminShellComponent } from './admin-shell.component';
import { AdminUsersComponent } from './admin-users.component';
import { AdminCatalogConfigComponent } from './admin-catalog-config.component';
import { AdminProductsComponent } from './admin-products.component';
import { AdminInventoryComponent } from './admin-inventory.component';
import { AdminReportsComponent } from './admin-reports.component';
import { AdminAiReportsComponent } from './admin-ai-reports.component';
import { AdminPromotionsComponent } from './admin-promotions.component';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    component: AdminShellComponent,
    children: [
      { path: '', redirectTo: 'users', pathMatch: 'full' },
      { path: 'users', component: AdminUsersComponent },
      { path: 'catalog', component: AdminCatalogConfigComponent },
      { path: 'products', component: AdminProductsComponent },
      { path: 'inventory', component: AdminInventoryComponent },
      { path: 'promotions', component: AdminPromotionsComponent },
      { path: 'reports', component: AdminReportsComponent },
      { path: 'reports/ai', component: AdminAiReportsComponent },
    ],
  },
];