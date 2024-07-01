import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    console.log('authGuard: User is authenticated');
    return true;
  } else {
    console.log('authGuard: User is not authenticated, redirecting to login');
    router.navigate(['login']);
    return false;
  }
};
