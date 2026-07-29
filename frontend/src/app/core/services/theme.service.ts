import { Injectable, OnInit } from "@angular/core";
import { ApiService } from "./api.service";
import { API_ENDPOINTS, ApiMethod } from "../constants/api-endpoints.constant";

const THEME_KEY = "theme-mode";
const DARK_VALUE = "dark-modal";
const LIGHT_VALUE = "light-modal";
const USER_KEY = "nexadmin.user";

@Injectable({ providedIn: "root" })
export class ThemeService implements OnInit {
  constructor(private httpService: ApiService) {   // AuthService yahan inject nahi karna — circular dependency
    const isDark = localStorage.getItem(THEME_KEY) === DARK_VALUE;
    document.body.classList.toggle("dark", isDark);
  }
ngOnInit(): void {
  this.toggleTheme()
}
  toggleTheme(): void {
    const isDark = document.body.classList.toggle("dark");
    const newTheme = isDark ? "dark" : "light";
    localStorage.setItem(THEME_KEY, isDark ? DARK_VALUE : LIGHT_VALUE);

    const userId = this.getCurrentUserId();
    if (!userId) return;

    const url = `${API_ENDPOINTS.UPDATE_THEME}?user_id=${userId}`;
    this.httpService.requestCall(url, ApiMethod.POST, { theme: newTheme }).subscribe();
  }

  applyTheme(theme: "light" | "dark"): void {
    document.body.classList.toggle("dark", theme === "dark");
    localStorage.setItem(THEME_KEY, theme === "dark" ? DARK_VALUE : LIGHT_VALUE);
  }

  private getCurrentUserId(): number | null {
    try {
      const raw = localStorage.getItem(USER_KEY);
      if (!raw) return null;
      const user = JSON.parse(raw);
      return user?.id ?? null;
    } catch {
      return null;
    }
  }
}