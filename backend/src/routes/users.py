from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from helper import customhelper
from helper.sessionData import getSessionUserId
from modules.login.crud import update_auth_token, user_login
import modules.login.models as models
import modules.login.schemas as schemas
import authentication.auth as auth
from database.database import get_db

routes = APIRouter(prefix="/auth", tags=["auth"])


@routes.post("/signup", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Users).filter(models.Users.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=200, detail="Email already registered")

    user = models.Users(
        name=payload.name,
        email=payload.email,
        password=auth.hash_password(payload.password),
        theme='light',
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id)})

    db.add(models.LoginTokens(
        token=token,
        user_id=user.id,
        expires_at=datetime.now() + timedelta(minutes=180),
    ))
    db.commit()

    return {"access_token": token, "token_type": "bearer", "user": user, "theme": user.theme}


@routes.post("/login")
def login(user_request: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    customhelper.do_nothing(request)
    return user_login(user_request, db)


@routes.get("/me", response_model=schemas.UserOut)
def me(current: models.Users = Depends(auth.get_current_user)):
    return current


@routes.get("/logout")
def logout(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.LoginTokens)\
        .filter(models.LoginTokens.user_id == user_id)\
        .first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.query(models.LoginTokens)\
        .filter(models.LoginTokens.user_id == user_id)\
        .delete(synchronize_session=False)
    db.commit()
    return {"message": "Logout successful"}


@routes.post("/re-login")
def update_token(userrequest: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    return update_auth_token(userrequest, db)


@routes.post("/update-theme")
def update_theme(user_id: int, payload: dict, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.theme = payload.get("theme")
    db.commit()
    return customhelper.printCustmMsg(200, "TRUE", "Theme updated")