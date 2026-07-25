from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database.database import get_db
from helper import customhelper
from config import get_setting
from dependencies import is_readable, tokenvalidation
from modules.agent.crud import get_commission_summary, get_family_policies, set_commission_rate, update_commission_status


is_valid = [Depends(tokenvalidation),Depends(is_readable)]
routes = APIRouter(tags=["Agent"],dependencies=is_valid)

configObj = get_setting()


@routes.get("/family_code")
def get_family(policy_holder: Optional[str] = None, db: Session = Depends(get_db)):
    return get_family_policies(db, policy_holder)

@routes.get("/summary")
def summary(request: Request,agent_code: str = None,db: Session = Depends(get_db)):
    user_id = request.session["userData"]["id"]
    return get_commission_summary(db, user_id, agent_code)


@routes.put("/rate")
def update_rate(policy_id: int,rate: float,request: Request,db: Session = Depends(get_db)):
    return set_commission_rate(db, policy_id, rate)


@routes.put("/status")
def update_status(policy_id: int,status: str,request: Request,db: Session = Depends(get_db)):
    return update_commission_status(db, policy_id, status)