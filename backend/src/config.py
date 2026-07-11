from functools import lru_cache
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _env(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None or not str(value).strip():
        raise RuntimeError(
            f"Missing required environment variable: {key}. "
            "Set it in the Vercel project Environment Variables."
        )
    return str(value).strip()


class Settings:
    def __init__(self):
        self.PG_DB_USER: str = _env("POSTGRES_USER")
        self.PG_DB_PASSWORD: str = _env("POSTGRES_PASSWORD")
        self.PG_DB_SERVER: str = _env("POSTGRES_SERVER")
        self.PG_DB_PORT: str = _env("POSTGRES_PORT")
        self.PG_DATABASE: str = _env("POSTGRES_DB")
        self.UPLOAD_PATH: str = "uploads/"
        self.doc_enable: str = _env("DOC_ENABLE", "False")
        self.SMTP_EMAIL: str = _env("SMTP_EMAIL")
        self.SMTP_APP_PASSWORD: str = _env("SMTP_APP_PASSWORD")
        self.SECRET_KEY: str = _env("SECRET_KEY")
        self.ALGORITHM: str = _env("ALGORITHM", "HS256")


@lru_cache()
def get_setting():
    return Settings()
