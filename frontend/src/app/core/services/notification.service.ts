import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { ApiService } from './api.service';
import { API_ENDPOINTS, ApiMethod } from '../constants/api-endpoints.constant';
import { AppNotification } from '../models/notification.model';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly store$ = new BehaviorSubject<AppNotification[]>([]);

  /** Live alert list — the navbar subscribes to this. */
  notifications$: Observable<AppNotification[]> = this.store$.asObservable();

  constructor(private api: ApiService) {}

  get unreadCount(): number {
    return this.store$.value.filter((n) => n.unread).length;
  }

  /** GET /get_notifications -> { unread_count, notifications[] } */
  loadAlerts(): void {
    this.api.requestCall(API_ENDPOINTS.ALERTS, ApiMethod.GET).subscribe({
      next: (res) => {
        const list = (res?.notifications ?? []).map((n: any): AppNotification => ({
          id: n.id,
          title: n.title,
          message: n.message,
          type: n.type,
          date: n.date,
          unread: !n.is_read,          // backend is_read -> unread flip
        }));
        this.store$.next(list);
      },
      error: () => this.store$.next([]),
    });
  }

  /** Mark all read — local + persist to backend */
  markAllRead(): void {
    // optimistic: turant UI update
    this.store$.next(this.store$.value.map((n) => ({ ...n, unread: false })));
    // persist
    this.api.requestCall(API_ENDPOINTS.MARK_ALL_READ, ApiMethod.GET).subscribe({
      error: () => {},   // fail hua to bhi UI already updated; next poll sync karega
    });
  }

  /** Mark a single notification read */
  markRead(id: number): void {
    this.store$.next(
      this.store$.value.map((n) => (n.id === id ? { ...n, unread: false } : n))
    );
    this.api.requestCall(
      `${API_ENDPOINTS.MARK_NOTIFICATION_READ}?notification_id=${id}`,
      ApiMethod.GET
    ).subscribe({ error: () => {} });
  }
}