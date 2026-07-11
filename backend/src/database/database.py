from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from urllib.parse import quote_plus
import os

from config import get_setting

settings = get_setting()

PG_DB_URL = (
    f"postgresql://{settings.PG_DB_USER}:{quote_plus(settings.PG_DB_PASSWORD)}"
    f"@{settings.PG_DB_SERVER}:{settings.PG_DB_PORT}/{settings.PG_DATABASE}"
    f"?sslmode=require"
)

# NullPool is required on Vercel serverless — connection pooling across
# frozen/thawed instances causes broken connections.
_engine_kwargs = {
    "connect_args": {"options": "-c timezone=Asia/Kolkata -c search_path=public"},
    "echo": False,
}
if os.getenv("VERCEL"):
    _engine_kwargs["poolclass"] = NullPool


class Database:
    def __init__(self):
        self.database_url = PG_DB_URL
        self.engine = create_engine(PG_DB_URL, **_engine_kwargs)
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


Base = declarative_base(metadata=MetaData(schema="public"))

_tx_kwargs = {
    "connect_args": {"options": "-c timezone=Asia/Kolkata"},
    "echo": False,
}
if os.getenv("VERCEL"):
    _tx_kwargs["poolclass"] = NullPool

engine = create_engine(PG_DB_URL, **_tx_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_transaction_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
