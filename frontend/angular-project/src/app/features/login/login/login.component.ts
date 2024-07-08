import { Component } from '@angular/core';
import { AuthService } from '../../../auth.service';
import { Router } from '@angular/router';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule, NgIf],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})

export class LoginComponent {
  form: FormGroup;
  errorMessage: string = '';

  constructor(
    private fb:FormBuilder, 
    private authService: AuthService, 
    private router: Router) {
      this.form = this.fb.group({
        username: ['',[Validators.required, Validators.minLength(3), Validators.maxLength(20), this.usernameValidator]],
        password: ['',[Validators.required, Validators.minLength(8)]]
      });
    }

    usernameValidator(control: FormControl) {
      const username = control.value;
      const regex = /^[a-zA-Z0-9_-]+$/;
      if (username && !regex.test(username)) {
        return { invalidUsername: true };
      }
      return null;
    }

    login() {
      if (this.form.invalid) {
        this.form.markAllAsTouched(); 
        return;
      }
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
          },
          (error) => {
            console.error("Login error:", error);
            this.errorMessage = "Nume de utilizator sau parolă incorecte. Vă rugăm încercați din nou."
          }
        );
      }
    }
}



