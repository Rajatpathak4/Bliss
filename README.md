# Grid Ops — Auth + Dashboard (Angular + FastAPI)

Full-stack starter: user **signup/login** with a global **alert (toast)** feature and a
**dashboard of cards** behind JWT-protected routes.

```
project/
├── backend/     FastAPI + SQLAlchemy + JWT (SQLite for dev)
└── frontend/    Angular 17 (standalone components)
```

## Features

- Signup & login with hashed passwords (bcrypt) and JWT tokens
- Global alert/toast service — success, error, info, warning (auto-dismiss + manual close)
- Reactive-form validation with inline field errors
- Route guard + HTTP interceptor (auto-attaches token, bounces to login on 401)
- Dashboard with a responsive grid of stat cards, skeleton loading, refresh
- Control-room ("Grid Ops") dark theme

## Backend — run

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API runs at `http://localhost:8000` (docs at `/docs`). SQLite file `app.db` is auto-created.

Endpoints:
- `POST /auth/signup` — `{name, email, password}` → token + user
- `POST /auth/login`  — `{email, password}` → token + user
- `GET  /auth/me`     — current user (auth required)
- `GET  /dashboard/stats` — card data (auth required)

> Swap to PostgreSQL by editing `SQLALCHEMY_DATABASE_URL` in `backend/database.py`.
> Move `SECRET_KEY` in `backend/auth.py` to an env var before deploying.

## Frontend — run

```bash
cd frontend
npm install
npm start          # ng serve → http://localhost:4200
```

The frontend calls the API at `http://localhost:8000` (see `API` const in the services).
CORS in `backend/main.py` already allows `http://localhost:4200`.

## Quick test

1. Start backend (port 8000), then frontend (port 4200).
2. Open `http://localhost:4200` → redirected to **/login**.
3. Click **Create one**, sign up → success toast → lands on **/dashboard**.
4. Hit **Sign out**, then log back in.
