import { Injectable } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { catchError, map, switchMap, tap } from 'rxjs/operators';

import { ApiService } from './api.service';
import { API_ENDPOINTS, ApiMethod } from '../constants/api-endpoints.constant';
import {
  AuthApiResponse,
  AuthResponse,
  AuthUser,
  LoginRequest,
  SignupRequest,
} from '../models/user.model';
import { GlobalServiceService } from './global-service.service';

const TOKEN_KEY = 'nexadmin.token';
const USER_KEY = 'nexadmin.user';

/**
 * Switch to `sessionStorage` if you want the session cleared when the
 * browser tab closes. localStorage keeps the user signed in across tabs.
 */
const STORAGE: Storage = localStorage;

@Injectable({ providedIn: 'root' })
export class AuthService {
  constructor(private httpService: ApiService, private globlSrv: GlobalServiceService) {}

login(payload: LoginRequest): Observable<AuthResponse> {
  return this.httpService.requestCall(API_ENDPOINTS.LOGIN, ApiMethod.POST, payload)
    .pipe(
      switchMap((res: any) => {
        if (res?.status === 'FALSE') {
          this.globlSrv.showToastr(res?.message, 'error');
          return throwError(() => new Error(res?.message || 'Login failed'));
        }
        return of(this.normalize(res, payload.email));
      }),
      tap((res) => {
        this.persistSession(res);
      })
    );
}

  signup(payload: SignupRequest): Observable<AuthResponse> {
    return this.httpService.requestCall(API_ENDPOINTS.SIGNUP, ApiMethod.POST, payload)
      .pipe(
        map((res) => this.normalize(res, payload.email, payload.fullName)),
        tap((res) => this.persistSession(res))
      );
  }

  /**
   * POST /logout — tells the backend to invalidate the token, then clears
   * local session no matter what the server responds.
   */
  logout(): Observable<unknown> {
    // Clear the local session first so route guards react immediately,
    // then notify the backend (ignoring any error from that call).
    this.clearSession();
    return this.httpService.requestCall(API_ENDPOINTS.LOGOUT, ApiMethod.POST).pipe(catchError(() => of(null)));
  }

  /** Clears local session immediately (used by the interceptor on 401). */
  clearSession(): void {
    STORAGE.removeItem(TOKEN_KEY);
    STORAGE.removeItem(USER_KEY);
  }

  /**
   * Forgot-password step 1. No dedicated endpoint was provided, so this is a
   * local stub — wire it to your reset route when you have one.
   */
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

  /* ---------- helpers ---------- */

  /** Reads whichever token field the backend sends and fills a user fallback. */
private normalize(
  res: any,
  email: string,
  fullName?: string
): AuthResponse {

  const data = res.value;

  return {
    token: data.token,
    user: {
      id: data.uid,
      fullName: data.name,
      email: data.email,
      phone_number: '',
      company: '',
      role: 'User',
      location: '',
      avatarInitials: this.initials(data.name)
    }
  };
}

  private fallbackUser(email: string, fullName?: string): AuthUser {
    const name = fullName || email.split('@')[0];
    return {
      id: 0,
      fullName: name,
      email,
      phone_number: '',
      company: '',
      role: 'User',
      location: '',
      avatarInitials: this.initials(name),
    };
  }

  private persistSession(res: AuthResponse): void {
    if (res.token) STORAGE.setItem(TOKEN_KEY, res.token);
    STORAGE.setItem(USER_KEY, JSON.stringify(res.user));
  }

  private initials(name: string): string {
    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0].toUpperCase())
      .join('');
  }
}
