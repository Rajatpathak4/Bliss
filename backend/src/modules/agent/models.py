from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.database import Base


class PolicyCommission(Base):
    __tablename__ = "policy_commission"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("user_excel.id"), unique=True, nullable=False)
    commission_rate = Column(Numeric(5, 2), default=0)
    commission_status = Column(String(20), default="pending")   # pending / received
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())