from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/surveys", tags=["surveys"])

# ---------- CRUD опросов (админ) ----------

@router.get("/", response_model=list[schemas.SurveyOut])
def list_surveys(db: Session = Depends(get_db)):
    return db.query(models.Survey).all()


@router.get("/{survey_id}", response_model=schemas.SurveyOut)
def get_survey(survey_id: int, db: Session = Depends(get_db)):
    survey = db.get(models.Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


# ---------- отправка результатов ----------

@router.post("/{survey_id}/submit", response_model=schemas.SurveyResponseOut)
def submit(
    survey_id: int,
    payload: schemas.SurveySubmit,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    survey = db.get(models.Survey, survey_id)
    if not survey:
        raise HTTPException(404, "Survey not found")

    # 1. валидируем диапазоны
    answers_dict = {a.question_id: a.answer_value for a in payload.answers}
    total = sum(answers_dict.values())

    # 2. ищем рекомендацию
    recommendation = None
    for rng in survey.ranges:
        if rng.min_score <= total <= rng.max_score:
            recommendation = rng.message
            break

    response = models.SurveyResponse(
        survey_id=survey_id,
        user_id=current_user.id,
        respondent_name=payload.respondent_name,
        answers_raw=json.dumps(answers_dict),
        total_score=total,
        recommendation=recommendation,
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response
