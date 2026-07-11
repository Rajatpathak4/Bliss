from datetime import datetime
from sqlalchemy import Boolean, Column, String, Integer, DateTime, func
from database.database import Base
from fastapi import Request, Depends, FastAPI
from sqlalchemy.orm import Session


class UserNotification(Base):
    __tablename__ = "bell_alerts"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_excel_id = Column(Integer, nullable=False)
    notification_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    notification_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)