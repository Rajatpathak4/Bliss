# LIC Tracker — Angular Admin Dashboard

A pixel-faithful rebuild of the LIC Tracker client-management UI in **Angular (NgModule based — not standalone)** with **SCSS**. Every screen is a real component with its own `.html`, `.ts`, and `.scss` files, and all mock data lives in a single API constant.

## Requirements
- Node.js 18.13+ (or 20+)
- npm 9+

## Run it
```bash
npm install
npm start          # → http://localhost:4200
```
Build for production:
```bash
npm run build
```

## Demo login
```
Email:    admin@nexadmin.io
Password: admin123
```

## What's included
- **Auth** — split-screen Sign In / Sign Up (reactive forms + validation)
- **Forgot password** — 3-step stepper (Email → Verify → Reset)
- **Dashboard** — 4 KPI cards + 4 ApexCharts (area / line / bar / area)
- **Clients** — bulk import (drag & drop), add-client form, searchable table, view + edit modals, delete
- **Profile** — profile card
- **Navbar** — notifications dropdown + profile menu + dark-mode toggle
- **AuthGuard / GuestGuard** — route protection
- **AuthInterceptor** — attaches `Bearer` token, logs out on 401

## Project structure
```
src/app/
├── core/
│   ├── constants/api.constant.ts     ← ALL mock data lives here
│   ├── models/                       ← typed interfaces
│   ├── guards/                       ← auth.guard.ts, guest.guard.ts
│   ├── interceptors/auth.interceptor.ts
│   └── services/                     ← auth, client, dashboard, notification
├── shared/shared.module.ts           ← re-exports Common/Forms modules
├── layout/                           ← navbar + main-layout shell
│   └── layout.module.ts
├── features/                         ← lazy-loaded feature modules
│   ├── auth/                         (login, signup, split-screen layout)
│   ├── forgot-password/
│   ├── dashboard/
│   ├── clients/                      (list, form, view-modal, edit-modal)
│   └── profile/
├── app-routing.module.ts
├── app.module.ts
└── app.component.*
```

## Backend API (live)
All services now call the FastAPI backend through `ApiService`
(`core/services/api.service.ts`), which prefixes every request with
`environment.apiBaseUrl`. The `AuthInterceptor` attaches the Bearer token and
logs the user out on a 401.

Set your API origin in `src/environments/environment.ts` (`apiBaseUrl`).
Endpoints live in one place: `core/constants/api-endpoints.constant.ts`.

| Endpoint | Method | Used by | Purpose |
|---|---|---|---|
| `/login` | POST | AuthService | sign in → `{ access_token \| token, user }` |
| `/signup` | POST | AuthService | register |
| `/logout` | POST | AuthService | invalidate token |
| `/alerts` | GET | NotificationService | navbar notifications |
| `/get_user_table_data` | GET | ClientService | clients table |
| `/user_modal_data?id=` | GET | ClientService | client detail (view modal) |
| `/add_user_data` | POST | ClientService | create client |
| `/update_user_data` | POST | ClientService | update client |
| `/upload_user_excel` | POST | ClientService | bulk import (multipart) |
| `/delete_user_excel` | POST | ClientService | clear uploaded excel |
| `/get_active_client` | GET | DashboardService | Active-Users card + chart |
| `/get_premium_stats` | GET | DashboardService | Premium-Due card + chart |

### Expected request/response shapes
- **Login/Signup** — accepts `{ access_token }` (OAuth2 style) **or** `{ token }`,
  plus an optional `user` object. If `user` is omitted, a minimal one is built
  from the email. Adjust field names in `AuthApiResponse` (`models/user.model.ts`).
- **Clients** — `get_user_table_data` returns `Client[]` matching
  `models/client.model.ts`. `user_modal_data` returns one `Client`.
- **Dashboard** — each endpoint may return
  `{ count, label?, hint?, trend?, categories?, series?, target? }`; missing
  fields fall back gracefully. See `dashboard.service.ts` for the exact contract.

### Endpoints still needed (currently placeholders / stubs)
- **Delete a single client** — no path was provided; `deleteClient()` posts to
  `/delete_user_data`. Confirm or rename in `api-endpoints.constant.ts`.
- **Revenue** and **New-Clients** charts + the "Premium Done" / "Revenue" cards —
  no endpoints yet, so they keep placeholder values from `api.constant.ts`.
- **Forgot-password** (send code / verify / reset) — `requestResetCode()` is a
  local stub; wire it when the reset routes exist.

### Token storage
Stored in `localStorage` (keys `nexadmin.token`, `nexadmin.user`). To clear the
session when the tab closes, change the single `STORAGE` constant in
`auth.service.ts` to `sessionStorage`.

## Notes
- The left art panel on the auth screens is recreated with CSS/SVG (the
  original screenshot bitmap isn't shipped). Drop a real image into
  `src/assets/` and set it as the panel background if you prefer.
- Data changes (add / edit / delete / import) are kept in an in-memory
  `BehaviorSubject`, so they reset on refresh — expected for a mock backend.
