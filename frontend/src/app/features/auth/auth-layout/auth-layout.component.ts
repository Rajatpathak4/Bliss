import { Component } from '@angular/core';

@Component({
  selector: 'app-auth-layout',
  templateUrl: './auth-layout.component.html',
  styleUrls: ['./auth-layout.component.scss'],
})
export class AuthLayoutComponent {
  /** Heights (%) for the decorative bar chart on the left panel. */
  bars: number[] = [30, 45, 62, 88, 100, 82, 70, 58, 48, 40, 34, 28, 24, 20, 16, 12];
}
