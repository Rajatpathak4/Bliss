import { Injectable } from '@angular/core';
import { from, Observable, of, EMPTY } from 'rxjs';
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
import { Router, ActivatedRoute } from '@angular/router';

const TOKEN_KEY = 'nexadmin.token';
const USER_KEY = 'nexadmin.user';

const STORAGE: Storage = localStorage;

@Injectable({ providedIn: 'root' })
export class AuthService {
  constructor(private httpService: ApiService,private globalService: GlobalServiceService, private router: Router, private route: ActivatedRoute) {}

login(payload: LoginRequest): Observable<any> {
  return this.httpService
    .requestCall(API_ENDPOINTS.LOGIN, ApiMethod.POST, payload)
    .pipe(
      switchMap((res: any) => {

        if (res?.status === 'TRUE') {
          this.persistSession(this.normalizeFlow(res, payload.email));
          return of(res);
        }

        if (res?.value?.relogin_required) {

          return from(
            this.globalService.triggerSweetAlert({
              title: 'Please confirm...',
              icon: 'warning',
              text: "You're already logged in on another device. Do you want to terminate that session and log in here?",
              confirmButtonText: 'Yes',
              denyButtonText: 'No'
            })
          ).pipe(
            switchMap(result => {

              if (!result.isConfirmed) {
                return EMPTY;
              }

              return this.reLoginUser({
                ...payload,
                is_confirm: true
              });
            })
          );
        }

        return of(res);
      })
    );
}

reLoginUser(
  payload: LoginRequest & { is_confirm: boolean }
): Observable<any> {

  return this.httpService
    .requestCall(API_ENDPOINTS.RE_LOGIN, ApiMethod.POST, payload)
    .pipe(
      tap((res: any) => {
        if (res?.status === 'TRUE') {
          this.persistSession(this.normalizeFlow(res, payload.email));
        }
      })
    );
}

  /**
   * Normalize backend response.
   */
private normalizeFlow(res: any, email: string): any {
  const user = res.data || res.value;

  return {
    uid: user.uid,
    name: user.name,
    email: user.email ?? email,
    token: user.token,
    redirectUrl: user.redirectUrl,
    first_redirection: user.first_redirection,
    is_active: user.is_active,
    current_time: user.current_time,
  };
}

  signup(payload: SignupRequest): Observable<AuthResponse> {
    return this.httpService.requestCall(API_ENDPOINTS.SIGNUP, ApiMethod.POST, payload)
      .pipe(
        map((res) => this.normalize(res, payload.email, payload.fullName)),
        tap((res) => this.persistSession(res))
      );
  }

  logout(): Observable<unknown> {
    this.clearSession();
    return this.httpService.requestCall(API_ENDPOINTS.LOGOUT, ApiMethod.POST).pipe(catchError(() => of(null)));
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