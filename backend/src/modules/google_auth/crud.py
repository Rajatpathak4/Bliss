from datetime import datetime, timedelta
import uuid
from helper import customhelper
from helper.customhelper import create_access_token, bcrypt_context
from modules.login.models import Users, LoginTokens
from config import get_setting
import requests

configObj = get_setting()

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


def verify_google_token(token: str):
    try:
        response = requests.get(GOOGLE_TOKENINFO_URL, params={"id_token": token}, timeout=5)
        if response.status_code != 200:
            return None

        idinfo = response.json()

        if idinfo.get("aud") != configObj.GOOGLE_CLIENT_ID:
            print(f"[GOOGLE TOKEN] audience mismatch: {idinfo.get('aud')}")
            return None

        return idinfo
    except Exception as e:
        print(f"[GOOGLE TOKEN VERIFY FAILED]: {e}")
        return None


def google_login(db, token: str):
    idinfo = verify_google_token(token)
    if not idinfo:
        return customhelper.printCustmMsg(401, "FALSE", "Invalid Google token")

    email = idinfo["email"].lower()
    name = idinfo.get("name", email.split("@")[0])

    user = db.query(Users).filter(Users.email == email).first()

    if not user:
        random_password = bcrypt_context.hash(uuid.uuid4().hex)
        user = Users(name=name, email=email, password=random_password)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif user.is_deleted:
        user.is_deleted = False
        user.name = name
        db.commit()

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