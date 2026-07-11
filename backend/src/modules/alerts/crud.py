from fastapi import Request, Depends, FastAPI
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from sqlalchemy import func
from config import get_setting
from helper.sessionData import getSessionUserId
from helper import customhelper
from modules.Upload_Excel.models import UserExcel
from modules.alerts.models import UserNotification
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

configObj =get_setting()

def create_fup_notifications(db):
    try:
        today = date.today()
        end_date = today + timedelta(days=7)

        policies = db.query(UserExcel).filter(
            UserExcel.is_deleted == False,
            UserExcel.fup_date >= today,
            UserExcel.fup_date <= end_date
        ).all()

        for policy in policies:
            exists = db.query(UserNotification).filter(
                UserNotification.user_id == policy.user_id,
                UserNotification.user_excel_id == policy.id,
                UserNotification.notification_type == "FUP_REMINDER",
                func.date(UserNotification.notification_date) == today
            ).first()

            if exists:
                continue

            fup_str = policy.fup_date.strftime('%d-%b-%Y')
            msg = f"Policy {policy.policy_number} premium is due on {fup_str}"

            notification = UserNotification(
                user_id=policy.user_id,
                user_excel_id=policy.id,
                notification_type="FUP_REMINDER",
                title="Premium Due Reminder",
                message=msg,
                notification_date=datetime.now(),
                is_read=False,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(notification)

            # ---- send email if policy has an email ----
            if policy.email:
                body = f"""
                <div style="font-family:Arial,sans-serif;color:#0f172a;">
                  <h2 style="color:#2563eb;">Premium Due Reminder</h2>
                  <p>Dear {policy.policy_holder or 'Customer'},</p>
                  <p>This is a reminder that your policy
                     <b>{policy.policy_number}</b> has a premium due on
                     <b>{fup_str}</b>.</p>
                  <p>Please make the payment before the due date to keep your
                     policy active.</p>
                  <br>
                  <p style="color:#64748b;font-size:13px;">— NexAdmin Team</p>
                </div>
                """
                send_email(policy.email, "Premium Due Reminder", body)

        db.commit()

    except Exception as err:
        db.rollback()
        return customhelper.print_error_with_linenumebr(err)

def get_manual_notification(db, serviceRequest):
    try:
        user_id = getSessionUserId(serviceRequest)
        notifications = db.query(UserNotification).filter(UserNotification.user_id == user_id,UserNotification.is_active == True).order_by(UserNotification.created_at.desc()).all()
        return customhelper.printCustmMsg( 200, "TRUE", "Notifications fetched successfully", notifications)
    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)
    
def send_email(to_email: str, subject: str, body_html: str) -> bool:
    try:
        sender = configObj.SMTP_EMAIL
        password = configObj.SMTP_APP_PASSWORD

        print(f"[EMAIL] trying to send to {to_email} from {sender}")   # debug

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())

        print(f"[EMAIL] SUCCESS sent to {to_email}")                   # debug
        return True
    except Exception as e:
        print(f"[EMAIL] failed to {to_email}: {e}")
        return False