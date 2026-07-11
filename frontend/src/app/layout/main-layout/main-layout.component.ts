import { Component, OnDestroy } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { Subscription, filter } from 'rxjs';

@Component({
  selector: 'app-main-layout',
  templateUrl: './main-layout.component.html',
  styleUrls: ['./main-layout.component.scss'],
})
export class MainLayoutComponent implements OnDestroy {
  /** The tab bar only shows on Dashboard & Clients (not on Profile). */
  showTabs = true;

  private sub: Subscription;

  constructor(private router: Router) {
    this.evaluate(this.router.url);
    this.sub = this.router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe((e) => this.evaluate(e.urlAfterRedirects));
  }

  private evaluate(url: string): void {
    this.showTabs = url.startsWith('/dashboard') || url.startsWith('/clients');
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }
}
