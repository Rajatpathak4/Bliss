import { Component, OnDestroy, OnInit } from "@angular/core";
import { FormBuilder, Validators } from "@angular/forms";
import { ActivatedRoute, Router } from "@angular/router";
import { Subscription } from "rxjs";

import { AuthService } from "../../../core/services/auth.service";
import { SocialAuthService } from "@abacritt/angularx-social-login";
import { GlobalServiceService } from "../../../core/services/global-service.service";

@Component({
  selector: "app-login",
  templateUrl: "./login.component.html",
  styleUrls: ["./login.component.scss"],
})
export class LoginComponent implements OnInit, OnDestroy {
  loading = false;
  errorMsg = "";
  showPassword = false;
  form = this.fb.group({
    email: ["", [Validators.required, Validators.email]],
    password: ["", [Validators.required]],
  });

  private authSub?: Subscription;

  constructor(
    private fb: FormBuilder,
    private auth: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private socialAuth: SocialAuthService,
    private glbSrvc: GlobalServiceService
  ) {}

ngOnInit(): void {
    // Make sure auto sign-in is disabled every time login page loads
    if ((window as any).google?.accounts?.id) {
      (window as any).google.accounts.id.disableAutoSelect();
    }

    this.authSub = this.socialAuth.authState.subscribe((user) => {
  console.log("Google authState:", user);

  if (!user || this.auth.isAuthenticated()) {
    return;
  }

      if (!user.idToken) {
        return;
      }

      this.auth.googleLogin(user.idToken).subscribe({
        next: () => {
          this.router.navigateByUrl("/dashboard");
        },
        error: () => {
          this.glbSrvc.showToastr("Google login failed", "error");
        },
      });
    });
  }


  ngOnDestroy(): void {
    this.authSub?.unsubscribe();
  }

  get f() {
    return this.form.controls;
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.loading = true;
    this.errorMsg = "";

    const { email, password } = this.form.getRawValue();
    this.auth.login({ email: email!, password: password! }).subscribe({
      next: (res) => {
        if (res?.status !== "TRUE") {
          return;
        }
        const returnUrl =
          this.route.snapshot.queryParamMap.get("returnUrl") || "/dashboard";
        this.router.navigateByUrl(returnUrl).then((result) => {});
      },
    });
  }
}