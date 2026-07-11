from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric
from database.database import Base


class UserExcel(Base):
    __tablename__ = "user_excel"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    agent_code = Column(String)
    from_date = Column(Date)
    to_date = Column(Date)
    family_code = Column(String)
    policy_holder = Column(String)
    policy_number = Column(String)
    dob = Column(Date)
    phone_number = Column(String)
    email = Column(String)
    address = Column(String)
    agency_code = Column(String)
    commecement_date = Column(Date)
    plan = Column(String)
    term = Column(Integer)
    ppt = Column(Integer)
    sum_assured = Column(Numeric)
    mode = Column(String)
    fup_date = Column(Date)
    premium = Column(Numeric)
    nominee = Column(String)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    user_id = Column(Integer, nullable=False) 