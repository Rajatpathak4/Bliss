import { Component, inject } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.scss'],
})
export class ForgotPasswordComponent {
  private fb = inject(FormBuilder);

  step = 1;
  loading = false;
  message = '';

  steps = [
    { n: 1, label: 'Email' },
    { n: 2, label: 'Verify' },
    { n: 3, label: 'Reset' },
  ];

  emailForm = this.fb.group({
    email: ['admin@nexadmin.io', [Validators.required, Validators.email]],
  });

  codeForm = this.fb.group({
    code: ['', [Validators.required, Validators.minLength(4)]],
  });

  resetForm = this.fb.group({
    password: ['', [Validators.required, Validators.minLength(6)]],
    confirmPassword: ['', [Validators.required]],
  });

  constructor(
    private auth: AuthService,
    private router: Router
  ) {}

  sendCode(): void {
    if (this.emailForm.invalid) {
      this.emailForm.markAllAsTouched();
      return;
    }
    this.loading = true;
    this.auth
      .requestResetCode(this.emailForm.value.email!)
      .subscribe(() => {
        this.loading = false;
        this.message = 'A 6-digit verification code was sent to your email.';
        this.step = 2;
      });
  }

  verifyCode(): void {
    if (this.codeForm.invalid) {
      this.codeForm.markAllAsTouched();
      return;
    }
    this.message = '';
    this.step = 3;
  }

  resetPassword(): void {
    const { password, confirmPassword } = this.resetForm.value;
    if (this.resetForm.invalid || password !== confirmPassword) {
      this.resetForm.markAllAsTouched();
      this.message =
        password !== confirmPassword ? 'Passwords do not match.' : '';
      return;
    }
    this.loading = true;
    setTimeout(() => {
      this.loading = false;
      this.router.navigate(['/auth/login']);
    }, 700);
  }

  goBack(): void {
    if (this.step > 1) {
      this.step -= 1;
      this.message = '';
    } else {
      this.router.navigate(['/auth/login']);
    }
  }
}
