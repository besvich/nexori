# app/config.py
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nexori.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here_change_me")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
