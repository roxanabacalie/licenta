import { Component } from '@angular/core';
import { AuthService } from '../../../auth.service';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})

export class LoginComponent {
  form: FormGroup;
  constructor(
    private fb:FormBuilder, 
    private authService: AuthService, 
    private router: Router) {
      this.form = this.fb.group({
        username: ['',Validators.required],
        password: ['',Validators.required]
      });
    }

    login() {
      console.log('login component login')
      console.log('Form value:', this.form.value);
    console.log('Form errors:', this.form.errors);
      const val = this.form.value;
      console.log(val)
      if (val.username && val.password) {
        this.authService.login(val.username, val.password).subscribe(
          () => {
            console.log("User is logged in");
            this.router.navigateByUrl('/');
          }
        );
      }
    }
}



