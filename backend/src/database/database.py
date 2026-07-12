from contextlib import contextmanager
from urllib.parse import quote_plus

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Settings as settings

# ---------------------- DATABASE URL ----------------------

PG_DB_URL = (
    f"postgresql://{settings.PG_DB_USER}:"
    f"{quote_plus(settings.PG_DB_PASSWORD)}@"
    f"{settings.PG_DB_SERVER}:"
    f"{settings.PG_DB_PORT}/"
    f"{settings.PG_DATABASE}"
    f"?sslmode=require"
)

print("PG_DB_URL:", PG_DB_URL)

# ---------------------- ENGINE ----------------------

engine = create_engine(
    PG_DB_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base(
    metadata=MetaData(schema="public")
)

# ---------------------- DATABASE CLASS ----------------------

class Database:
    def __init__(self):
        self.engine = engine
        self.session = SessionLocal

    @contextmanager
    def connect(self):
        db = self.session()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

# ---------------------- DEPENDENCIES ----------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_transaction_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()