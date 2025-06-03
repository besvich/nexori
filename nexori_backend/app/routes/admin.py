# app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

def admin_required(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user

# ---------- управление опросами ----------
@router.post("/surveys", response_model=schemas.SurveyOut, status_code=201)
def create_survey(
    survey_in: schemas.SurveyCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(admin_required),
):
    survey = models.Survey(
        title=survey_in.title,
        description=survey_in.description,
        questions=[
            models.SurveyQuestion(**q.model_dump()) for q in survey_in.questions
        ],
        ranges=[
            models.SurveyResultRange(**r.model_dump()) for r in survey_in.ranges
        ],
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey

@router.put("/surveys/{survey_id}", response_model=schemas.SurveyOut)
def update_survey(
    survey_id: int,
    patch: schemas.SurveyUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(admin_required),
):
    survey = db.get(models.Survey, survey_id)
    if not survey:
        raise HTTPException(404, "Survey not found")

    if patch.title is not None:
        survey.title = patch.title
    if patch.description is not None:
        survey.description = patch.description

    if patch.questions is not None:
        survey.questions.clear()
        survey.questions.extend(
            models.SurveyQuestion(**q.model_dump()) for q in patch.questions
        )
    if patch.ranges is not None:
        survey.ranges.clear()
        survey.ranges.extend(
            models.SurveyResultRange(**r.model_dump()) for r in patch.ranges
        )

    db.commit()
    db.refresh(survey)
    return survey

@router.delete("/surveys/{survey_id}", status_code=204)
def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(admin_required),
):
    survey = db.get(models.Survey, survey_id)
    if not survey:
        raise HTTPException(404, "Survey not found")
    db.delete(survey)
    db.commit()
