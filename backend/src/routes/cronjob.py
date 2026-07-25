from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from helper import customhelper
from modules.alerts.crud import create_fup_notifications

routes = APIRouter(tags=["Cronjob"])

@routes.get('/create_fup_notification')
def send_email_notification(db: Session = Depends(get_db)):
    try:
        response =  create_fup_notifications(db)
        return response
    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)