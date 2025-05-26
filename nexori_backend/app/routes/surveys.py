from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import SessionLocal
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/surveys", tags=["surveys"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Создать опрос ---------- #
@router.post("/", response_model=schemas.SurveyOut, status_code=201)
def create_survey(
    survey: schemas.SurveyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Проверяем, что тест существует
    if not crud.get_test(db, survey.test_id):
        raise HTTPException(status_code=404, detail="Test not found")
    created = crud.create_survey(db, survey, owner_id=current_user.id)
    return created


# ---------- Получить список опросов ---------- #
@router.get("/", response_model=list[schemas.SurveyOut])
def read_surveys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role == "admin":
        return crud.get_surveys(db, skip, limit)
    return crud.get_surveys_by_owner(db, current_user.id, skip, limit)


# ---------- Получить один опрос ---------- #
@router.get("/{survey_id}", response_model=schemas.SurveyOut)
def read_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey["owner_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return survey


# ---------- Удалить опрос ---------- #
@router.delete("/{survey_id}", status_code=204)
def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey["owner_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.delete_survey(db, survey_id)


# ---------- Получить рекомендацию ---------- #
@router.get("/{survey_id}/recommendation", response_model=schemas.RecommendationOut)
def get_recommendation(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    survey = crud.get_survey(db, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey["owner_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    recommendation = crud.evaluate_survey(db, survey)
    return schemas.RecommendationOut(survey_id=survey_id, recommendation=recommendation)
