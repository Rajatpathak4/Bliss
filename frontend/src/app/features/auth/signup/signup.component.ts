import { Component } from '@angular/core';
import { AbstractControl, FormBuilder, ValidationErrors, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.scss'],
})
export class SignupComponent {
  loading = false;
  errorMsg = '';

  form = this.fb.group(
    {
      fullName: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]],
    },
    { validators: [this.matchPasswords] }
  );

  constructor(
    private fb: FormBuilder,
    private auth: AuthService,
    private router: Router
  ) {}

  get f() {
    return this.form.controls;
  }

  private matchPasswords(group: AbstractControl): ValidationErrors | null {
    const pw = group.get('password')?.value;
    const cpw = group.get('confirmPassword')?.value;
    return pw && cpw && pw !== cpw ? { mismatch: true } : null;
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.loading = true;
    this.errorMsg = '';

    const { fullName, email, password } = this.form.getRawValue();
    this.auth
      .signup({ fullName: fullName!, email: email!, password: password! })
      .subscribe({
        next: () => this.router.navigateByUrl('/dashboard'),
        error: (err) => {
          this.loading = false;
          this.errorMsg =
            err?.error?.detail ||
            err?.message ||
            'Could not create the account.';
        },
      });
  }
}
