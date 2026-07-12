from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from urllib.parse import quote_plus

from config import Settings as settings

PG_DB_URL = (
    f"postgresql://{settings.PG_DB_USER}:"
    f"{quote_plus(settings.PG_DB_PASSWORD)}@"
    f"{settings.PG_DB_SERVER}:"
    f"{settings.PG_DB_PORT}/"
    f"{settings.PG_DATABASE}?sslmode=require"
)

print("PG_DB_URL:", PG_DB_URL)

class Database:
    def __init__(self):
        self.database_url = PG_DB_URL
        self.engine = create_engine(
            PG_DB_URL,
            echo=False
        )
        self.session = sessionmaker(bind=self.engine)

    @contextmanager
    def connect(self):
        session = self.session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def get_db():
    with Database().connect() as db_session:
        yield db_session


Base = declarative_base(metadata=MetaData(schema="public"))

# -------- SECOND DB FOR TRANSACTION ---------------------------------------

engine = create_engine(
    PG_DB_URL,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_transaction_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()