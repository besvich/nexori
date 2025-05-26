# app/routes/analytics.py
import json
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/surveys", summary="Аналитика по опросам")
def get_surveys_analytics(db: Session = Depends(get_db)):
    surveys = crud.get_surveys(db=db)
    if not surveys:
        raise HTTPException(status_code=404, detail="No surveys found")
    
    aggregated = {}
    distribution = {}
    for survey in surveys:
        try:
            answers = json.loads(survey.answers)
        except Exception:
            continue
        for question, score in answers.items():
            if question not in aggregated:
                aggregated[question] = {'total': 0, 'count': 0, 'min': score, 'max': score}
                distribution[question] = defaultdict(int)
            aggregated[question]['total'] += score
            aggregated[question]['count'] += 1
            aggregated[question]['min'] = min(aggregated[question]['min'], score)
            aggregated[question]['max'] = max(aggregated[question]['max'], score)
            distribution[question][score] += 1

    analytics = {}
    for question, data in aggregated.items():
        avg = data['total'] / data['count'] if data['count'] > 0 else 0
        analytics[question] = {
            'average': avg,
            'min': data['min'],
            'max': data['max'],
            'count': data['count'],
            'distribution': dict(distribution[question])
        }
    return analytics
