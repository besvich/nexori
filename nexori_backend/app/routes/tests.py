from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.dependencies import get_current_active_user, get_db

router = APIRouter(prefix="/tests", tags=["tests"])

# ---------- Admin-only: создать тест ---------- #
@router.post("/", response_model=schemas.TestOut, status_code=201)
def create_test(
    test: schemas.TestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    db_test = crud.create_test(db, test)
    return db_test


# ---------- Все пользователи: список тестов ---------- #
@router.get("/", response_model=List[schemas.TestOut])
def list_tests(db: Session = Depends(get_db)):
    return crud.list_tests(db)


# ---------- Получить один тест ---------- #
@router.get("/{test_id}", response_model=schemas.TestOut)
def get_test(test_id: int, db: Session = Depends(get_db)):
    db_test = crud.get_test(db, test_id)
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    return db_test


# ---------- Admin-only: обновить тест ---------- #
@router.put("/{test_id}", response_model=schemas.TestOut)
def update_test(
    test_id: int,
    test: schemas.TestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    db_test = crud.update_test(db, test_id, test)
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    return db_test


# ---------- Admin-only: удалить тест ---------- #
@router.delete("/{test_id}", status_code=204)
def delete_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    if not crud.delete_test(db, test_id):
        raise HTTPException(status_code=404, detail="Test not found")
    return {"ok": True}
