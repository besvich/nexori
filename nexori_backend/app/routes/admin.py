# app/routes/admin.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models, crud          # <-- импорт schemas обязательно!
from app.database import SessionLocal
from app.dependencies import get_current_active_user

router = APIRouter()

# Зависимость для получения БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/users",
    response_model=List[schemas.UserOut],       # Используем List[schemas.UserOut]
    summary="Список всех пользователей (админы)"
)
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Проверяем, что current_user — админ
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )
    return db.query(models.User).all()

@router.patch(
    "/users/{user_id}/role",
    response_model=schemas.UserOut,
    summary="Установить роль пользователю (админы)"
)
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user
