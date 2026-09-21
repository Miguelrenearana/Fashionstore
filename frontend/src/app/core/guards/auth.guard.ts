import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '@core/auth/auth.service';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): boolean {
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/auth']);
      return false;
    }
    return true;
  }
}

@Injectable({ providedIn: 'root' })
export class NegAuthGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): boolean {
    if (this.auth.isAuthenticated()) {
      this.router.navigate([this.auth.homeRoute()]);
      return false;
    }
    return true;
  }
}

/** Permite el acceso solo a usuarios cuyo rol esté en `data.roles` (o en staff si no se indica). */
@Injectable({ providedIn: 'root' })
export class RoleGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/auth']);
      return false;
    }
    const allowed = (route.data['roles'] as string[] | undefined) ?? undefined;
    const ok = allowed ? this.auth.hasAnyRole(...allowed) : this.auth.isStaff();
    if (!ok) {
      this.router.navigate(['/']);
      return false;
    }
    return true;
  }
}