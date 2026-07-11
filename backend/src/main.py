import sys
import os

# Ensure `src/` is importable on Vercel (and locally).
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from functools import lru_cache
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from config import Settings

IS_VERCEL = bool(os.getenv("VERCEL"))


@lru_cache
def get_settings():
    return Settings()


origins = ["*"]

_docs_enabled = get_settings().doc_enable == "True"

app = FastAPI(
    description="Bliss portal api only",
    title="Bliss Data api's",
    redoc_url=None,
    docs_url="/docs" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
    dependencies=[Depends(get_settings)],
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().SECRET_KEY
    or "61729ba0e591d387b85851d34af9e33bcc6f8e4a74fba56ce9a62f75a34c5892",
    max_age=36000,
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "Bliss Data API"}


@app.get("/")
def index():
    if _docs_enabled:
        return RedirectResponse("/docs")
    return {"status": "ok", "service": "Bliss Data API"}


# Import routers after app exists so a partial import failure is easier to diagnose.
try:
    from routes import alerts, upload_excel, users, dashboard

    app.include_router(users.routes)
    app.include_router(dashboard.routes)
    app.include_router(upload_excel.routes)
    app.include_router(alerts.routes)
except Exception as exc:  # pragma: no cover - surfaced on Vercel logs
    import traceback

    _import_error = f"{type(exc).__name__}: {exc}"
    _import_trace = traceback.format_exc()
    print("ROUTER IMPORT FAILED:", _import_error)
    print(_import_trace)

    @app.get("/__import_error")
    def import_error():
        return JSONResponse(
            status_code=500,
            content={"error": _import_error, "traceback": _import_trace},
        )


# create_all / APScheduler are not safe on Vercel serverless.
if not IS_VERCEL:
    import modules.login.models as models
    from database.database import engine
    from apscheduler.schedulers.background import BackgroundScheduler
    from database.database import SessionLocal
    from modules.alerts.crud import create_fup_notifications

    models.Base.metadata.create_all(bind=engine)

    scheduler = BackgroundScheduler()

    def notification_scheduler():
        db = SessionLocal()
        try:
            print("IN Scheduler")
            create_fup_notifications(db)
        except Exception as e:
            print(f"Notification Scheduler Error: {e}")
        finally:
            db.close()

    @app.on_event("startup")
    def startup_event():
        scheduler.add_job(notification_scheduler, trigger="cron", hour=19, minute=29)
        scheduler.start()

    @app.on_event("shutdown")
    def shutdown_event():
        scheduler.shutdown()
        print("Shutting down scheduled tasks.")
