import { Injectable } from "@angular/core";
import { from, Observable, of, EMPTY } from "rxjs";
import { catchError, map, switchMap, tap } from "rxjs/operators";

import { ApiService } from "./api.service";
import { API_ENDPOINTS, ApiMethod } from "../constants/api-endpoints.constant";
import {
  AuthApiResponse,
  AuthResponse,
  AuthUser,
  LoginRequest,
  SignupRequest,
} from "../models/user.model";
import { GlobalServiceService } from "./global-service.service";
import { Router, ActivatedRoute } from "@angular/router";
import { ThemeService } from "./theme.service";

const TOKEN_KEY = "nexadmin.token";
const USER_KEY = "nexadmin.user";

const STORAGE: Storage = localStorage;

@Injectable({ providedIn: "root" })
export class AuthService {
  constructor(
    private httpService: ApiService,
    private globalService: GlobalServiceService,
    private router: Router,
    private route: ActivatedRoute,
    private themeService: ThemeService,
  ) {}

  login(payload: LoginRequest): Observable<any> {
    return this.httpService
      .requestCall(API_ENDPOINTS.LOGIN, ApiMethod.POST, payload)
      .pipe(
        switchMap((res: any) => {
          if (res?.status === "TRUE") {
            this.persistSession(this.normalizeFlow(res, payload.email));
            this.globalService.showToastr(res?.message, "success");
            return of(res);
          } else {
            this.globalService.showToastr(res?.message, "error");
          }

          if (res?.value?.relogin_required) {
            return from(
              this.globalService.triggerSweetAlert({
                title: "Please confirm...",
                icon: "warning",
                text: "You're already logged in on another device. Do you want to terminate that session and log in here?",
                confirmButtonText: "Yes",
                denyButtonText: "No",
              }),
            ).pipe(
              switchMap((result) => {
                if (!result.isConfirmed) {
                  return EMPTY;
                }

                return this.reLoginUser({
                  ...payload,
                  is_confirm: true,
                });
              }),
            );
          }

          return of(res);
        }),
      );
  }

  reLoginUser(
    payload: LoginRequest & { is_confirm: boolean },
  ): Observable<any> {
    return this.httpService
      .requestCall(API_ENDPOINTS.RE_LOGIN, ApiMethod.POST, payload)
      .pipe(
        tap((res: any) => {
          if (res?.status === "TRUE") {
            this.persistSession(this.normalizeFlow(res, payload.email));
          }
        }),
      );
  }

  private normalizeFlow(res: any, email: string): AuthResponse {
    const user = res.data || res.value;

    if (user.theme) {
    this.themeService.applyTheme(user.theme);   // localStorage bhi update ho jaayegi
  }

    return {
      token: user.token,
      user: {
        id: user.uid,
        fullName: user.name,
        email: user.email ?? email,
        phone_number: "",
        company: "",
        role: "User",
        location: "",
        avatarInitials: this.initials(user.name ?? email),
        avatarUrl: null,
        redirectUrl: user.redirectUrl,
        first_redirection: user.first_redirection,
        is_active: user.is_active,
        current_time: user.current_time,
      } as AuthUser & {
        redirectUrl?: any;
        first_redirection?: any;
        is_active?: any;
        current_time?: any;
      },
    };
  }

  signup(payload: SignupRequest): Observable<AuthResponse> {
    const backendPayload = {
      name: payload.fullName,
      email: payload.email,
      password: payload.password,
      theme : payload.theme
    };

    return this.httpService
      .requestCall(API_ENDPOINTS.SIGNUP, ApiMethod.POST, backendPayload)
      .pipe(
        map((res) => this.normalize(res, payload.email, payload.fullName)),
        tap((res) => this.persistSession(res)),
      );
  }


logout(user_id: number) {

  // Clear local storage immediately
  this.clearSession();

  window.google?.accounts?.id?.disableAutoSelect();
  window.google?.accounts?.id?.cancel();

  // Backend logout
  const url = `${API_ENDPOINTS.LOGOUT}?user_id=${user_id}`;

  this.httpService.requestCall(url, ApiMethod.GET).subscribe({
    next: (data: any) => {
      this.globalService.showToastr(data?.message, "success");
    },
    error: () => {},
    complete: () => {
      this.router.navigateByUrl("/auth/login");
    },
  });
}

  clearSession(): void {
    STORAGE.removeItem(TOKEN_KEY);
    STORAGE.removeItem(USER_KEY);
  }

  requestResetCode(email: string): Observable<{ sent: boolean }> {
    return of({ sent: !!email });
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null {
    return STORAGE.getItem(TOKEN_KEY);
  }

  getUser(): AuthUser | null {
    const raw = STORAGE.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  }

  private normalize(res: any, email: string, fullName?: string): AuthResponse {
    return {
      token: res.access_token,
      user: {
        id: res.user.id,
        fullName: res.user.name,
        email: res.user.email,
        phone_number: "",
        company: "",
        role: "User",
        location: "",
        avatarInitials: this.initials(res.user.name),
        avatarUrl: null,
      },
    };
  }

  private fallbackUser(email: string, fullName?: string): AuthUser {
    const name = fullName || email.split("@")[0];
    return {
      id: 0,
      fullName: name,
      email,
      phone_number: "",
      company: "",
      role: "User",
      location: "",
      avatarInitials: this.initials(name),
      avatarUrl: null,
    };
  }

  private persistSession(res: AuthResponse): void {
    if (res.token) STORAGE.setItem(TOKEN_KEY, res.token);
    STORAGE.setItem(USER_KEY, JSON.stringify(res.user));
  }

  private initials(name: string): string {
    return name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0].toUpperCase())
      .join("");
  }

  googleLogin(idToken: string): Observable<any> {
    return this.httpService
      .requestCall(API_ENDPOINTS.GOOGLE_LOGIN, ApiMethod.POST, {
        token: idToken,
      })
      .pipe(
        tap((res: any) => {
          if (res?.status && res.status !== "TRUE") {
            throw new Error(res?.message || "Google login failed");
          }

          this.persistSession(this.normalizeFlow(res, ""));
        }),
      );
  }
  
}
