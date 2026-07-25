from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from helper import customhelper
from modules.alerts.crud import create_fup_notifications
from config import get_setting

routes = APIRouter(tags=["Cronjob"])

configObj = get_setting()


@routes.get('/create_fup_notification')
def send_email_notification(x_cron_secret: str = Header(None), db: Session = Depends(get_db)):
    if x_cron_secret != configObj.CRON_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        response = create_fup_notifications(db)
        return response
    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)