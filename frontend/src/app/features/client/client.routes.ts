import { Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';
import { ClientShellComponent } from './client-shell.component';
import { CatalogComponent } from './catalog.component';
import { ProductDetailComponent } from './product-detail.component';
import { CartComponent } from './cart.component';
import { CheckoutComponent } from './checkout.component';
import { ReservationsComponent } from './reservations.component';
import { ReservationDetailComponent } from './reservation-detail.component';
import { ProfileComponent } from './profile.component';
import { PurchaseHistoryComponent } from './purchase-history.component';
import { NotificationsComponent } from './notifications.component';
import { RecommendationsComponent } from './recommendations.component';
import { ChatComponent } from './chat.component';

export const CLIENT_ROUTES: Routes = [
  {
    path: '',
    component: ClientShellComponent,
    canActivate: [AuthGuard],
    children: [
      { path: '', redirectTo: 'catalog', pathMatch: 'full' },
      { path: 'catalog', component: CatalogComponent },
      { path: 'catalog/:id', component: ProductDetailComponent },
      { path: 'cart', component: CartComponent },
      { path: 'checkout', component: CheckoutComponent },
      { path: 'reservations', component: ReservationsComponent },
      { path: 'reservations/:id', component: ReservationDetailComponent },
      { path: 'profile', component: ProfileComponent },
      { path: 'history', component: PurchaseHistoryComponent },
      { path: 'history/:id', component: PurchaseHistoryComponent },
      { path: 'notifications', component: NotificationsComponent },
      { path: 'recommendations', component: RecommendationsComponent },
      { path: 'chat', component: ChatComponent },
    ],
  },
];