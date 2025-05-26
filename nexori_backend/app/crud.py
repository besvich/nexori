from sqlalchemy.orm import Session
from app import models, schemas
import json

# ---------- Tests ---------- #
def create_test(db: Session, test: schemas.TestCreate):
    db_test = models.Test(title=test.title, description=test.description)
    db.add(db_test)
    db.flush()  # получить id, чтобы добавить вопросы/результаты

    # Добавляем вопросы
    for q in test.questions:
        db_question = models.TestQuestion(
            test_id=db_test.id,
            text=q.text,
            options=json.dumps(q.options) if q.options else None,
            weight=q.weight
        )
        db.add(db_question)

    # Добавляем диапазоны результатов
    for r in test.results:
        db_result = models.TestResult(
            test_id=db_test.id,
            min_score=r.min_score,
            max_score=r.max_score,
            recommendation=r.recommendation
        )
        db.add(db_result)

    db.commit()
    db.refresh(db_test)
    return db_test

def get_test(db: Session, test_id: int):
    return db.query(models.Test).filter(models.Test.id == test_id).first()

def list_tests(db: Session):
    return db.query(models.Test).all()

def update_test(db: Session, test_id: int, test: schemas.TestCreate):
    db_test = db.query(models.Test).filter(models.Test.id == test_id).first()
    if not db_test:
        return None
    
    # Обновляем основную информацию
    db_test.title = test.title
    db_test.description = test.description
    
    # Удаляем старые вопросы и результаты
    db.query(models.TestQuestion).filter(models.TestQuestion.test_id == test_id).delete()
    db.query(models.TestResult).filter(models.TestResult.test_id == test_id).delete()
    
    # Добавляем новые вопросы
    for q in test.questions:
        db_question = models.TestQuestion(
            test_id=test_id,
            text=q.text,
            options=json.dumps(q.options) if q.options else None,
            weight=q.weight
        )
        db.add(db_question)

    # Добавляем новые диапазоны результатов
    for r in test.results:
        db_result = models.TestResult(
            test_id=test_id,
            min_score=r.min_score,
            max_score=r.max_score,
            recommendation=r.recommendation
        )
        db.add(db_result)

    db.commit()
    db.refresh(db_test)
    return db_test

def delete_test(db: Session, test_id: int):
    db_test = db.query(models.Test).filter(models.Test.id == test_id).first()
    if not db_test:
        return False
    db.delete(db_test)
    db.commit()
    return True

# ---------- Surveys ---------- #
def convert_survey(db_survey: models.Survey):
    answers_dict = json.loads(db_survey.answers) if db_survey.answers else {}
    return {
        "id": db_survey.id,
        "respondent_name": db_survey.respondent_name,
        "answers": answers_dict,
        "created_at": db_survey.created_at,
        "owner_id": db_survey.owner_id,
        "test_id": db_survey.test_id
    }

def create_survey(db: Session, survey: schemas.SurveyCreate, owner_id: int):
    db_survey = models.Survey(
        respondent_name=survey.respondent_name,
        answers=json.dumps(survey.answers),
        owner_id=owner_id,
        test_id=survey.test_id
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return convert_survey(db_survey)

def get_survey(db: Session, survey_id: int):
    s = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    return convert_survey(s) if s else None

def get_surveys(db: Session, skip=0, limit=100):
    surveys = db.query(models.Survey).offset(skip).limit(limit).all()
    return [convert_survey(s) for s in surveys]

def get_surveys_by_owner(db: Session, owner_id: int, skip=0, limit=100):
    surveys = (db.query(models.Survey)
                 .filter(models.Survey.owner_id == owner_id)
                 .offset(skip).limit(limit).all())
    return [convert_survey(s) for s in surveys]

# ---------- Recommendation (rule-based) ---------- #
def evaluate_survey(db: Session, survey_dict: dict):
    """
    Находим тест, считаем суммарный балл (ответ * weight),
    подбираем рекомендацию из таблицы диапазонов.
    """
    test = db.query(models.Test).get(survey_dict["test_id"])
    if not test:
        return "Тест не найден"

    # словарь для быстрого доступа к весу вопроса
    weights = {str(q.id): q.weight for q in test.questions}
    total = 0
    for q_id, ans in survey_dict["answers"].items():
        total += int(ans) * weights.get(str(q_id), 1)

    # ищем диапазон
    for r in test.results:
        if r.min_score <= total <= r.max_score:
            return r.recommendation
    return "Нет подходящей рекомендации"

# ---------- Users ---------- #
def get_user_by_username(db: Session, username: str):
    """Вернуть пользователя по имени-логину или None, если не найден."""
    return (
        db.query(models.User)
        .filter(models.User.username == username)
        .first()
    )
