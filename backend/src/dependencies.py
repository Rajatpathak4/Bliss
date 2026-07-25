
from fastapi import HTTPException, Header, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.database import get_db
from config import get_setting

from modules.login import models
from sqlalchemy import  func
from datetime import datetime, timedelta


config = get_setting()
ACCESS_TOKEN_EXPIRE_MINUTES = 300

auth_scheme = HTTPBearer()
def tokenvalidation(dbObj: Session = Depends(get_db), creds: HTTPAuthorizationCredentials = Depends(auth_scheme), request: Request = None):
    try:
        token = creds.credentials

        tokenRow = (
            dbObj.query(models.LoginTokens)
            .with_entities(models.Users.id, models.Users.name, models.Users.email, models.LoginTokens.token)
            .join(models.Users, models.LoginTokens.user_id == models.Users.id)
            .filter(
                models.LoginTokens.token == token,
                models.LoginTokens.expires_at >= datetime.now(),
            )
            .first()
        )

        if not tokenRow:
            raise HTTPException(status_code=401, detail="Session expired. Please login again.")

        request.session["userData"] = dict(tokenRow._mapping)
        return True   # koi update/refresh nahi — bas check karo aur aage badho

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="You are not authorised to access")
def is_readable(db: Session = Depends(get_db),serviceRequest:Request = None):
    try:
        return True
    except Exception as e:  # catches any exception
        print(e, 'exce')
        raise HTTPException(
            status_code=403,
            detail=str(e)) 
 

def is_writable(db: Session = Depends(get_db),serviceRequest:Request = None):
    try:
        return True
    except Exception as e:  # catches any exception
        print(e, 'write exce')
        return True