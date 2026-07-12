import { Component, ElementRef, HostListener, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, timer } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';
import { NotificationService } from '../../core/services/notification.service';
import { AppNotification } from '../../core/models/notification.model';
import { AuthUser } from '../../core/models/user.model';
import { API_ENDPOINTS, ApiMethod } from '../../core/constants/api-endpoints.constant';
import { ApiService } from '../../core/services/api.service';
import { GlobalServiceService } from '../../core/services/global-service.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
})
export class NavbarComponent implements OnInit {
  user: AuthUser | null = null;
  notifications$!: Observable<AppNotification[]>;
  unreadCount = 0;
  darkMode = false;

  notifOpen = false;
  profileOpen = false;

  constructor(
    private auth: AuthService,
    private notificationService: NotificationService,
    private router: Router,
    private host: ElementRef<HTMLElement>,
    private httpService: ApiService,
    private globalSrv: GlobalServiceService
  ) {}

  ngOnInit(): void {
    this.user = this.auth.getUser();
    this.notifications$ = this.notificationService.notifications$;
    // Keep the unread badge in sync as alerts load / are marked read.
    this.notifications$.subscribe(
      (list) => (this.unreadCount = list.filter((n) => n.unread).length)
    );
    this.notificationService.loadAlerts();
     this.user = this.auth.getUser();
  this.notifications$ = this.notificationService.notifications$;
  this.notifications$.subscribe(
    (list) => (this.unreadCount = list.filter((n) => n.unread).length)
  );

  // poll every 30s
  timer(0, 500000).subscribe(() => this.notificationService.loadAlerts());
  }

  get initials(): string {
    return this.user?.avatarInitials ?? 'NA';
  }

  get shortName(): string {
    if (!this.user) return 'Guest';
    const [first, last] = this.user.fullName.split(' ');
    return last ? `${first} ${last[0]}.` : first;
  }

  toggleNotifications(event: MouseEvent): void {
    event.stopPropagation();
    this.notifOpen = !this.notifOpen;
    this.profileOpen = false;
    if (this.notifOpen) {
      this.notificationService.markAllRead();
      this.unreadCount = 0;
    }
  }

  toggleProfile(event: MouseEvent): void {
    event.stopPropagation();
    this.profileOpen = !this.profileOpen;
    this.notifOpen = false;
  }

toggleDark(): void {
    this.darkMode = !this.darkMode;
    document.body.classList.toggle('dark', this.darkMode);
  }

  goProfile(): void {
    this.profileOpen = false;
    this.router.navigate(['/profile']);
  }

  goForgotPassword(): void {
    this.profileOpen = false;
    this.router.navigate(['/forgot-password']);
  }

logout(user_id?: number): void {
  const url = `${API_ENDPOINTS.LOGOUT}?user_id=${user_id}`;
  this.httpService.requestCall(url, ApiMethod.GET).subscribe((data) => {
    this.profileOpen = false;
    this.auth.clearSession?.(); 
    this.router.navigate(['/auth/login']);
    this.globalSrv.showToastr(data?.message, 'success')
  });
}

  /** Close open dropdowns when clicking anywhere outside the navbar. */
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.host.nativeElement.contains(event.target as Node)) {
      this.notifOpen = false;
      this.profileOpen = false;
    }
  }
}
