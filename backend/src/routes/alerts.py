from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from config import get_setting
from config import get_setting
from database.database import get_db
from helper import customhelper
from helper.sessionData import getSessionUserId
from modules.alerts.crud import get_manual_notification
from dependencies import tokenvalidation,is_readable
from modules.alerts.models import UserNotification

is_valid = [Depends(tokenvalidation),Depends(is_readable)]
routes = APIRouter(
    tags=["Alerts"],
    dependencies=is_valid
)
configObj = get_setting()

@routes.post("/alerts")
def get_alerts(db: Session = Depends(get_db), serviceRequest: Request = None):
    try:
        return get_manual_notification(db, serviceRequest)
    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)
    
@routes.get('/get_notifications')
def get_notifications(db: Session = Depends(get_db), serviceRequest: Request = None):
    try:
        user_id = getSessionUserId(serviceRequest)

        notifications = (
            db.query(UserNotification)
            .filter(
                UserNotification.user_id == user_id,
                UserNotification.is_active == True,
            )
            .order_by(UserNotification.created_at.desc())
            .limit(50)
            .all()
        )

        unread_count = (
            db.query(UserNotification)
            .filter(
                UserNotification.user_id == user_id,
                UserNotification.is_active == True,
                UserNotification.is_read == False,
            )
            .count()
        )

        data = [{
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.notification_type,
            "is_read": n.is_read,
            "date": n.notification_date.strftime('%d-%b-%Y %H:%M') if n.notification_date else None,
        } for n in notifications]

        return {"unread_count": unread_count, "notifications": data}

    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)


# ---- 2. Mark one as read ----
@routes.get('/mark_notification_read')
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), serviceRequest: Request = None):
    try:
        user_id = getSessionUserId(serviceRequest)
        notif = db.query(UserNotification).filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == user_id,
        ).first()

        if not notif:
            return customhelper.printCustmMsg(200, 'FALSE', 'Notification not found')

        notif.is_read = True
        db.commit()
        return customhelper.printCustmMsg(200, 'TRUE', 'Marked as read')
    except Exception as err:
        db.rollback()
        return customhelper.print_error_with_linenumebr(err)


# ---- 3. Mark all as read ----
@routes.get('/mark_all_notifications_read')
def mark_all_notifications_read(db: Session = Depends(get_db), serviceRequest: Request = None):
    try:
        user_id = getSessionUserId(serviceRequest)
        db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.is_read == False,
        ).update({UserNotification.is_read: True})
        db.commit()
        return customhelper.printCustmMsg(200, 'TRUE', 'All marked as read')
    except Exception as err:
        db.rollback()
        return customhelper.print_error_with_linenumebr(err)