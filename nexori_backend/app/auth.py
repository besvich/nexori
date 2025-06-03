# app/routes/auth.py

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # <-- именно так
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from app import models, schemas, crud
from app.dependencies import get_db, get_current_active_user
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["auth"])


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверяем, что логин свободен
    existing = crud.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = get_password_hash(user.password)
    new_user = crud.create_user(db, user, hashed)
    return new_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token", response_model=schemas.Token, summary="Получить токен (OAuth2)")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),  # <-- именно форма
    db: Session = Depends(get_db),
):
    """
    Эндпоинт для получения токена. Требует 'username' и 'password' в формате
    application/x-www-form-urlencoded. Возвращает в ответе JSON:
      { "access_token": "...", "token_type": "bearer", "role": "..." }
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
    }


@router.post("/register", response_model=schemas.UserOut, summary="Регистрация нового пользователя")
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя. Ожидает JSON:
      { "username": "...", "password": "...", "full_name": "...", "email": "..." }
    и возвращает данные нового пользователя (без пароля).
    """
    # Проверим, что юзер с таким именем не существует
    existing = crud.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует",
        )
    hashed_pw = pwd_context.hash(user_in.password)
    new_user = crud.create_user(db, user_in, hashed_pw)
    return new_user


@router.get("/me", response_model=schemas.UserOut, summary="Получить информацию о текущем пользователе")
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user
