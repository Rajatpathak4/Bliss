export type NotificationType = 'warning' | 'success' | 'info';

export interface AppNotification {
  id: number;
  title: string;
  message: string;
  type: string;
  date: string;
  unread: boolean;
}
