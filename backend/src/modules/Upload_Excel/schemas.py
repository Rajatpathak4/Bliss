from typing import Optional
from datetime import date
from pydantic import BaseModel

class UserExcelSchema(BaseModel):
    id: Optional[int] = None
    agent_code: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    family_code: Optional[str] = None
    policy_holder: Optional[str] = None
    policy_number: Optional[str] = None
    dob: Optional[date] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    agency_code: Optional[str] = None
    commecement_date: Optional[date] = None
    plan: Optional[int] = None    
    term: Optional[int] = None
    ppt: Optional[float] = None
    sum_assured: Optional[float] = None
    mode: Optional[str] = None
    fup_date: Optional[date] = None
    premium: Optional[float] = None
    nominee: Optional[str] = None