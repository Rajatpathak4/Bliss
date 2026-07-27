from datetime import datetime, timedelta
import uuid

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from helper import customhelper
from helper.customhelper import create_access_token, bcrypt_context
from modules.login.models import Users, LoginTokens
from config import get_setting

configObj = get_setting()


def verify_google_token(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), configObj.GOOGLE_CLIENT_ID
        )
        return idinfo
    except ValueError:
        return None


def google_login(db, token: str):
    idinfo = verify_google_token(token)
    if not idinfo:
        return customhelper.printCustmMsg(401, "FALSE", "Invalid Google token")

    email = idinfo["email"].lower()
    name = idinfo.get("name", email.split("@")[0])

    user = db.query(Users).filter(Users.email == email, Users.is_deleted == False).first()  # noqa: E712

    if not user:
        random_password = bcrypt_context.hash(uuid.uuid4().hex)
        user = Users(name=name, email=email, password=random_password)
        db.add(user)
        db.commit()
        db.refresh(user)

    now = datetime.now()
    expiry_minutes = 180
    access_token = create_access_token(user.email, user.id, timedelta(minutes=expiry_minutes))

    db.query(LoginTokens).filter(LoginTokens.user_id == user.id, LoginTokens.expires_at < now).delete(synchronize_session=False)
    db.add(LoginTokens(token=access_token, user_id=user.id, created_at=now,
                        expires_at=now + timedelta(minutes=expiry_minutes)))
    db.commit()

    user_dict = {
        "uid": user.id,
        "name": user.name,
        "email": user.email,
        "token": access_token,
        "redirectUrl": "/dashboard",
    }
    return customhelper.printCustmMsg(200, "TRUE", "Google login successful", user_dict)