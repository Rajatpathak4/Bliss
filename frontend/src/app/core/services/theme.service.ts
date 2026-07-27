import { Injectable } from "@angular/core";
import { ApiService } from "./api.service";
import { API_ENDPOINTS, ApiMethod } from "../constants/api-endpoints.constant";

const THEME_KEY = "theme-mode";
const DARK_VALUE = "dark-modal";
const LIGHT_VALUE = "light-modal";

@Injectable({ providedIn: "root" })
export class ThemeService {
  constructor(private httpService: ApiService,) {
    const isDark = localStorage.getItem(THEME_KEY) === DARK_VALUE;
    document.body.classList.toggle("dark", isDark);
  }

  // theme.service.ts
  toggleTheme(): void {
    const isDark = document.body.classList.toggle("dark");
    const newTheme = isDark ? "dark" : "light";
    localStorage.setItem(THEME_KEY, isDark ? DARK_VALUE : LIGHT_VALUE);

    this.httpService
      .requestCall(API_ENDPOINTS.UPDATE_THEME, ApiMethod.POST, {
        theme: newTheme,
      })
      .subscribe();
  }

  applyTheme(theme: "light" | "dark"): void {
    document.body.classList.toggle("dark", theme === "dark");
    localStorage.setItem(
      THEME_KEY,
      theme === "dark" ? DARK_VALUE : LIGHT_VALUE,
    );
  }
}
