from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database.database import get_db
from helper import customhelper
from config import get_setting
from dependencies import is_readable, tokenvalidation
from modules.agent.crud import get_family_policies


is_valid = [Depends(tokenvalidation),Depends(is_readable)]
routes = APIRouter(tags=["Agent"],dependencies=is_valid)

configObj = get_setting()


@routes.get("/family_code")
def get_family(policy_holder: Optional[str] = None, db: Session = Depends(get_db)):
    return get_family_policies(db, policy_holder)