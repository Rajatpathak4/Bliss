from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from urllib.parse import quote_plus

from config import Settings as settings
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

PG_DB_URL = f"postgresql://{settings.PG_DB_USER}:{quote_plus(settings.PG_DB_PASSWORD)}@{settings.PG_DB_SERVER}:{settings.PG_DB_PORT}/{settings.PG_DATABASE}?sslmode=require"
class Database: 
    def __init__(self):
        self.database_url = PG_DB_URL
        self.engine = create_engine(PG_DB_URL,connect_args={"options": "-c timezone=Asia/Kolkata -c search_path=public"},echo=False)
        self.session = sessionmaker(bind=self.engine)
      
    @contextmanager
    def connect(self):
        session = self.session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

def get_db():
    with Database().connect() as db_session:
        yield db_session

Base = declarative_base(metadata=MetaData(schema='public'))

#-------- SECOND DB FOR TRANSACTION ---------------------------------------

engine = create_engine(PG_DB_URL,connect_args={"options": "-c timezone=Asia/Kolkata -c search_path=public"},echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_transaction_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()