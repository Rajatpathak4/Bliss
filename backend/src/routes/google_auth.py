from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from modules.google_auth.crud import google_login
from modules.google_auth.schemas import GoogleLoginRequest


routes = APIRouter(tags=["Google_Auth"])

@routes.post("/google-login")
def google_login_route(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    return google_login(db, payload.token)