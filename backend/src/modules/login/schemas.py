from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class DashboardCard(BaseModel):
    title: str
    value: str
    delta: str        
    trend: str       
    icon: str         
    hint: str


class DashboardStats(BaseModel):
    greeting: str
    cards: list[DashboardCard]
