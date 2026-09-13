import { Routes } from '@angular/router';
import { CatalogComponent } from './catalog.component';
import { ProductDetailComponent } from './product-detail.component';

export const CATALOG_ROUTES: Routes = [
  { path: '', component: CatalogComponent },
  { path: ':id', component: ProductDetailComponent },
];