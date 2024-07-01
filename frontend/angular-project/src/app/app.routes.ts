import { Routes } from '@angular/router';
import { HomepageComponent } from './features/homepage/homepage.component';
import { LoginComponent } from './features/login/login/login.component';
import { EditRoutesComponent } from './features/edit-routes/edit-routes.component';
import { authGuard } from './auth.guard';

export const routes: Routes = [
    { path: '', component: HomepageComponent },
    { path: 'login', component: LoginComponent },
    { path: 'edit-routes', component: EditRoutesComponent, canActivate: [authGuard]}
    
];
