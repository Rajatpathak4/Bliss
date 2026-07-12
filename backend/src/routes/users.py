from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from helper import customhelper
from helper.sessionData import getSessionUserId
from modules.login.crud import user_login
import modules.login.models as models
import modules.login.schemas as schemas
import authentication.auth as auth
from database.database import get_db

routes = APIRouter(prefix="/auth", tags=["auth"])


@routes.post("/signup", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Users).filter(models.Users.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user =models.Users(
        name=payload.name,
        email=payload.email,
        password=auth.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}

@routes.post("/login")
def login(user_request: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    customhelper.do_nothing(request)
    return user_login(user_request, db)

@routes.get("/me", response_model=schemas.UserOut)
def me(current:models.Users = Depends(auth.get_current_user)):
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