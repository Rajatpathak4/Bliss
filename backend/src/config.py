from functools import lru_cache
import os
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Settings():
    PG_DB_USER: str = os.getenv("POSTGRES_USER").strip()
    PG_DB_PASSWORD = os.getenv("POSTGRES_PASSWORD").strip()
    PG_DB_SERVER: str = os.getenv("POSTGRES_SERVER").strip()
    PG_DB_PORT: str = os.getenv("POSTGRES_PORT").strip()
    PG_DATABASE: str = os.getenv("POSTGRES_DB").strip()
    UPLOAD_PATH:str= 'uploads/'
    doc_enable:str=os.getenv('DOC_ENABLE').strip()
    SMTP_EMAIL: str = os.getenv('SMTP_EMAIL').strip()
    SMTP_APP_PASSWORD : str = os.getenv('SMTP_APP_PASSWORD').strip()
    # Token
    SECRET_KEY: str = os.getenv("SECRET_KEY").strip()
    ALGORITHM: str = os.getenv("ALGORITHM").strip()

    CLOUDINARY_CLOUD_NAME: str =  os.getenv("CLOUDINARY_CLOUD_NAME").strip()
    CLOUDINARY_API_KEY: str =  os.getenv("CLOUDINARY_API_KEY").strip()
    CLOUDINARY_API_SECRET: str =  os.getenv("CLOUDINARY_API_SECRET").strip()

@lru_cache()
def get_setting():
    return Settings()
