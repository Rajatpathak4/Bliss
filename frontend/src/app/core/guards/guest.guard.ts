import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';

import { AuthService } from '../services/auth.service';

/** Keeps signed-in users out of the auth pages. */
@Injectable({ providedIn: 'root' })
export class GuestGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): boolean | UrlTree {
    return this.auth.isAuthenticated()
      ? this.router.createUrlTree(['/dashboard'])
      : true;
  }
}
