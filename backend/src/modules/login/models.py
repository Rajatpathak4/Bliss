from sqlalchemy import Boolean, Column, Integer, String, DateTime, func
from database.database import Base


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, default=False)

class LoginTokens(Base):
    __tablename__='token'
    __table_args__ = {'extend_existing': True}
    id=Column(Integer,primary_key=True)
    token=Column(String,nullable=False)
    user_id=Column(Integer,nullable=False)
    created_at=Column(DateTime,default=func.now())
    expires_at=Column(DateTime)