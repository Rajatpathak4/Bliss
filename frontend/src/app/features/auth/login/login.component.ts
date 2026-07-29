import {
  AfterViewInit,
  Component,
  ElementRef,
  inject,
  OnDestroy,
  OnInit,
  ViewChild,
} from "@angular/core";
import { FormBuilder, Validators } from "@angular/forms";
import { ActivatedRoute, Router } from "@angular/router";

import { environment } from "../../../../environments/environment";
import { AuthService } from "../../../core/services/auth.service";
import { GlobalServiceService } from "../../../core/services/global-service.service";

declare global {
  interface Window {
    google?: any;
  }
}

@Component({
  selector: "app-login",
  templateUrl: "./login.component.html",
  styleUrls: ["./login.component.scss"],
})
export class LoginComponent implements OnInit, AfterViewInit, OnDestroy {
  private fb = inject(FormBuilder);

  loading = false;
  errorMsg = "";
  googleLoading = false;
  showPassword = false;
  form = this.fb.group({
    email: ["", [Validators.required, Validators.email]],
    password: ["", [Validators.required]],
  });

  @ViewChild("googleButton", { static: false })
  private googleButton?: ElementRef<HTMLDivElement>;

  private googleScriptPromise?: Promise<void>;
  private googleTokenInFlight: string | null = null;

  constructor(
    private auth: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private glbSrvc: GlobalServiceService
  ) {}

  ngOnInit(): void {
    window.google?.accounts?.id?.disableAutoSelect();
  }

  ngAfterViewInit(): void {
    this.renderGoogleButton().catch((error) => {
      this.glbSrvc.showToastr(this.getGoogleErrorMessage(error), "error");
    });
  }

  ngOnDestroy(): void {
    window.google?.accounts?.id?.cancel();
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

  loginWithGoogle(): void {
    this.googleLoading = true;
    this.renderGoogleButton()
      .then(() => {
        this.googleLoading = false;
      })
      .catch((error) => {
        this.googleLoading = false;
        this.glbSrvc.showToastr(this.getGoogleErrorMessage(error), "error");
      });
  }

  private handleGoogleCredential(response: any): void {
    const idToken = response?.credential;

    if (!idToken) {
      this.googleLoading = false;
      this.glbSrvc.showToastr("Google did not return a login token", "error");
      return;
    }

    if (this.googleTokenInFlight === idToken) {
      return;
    }

    this.googleTokenInFlight = idToken;
    this.googleLoading = true;

    this.auth.googleLogin(idToken).subscribe({
      next: () => {
        this.router.navigateByUrl("/dashboard");
      },
      error: (error) => {
        this.googleTokenInFlight = null;
        this.googleLoading = false;
        this.glbSrvc.showToastr(this.getGoogleErrorMessage(error), "error");
      },
      complete: () => {
        this.googleLoading = false;
      },
    });
  }

  private renderGoogleButton(): Promise<void> {
    return this.loadGoogleScript().then(() => {
      const target = this.googleButton?.nativeElement;

      if (!target || !window.google?.accounts?.id) {
        throw new Error("Google login is not available");
      }

      window.google.accounts.id.initialize({
        client_id: environment.googleClientId,
        callback: (response: any) => this.handleGoogleCredential(response),
        auto_select: false,
      });

      target.innerHTML = "";
      window.google.accounts.id.renderButton(target, {
        theme: "outline",
        size: "large",
        text: "signin_with",
        shape: "rectangular",
        width: target.offsetWidth || 360,
      });
    });
  }

  private loadGoogleScript(): Promise<void> {
    if (window.google?.accounts?.id) {
      return Promise.resolve();
    }

    if (this.googleScriptPromise) {
      return this.googleScriptPromise;
    }

    this.googleScriptPromise = new Promise<void>((resolve, reject) => {
      const existingScript = document.getElementById("google-identity-service");

      if (existingScript) {
        existingScript.addEventListener("load", () => resolve(), { once: true });
        existingScript.addEventListener(
          "error",
          () => reject(new Error("Failed to load Google login")),
          { once: true }
        );
        return;
      }

      const script = document.createElement("script");
      script.id = "google-identity-service";
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Failed to load Google login"));
      document.head.appendChild(script);
    });

    return this.googleScriptPromise;
  }

  private getGoogleErrorMessage(error: any): string {
    return (
      error?.error?.message ||
      error?.error?.detail ||
      error?.message ||
      "Google login failed"
    );
  }
}
