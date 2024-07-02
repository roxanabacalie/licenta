import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { FooterComponent } from './core/footer/footer.component';
import { NavbarComponent } from './core/navbar/navbar.component';
import { HomepageComponent } from './features/homepage/homepage.component';
import { GoogleMapsService } from './google-maps.service';
import { HttpClientModule } from '@angular/common/http';
import { EditRoutesComponent } from './features/edit-routes/edit-routes.component';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, FooterComponent, NavbarComponent, HomepageComponent, HttpClientModule, EditRoutesComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [GoogleMapsService] 
})

export class AppComponent {
  title = 'angular-project';

  constructor(private authService: AuthService) {}

  ngOnInit() {
    if (this.authService.isLoggedIn()) {
      this.authService.loggedIn.next(true);
    }
  }
}
