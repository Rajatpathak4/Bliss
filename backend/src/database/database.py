from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from urllib.parse import quote_plus

from config import Settings as settings
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

PG_DB_URL = Base_URL
print(PG_DB_URL,'PG_DB_URLPG_DB_URL')
class Database: 
    def __init__(self):
        self.database_url = PG_DB_URL
        self.engine = create_engine(PG_DB_URL,connect_args={"options": "-c timezone=Asia/Kolkata -c search_path=public"},echo=False)
        self.session = sessionmaker(bind=self.engine)
    
        @event.listens_for(self.engine, "connect")
        def connect(dbapi_connection, connection_record):
                print(f"[DB] New connection established. ID: {id(dbapi_connection)}")
                
        @event.listens_for(self.engine, "close")
        def close(dbapi_connection, connection_record):
            print(f"[DB] Connection closed. ID: {id(dbapi_connection)}")

    @contextmanager
    def connect(self):
        print("[DB] Creating session...")
        session = self.session()
        try:
            print("[DB] Session started.")
            yield session
            session.commit()
            print("[DB] Transaction committed.")
        except Exception as e:
            session.rollback()
            print(f"[DB] Transaction rolled back. Error: {e}")
            raise
        finally:
            session.close()
            print("[DB] Session closed.")

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