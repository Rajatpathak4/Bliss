import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from functools import lru_cache
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from config import Settings
import modules.login.models as models
from database.database import engine
from routes import alerts, upload_excel, users, dashboard
from starlette.middleware.sessions import SessionMiddleware

IS_VERCEL = bool(os.getenv("VERCEL"))


@lru_cache
def get_settings():
    return Settings()


origins = ["*"]

app = FastAPI(
    description="Bliss portal api only",
    title="Bliss Data api's",
    redoc_url=None,
    docs_url="/docs" if get_settings().doc_enable == "True" else None,
    openapi_url="/openapi.json" if get_settings().doc_enable == "True" else None,
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

app.include_router(users.routes)
app.include_router(dashboard.routes)
app.include_router(upload_excel.routes)
app.include_router(alerts.routes)

app.add_middleware(
    SessionMiddleware,
    secret_key="61729ba0e591d387b85851d34af9e33bcc6f8e4a74fba56ce9a62f75a34c5892",
    max_age=36000,
)


@app.get("/")
def index():
    if get_settings().doc_enable == "True":
        return RedirectResponse("/docs")
    return {"status": "ok", "service": "Bliss Data API"}


# create_all / APScheduler are not safe on Vercel cold starts.
# Use yoyo migrations for schema; run the notification job via cron elsewhere.
if not IS_VERCEL:
    models.Base.metadata.create_all(bind=engine)

    from apscheduler.schedulers.background import BackgroundScheduler
    from database.database import SessionLocal
    from modules.alerts.crud import create_fup_notifications

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
