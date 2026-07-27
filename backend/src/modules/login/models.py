from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from database.database import Base
from sqlalchemy.orm import relationship


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
    theme = Column(String(10), default="light", nullable=False)
    profile = relationship("UserProfile", back_populates="user", uselist=False)
class LoginTokens(Base):
    __tablename__='token'
    __table_args__ = {'extend_existing': True}
    id=Column(Integer,primary_key=True)
    token=Column(String,nullable=False)
    user_id=Column(Integer,nullable=False)
    created_at=Column(DateTime,default=func.now())
    expires_at=Column(DateTime)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    phone_number = Column(String(15), nullable=True)
    role = Column(String(50), nullable=True)
    company = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("Users", back_populates="profile")
