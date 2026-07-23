import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functools import lru_cache

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from apscheduler.schedulers.background import BackgroundScheduler

from config import Settings
from database.database import engine, SessionLocal
import modules.login.models as models
from modules.alerts.crud import create_fup_notifications

from routes import alerts, upload_excel, users, dashboard

models.Base.metadata.create_all(bind=engine)


@lru_cache
def get_settings():
    return Settings()


app = FastAPI(
    title="Bliss Data API",
    description="Bliss Portal API",
    dependencies=[Depends(get_settings)],
    openapi_url="/openapi.json" if get_settings().doc_enable == "True" else None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

# ------------------ CORS ------------------

origins = [
    "http://localhost:4200",
    "https://bliss-dun-six.vercel.app",
    "https://bliss-vnts.vercel.app",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Session ------------------

app.add_middleware(
    SessionMiddleware,
    secret_key="61729ba0e591d387b85851d34af9e33bcc6f8e4a74fba56ce9a62f75a34c5892",
    max_age=36000,
)

# ------------------ Routers ------------------

app.include_router(users.routes)
app.include_router(dashboard.routes)
app.include_router(upload_excel.routes)
app.include_router(alerts.routes)

# ------------------ Root ------------------

@app.get("/")
def root():
    return RedirectResponse("/docs")

# ------------------ Scheduler ------------------

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
    if not scheduler.running:
        scheduler.add_job(
            notification_scheduler,
            trigger="cron",
            hour=8,
            minute=0,
            id="notification_scheduler",
            replace_existing=True,
        )
        scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()