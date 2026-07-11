from functools import lru_cache
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _env(key: str, default: str = "") -> str:
    value = os.getenv(key)
    if value is None or not str(value).strip():
        return default
    return str(value).strip()


class Settings:
    def __init__(self):
        self.PG_DB_USER: str = _env("POSTGRES_USER", "postgres")
        self.PG_DB_PASSWORD: str = _env("POSTGRES_PASSWORD", "postgres")
        self.PG_DB_SERVER: str = _env("POSTGRES_SERVER", "localhost")
        self.PG_DB_PORT: str = _env("POSTGRES_PORT", "5432")
        self.PG_DATABASE: str = _env("POSTGRES_DB", "bliss")
        self.UPLOAD_PATH: str = "uploads/"
        self.doc_enable: str = _env("DOC_ENABLE", "True")
        self.SMTP_EMAIL: str = _env("SMTP_EMAIL", "")
        self.SMTP_APP_PASSWORD: str = _env("SMTP_APP_PASSWORD", "")
        self.SECRET_KEY: str = _env(
            "SECRET_KEY",
            "61729ba0e591d387b85851d34af9e33bcc6f8e4a74fba56ce9a62f75a34c5892",
        )
        self.ALGORITHM: str = _env("ALGORITHM", "HS256")


@lru_cache()
def get_setting():
    return Settings()
