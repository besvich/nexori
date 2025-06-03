# app/crud.py

from typing import List, Dict, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app import models, schemas


# --------------------------------------------
#  CRUD для User
# --------------------------------------------
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user_in: schemas.UserCreate, hashed_password: str) -> models.User:
    """
    Создаёт нового пользователя. Принимает уже захэшированный пароль.
    """
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        role="user",       # по умолчанию роль = user
        is_active=1
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str, verify_fn) -> Optional[models.User]:
    """
    Проверяет логин/пароль: 
    - verify_fn(plaintext, hashed) => True/False.
    - Возвращает пользователя, если пароль верный, иначе None.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_fn(password, user.hashed_password):
        return None
    return user


def update_user_role(db: Session, user_id: int, new_role: str) -> Optional[models.User]:
    """
    Изменяет роль пользователя (только админ).
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


# --------------------------------------------
#  CRUD для Survey (опрос)
# --------------------------------------------
def get_all_surveys(db: Session) -> List[models.Survey]:
    return db.query(models.Survey).all()


def get_survey(db: Session, survey_id: int) -> Optional[models.Survey]:
    return db.query(models.Survey).filter(models.Survey.id == survey_id).first()


def create_survey(db: Session, survey_in: schemas.SurveyCreate) -> models.Survey:
    """
    Создаёт новый опрос + связанные вопросы. Возвращает сохранённый Survey.
    """
    # 1) Сначала создаём сам опрос
    db_survey = models.Survey(
        title=survey_in.title,
        description=survey_in.description,
        created_at=datetime.utcnow()
    )
    db.add(db_survey)
    db.flush()  # синхронизируем, чтобы появился db_survey.id

    # 2) Создаём каждый вопрос
    for q in survey_in.questions:
        db_question = models.SurveyQuestion(
            text=q.text,
            min_value=q.min_value,
            max_value=q.max_value,
            survey_id=db_survey.id
        )
        db.add(db_question)

    db.commit()
    db.refresh(db_survey)
    return db_survey


def update_survey(
    db: Session, survey_id: int, survey_data: schemas.SurveyUpdate
) -> Optional[models.Survey]:
    """
    Обновляет поля опроса и/или перезаписывает вопросы.
    """
    db_survey = get_survey(db, survey_id)
    if not db_survey:
        return None

    # Обновляем title/description
    if survey_data.title is not None:
        db_survey.title = survey_data.title
    if survey_data.description is not None:
        db_survey.description = survey_data.description

    # Если пришли новые вопросы — удалить старые и добавить новые
    if survey_data.questions is not None:
        # Удаляем все связанные questions
        db.query(models.SurveyQuestion).filter(
            models.SurveyQuestion.survey_id == survey_id
        ).delete()
        # Добавляем новые
        for q in survey_data.questions:
            db_question = models.SurveyQuestion(
                text=q.text,
                min_value=q.min_value,
                max_value=q.max_value,
                survey_id=survey_id
            )
            db.add(db_question)

    db.commit()
    db.refresh(db_survey)
    return db_survey


def delete_survey(db: Session, survey_id: int) -> bool:
    """
    Удаляет опрос и все его вопросы. Возвращает True, если удалено, False, если не найден.
    """
    db_survey = get_survey(db, survey_id)
    if not db_survey:
        return False
    db.delete(db_survey)
    db.commit()
    return True


# --------------------------------------------
#  CRUD для SurveyResponse (ответы респондента)
# --------------------------------------------
def create_survey_response(
    db: Session,
    survey_id: int,
    respondent_name: str,
    answer_dict: Dict[int, int],
    total_score: int,
    recommendation: str
) -> models.SurveyResponse:
    """
    Сохраняет результаты ответа пользователя на опрос.
    - answer_dict: словарь {question_id: answer_value}.
    - total_score: сумма всех answer_value.
    - recommendation: строка-совет.
    """
    db_response = models.SurveyResponse(
        respondent_name=respondent_name,
        answers=str(answer_dict),  # сохраняем словарь как строку
        total_score=total_score,
        recommendation=recommendation,
        created_at=datetime.utcnow(),
        user_id=None,             # при необходимости можно добавить связь с user
        survey_id=survey_id
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response


def get_responses_for_survey(db: Session, survey_id: int) -> List[models.SurveyResponse]:
    """
    Возвращает список всех SurveyResponse по данному survey_id.
    """
    return db.query(models.SurveyResponse).filter(
        models.SurveyResponse.survey_id == survey_id
    ).all()


def get_response_by_id(db: Session, response_id: int) -> Optional[models.SurveyResponse]:
    """
    Возвращает один SurveyResponse по ID.
    """
    return db.query(models.SurveyResponse).filter(
        models.SurveyResponse.id == response_id
    ).first()


# --------------------------------------------
#  Здесь можно добавить любые вспомогательные функции,
#  необходимые для других роутов или аналитики.
# --------------------------------------------

