from fastapi import Request, Depends, FastAPI
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from sqlalchemy import func
from config import get_setting
from helper.sessionData import getSessionUserId
from helper import customhelper
from modules.Upload_Excel.models import UserExcel
from modules.alerts.models import UserNotification
from modules.login.models import Users  # confirm karo ye path/naam sahi hai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

configObj = get_setting()

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

            if policy.email:
                owner = db.query(Users).filter(Users.id == policy.user_id).first()
                sender_name = owner.name if owner and owner.name else "LIC Tracker"

                subject = f"Premium Due Reminder — Policy #{policy.policy_number} (Due {fup_str})"

                body = f"""
                <div style="font-family:Arial,sans-serif;color:#eaf7f1;background:#0c1e18;padding:28px;border-radius:12px;">
                  <div style="background:linear-gradient(135deg,#10b981,#0c1e18);padding:2px;border-radius:10px;display:inline-block;margin-bottom:20px;">
                    <div style="background:#0c1e18;border-radius:9px;padding:10px 16px;">
                      <span style="color:#34d399;font-weight:800;font-size:15px;">LIC Tracker</span>
                    </div>
                  </div>
                  <h2 style="color:#34d399;margin:0 0 12px;">Premium Due Reminder</h2>
                  <p style="margin:0 0 10px;">Dear {policy.policy_holder or 'Customer'},</p>
                  <p style="margin:0 0 10px;">This is a reminder that your policy
                     <b style="color:#eaf7f1;">{policy.policy_number}</b> has a premium due on
                     <b style="color:#eaf7f1;">{fup_str}</b>.</p>
                  <p style="margin:0 0 16px;">Please make the payment before the due date to keep your
                     policy active.</p>
                  <hr style="border:none;border-top:1px solid #1f3d33;margin:20px 0;">
                  <p style="color:#8bb3a1;font-size:13px;margin:0;">— {sender_name}</p>
                </div>
                """
                send_email(policy.email, subject, body, sender_name=sender_name)

        db.commit()

    except Exception as err:
        db.rollback()
        return customhelper.print_error_with_linenumebr(err)
def get_manual_notification(db, serviceRequest):
    try:
        user_id = getSessionUserId(serviceRequest)
        notifications = db.query(UserNotification).filter(UserNotification.user_id == user_id, UserNotification.is_active == True).order_by(UserNotification.created_at.desc()).all()
        return customhelper.printCustmMsg(200, "TRUE", "Notifications fetched successfully", notifications)
    except Exception as err:
        return customhelper.print_error_with_linenumebr(err)

def send_email(to_email: str, subject: str, body_html: str, sender_name: str = "LIC Tracker") -> bool:
    try:
        sender = configObj.SMTP_EMAIL
        password = configObj.SMTP_APP_PASSWORD

        print(f"[EMAIL] trying to send to {to_email} from {sender}")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{sender_name} <{sender}>"
        msg["To"] = to_email
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())

        print(f"[EMAIL] SUCCESS sent to {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL] failed to {to_email}: {e}")
        traceback.print_exc()
        return False