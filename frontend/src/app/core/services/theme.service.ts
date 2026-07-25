import { Injectable } from '@angular/core';

const THEME_KEY = 'theme-mode';
const DARK_VALUE = 'dark-modal';
const LIGHT_VALUE = 'light-modal';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  constructor() {
    const isDark = sessionStorage.getItem(THEME_KEY) === DARK_VALUE;
    document.body.classList.toggle('dark', isDark);
  }

  toggleTheme(): void {
    const isDark = document.body.classList.toggle('dark');
    sessionStorage.setItem(THEME_KEY, isDark ? DARK_VALUE : LIGHT_VALUE);
  }
}