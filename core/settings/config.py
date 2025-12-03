import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_HOST = os.getenv("DATABASE_HOST", "")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "")
    DATABASE_USER = os.getenv("DATABASE_USER", "")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    SECRET_ENTRY_PASSWORD = os.getenv("SECRET_ENTRY_PASSWORD", "")