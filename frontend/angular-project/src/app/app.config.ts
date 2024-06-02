import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { AuthService } from './auth.service';
import { AuthInterceptorService } from './auth-interceptor.service';
import { routes } from './app.routes';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { provideHttpClient } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    AuthService,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptorService,
      multi: true
    },
    provideHttpClient()
  ]
};
