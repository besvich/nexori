# app/routes/surveys.py

from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app import schemas, models, crud
from app.dependencies import get_current_active_user  # если нужен авторизованный доступ для некоторых эндпоинтов
from app.database import SessionLocal

router = APIRouter(
    prefix="/surveys",
    tags=["surveys"],
)


def get_db():
    """
    Зависимость для получения сессии БД.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schemas.SurveyOut], summary="Список всех опросов (краткие данные)")
def list_surveys(
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(get_current_active_user)
):
    """
    Возвращает список всех опросов.
    Поля: id, title, description, created_at, пустой список questions (если нужно, можно убрать).
    """
    surveys = db.query(models.Survey).all()
    return surveys


@router.get("/{survey_id}", response_model=schemas.SurveyOut, summary="Получить опрос по ID (с вопросами)")
def get_survey_by_id(
    survey_id: int,
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(get_current_active_user)
):
    """
    Возвращает полный объект опроса по ID, включая questions.
    """
    survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Опрос не найден")
    return survey


@router.post(
    "/",
    response_model=schemas.SurveyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый опрос (только админ)"
)
def create_survey(
    survey_in: schemas.SurveyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Создание нового опроса. Только роль 'admin' может создавать.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    # Создаём сам объект Survey
    db_survey = models.Survey(
        title=survey_in.title,
        description=survey_in.description,
        created_at=datetime.utcnow()
    )
    db.add(db_survey)
    db.flush()  # присвоит db_survey.id

    # Создаём связанные вопросы
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


@router.put(
    "/{survey_id}",
    response_model=schemas.SurveyOut,
    summary="Обновить параметры опроса (только админ)"
)
def update_survey(
    survey_id: int,
    survey_data: schemas.SurveyUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Обновление опроса: title/description/questions. Только админ.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    db_survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if not db_survey:
        raise HTTPException(status_code=404, detail="Опрос не найден")

    # Обновляем title/description, если переданы
    if survey_data.title is not None:
        db_survey.title = survey_data.title
    if survey_data.description is not None:
        db_survey.description = survey_data.description

    # Перезапись вопросов
    if survey_data.questions is not None:
        # удаляем старые вопросы
        db.query(models.SurveyQuestion).filter(models.SurveyQuestion.survey_id == survey_id).delete()
        # добавляем новые
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


@router.delete(
    "/{survey_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить опрос (только админ)"
)
def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Удаление опроса (и всех его вопросов). Только админ.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    db_survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if not db_survey:
        raise HTTPException(status_code=404, detail="Опрос не найден")

    db.delete(db_survey)
    db.commit()
    return None  # при 204 — без тела


@router.post(
    "/{survey_id}/responses",
    response_model=schemas.SurveyResponseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Отправить ответы на опрос"
)
def submit_survey(
    survey_id: int,
    submission: schemas.SurveySubmit,
    db: Session = Depends(get_db)
):
    """
    Пользователь отправляет ответы на опрос:
    - Вычисляем total_score = сумма всех answer_value.
    - Находим подходящую recommendation (логика ваша).
    - Сохраняем в таблицу SurveyResponse.
    - Возвращаем SurveyResponseOut.
    """

    # 1) проверим, что опрос существует:
    db_survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if not db_survey:
        raise HTTPException(status_code=404, detail="Опрос не найден")

    # 2) вычислим суммарный балл:
    total = 0
    answer_dict: Dict[int, int] = {}
    for ans in submission.answers:
        # проверяем диапазон ans.answer_value входит ли в [min_value, max_value] вопроса
        db_question = db.query(models.SurveyQuestion).filter(
            models.SurveyQuestion.id == ans.question_id,
            models.SurveyQuestion.survey_id == survey_id
        ).first()
        if not db_question:
            raise HTTPException(status_code=400, detail=f"Вопрос с ID={ans.question_id} не найден в этом опросе")

        if not (db_question.min_value <= ans.answer_value <= db_question.max_value):
            raise HTTPException(
                status_code=400,
                detail=f"Значение {ans.answer_value} вне диапазона [{db_question.min_value}, {db_question.max_value}]"
            )

        total += ans.answer_value
        answer_dict[ans.question_id] = ans.answer_value

    # 3) определяем recommendation для total (пример: если total < 10 — "Рекомендация A", иначе "Рекомендация B")
    #    Здесь вы можете подставить свою логику; я приведу простой пример:
    if total < 10:
        rec = "Вам стоит обратить внимание на гуманитарные направления."
    elif total < 20:
        rec = "Вам подойдут технические специальности."
    else:
        rec = "Вам стоит рассмотреть математические и научные специальности."

    # 4) Сохраняем в базу:
    from app.models import SurveyResponse  # импорт внутри функции, чтобы избежать циклических зависимостей
    db_response = SurveyResponse(
        respondent_name=submission.respondent_name,
        # Сохраняем словарь как JSON-строку; если у вас стоит колонка JSON, можно напрямую
        answers=str(answer_dict),
        total_score=total,
        recommendation=rec,
        created_at=datetime.utcnow(),
        user_id=None,  # если сохраняете связь с пользователем, заполните тут
        survey_id=survey_id
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)

    # 5) Формируем выходные данные (SurveyResponseOut ждёт answers как Dict[int, int], поэтому преобразуем)
    return schemas.SurveyResponseOut(
        id=db_response.id,
        respondent_name=db_response.respondent_name,
        answers=answer_dict,
        total_score=db_response.total_score,
        recommendation=db_response.recommendation,
        created_at=db_response.created_at
    )


@router.get(
    "/{survey_id}/responses",
    response_model=List[schemas.SurveyResponseOut],
    summary="Получить список всех ответов на опрос (только админ)"
)
def get_all_responses(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Получить все ответы (SurveyResponse) данного опроса. Только админ.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    responses = db.query(models.SurveyResponse).filter(
        models.SurveyResponse.survey_id == survey_id
    ).all()

    out_list = []
    for r in responses:
        # parse answers (строка) обратно в dict
        try:
            parsed: Dict[int, int] = eval(r.answers)  # если сохранили через str(dict)
        except:
            parsed = {}
        out_list.append(
            schemas.SurveyResponseOut(
                id=r.id,
                respondent_name=r.respondent_name,
                answers=parsed,
                total_score=r.total_score,
                recommendation=r.recommendation,
                created_at=r.created_at
            )
        )
    return out_list


@router.post("/", response_model=schemas.SurveyOut)
def create_survey_endpoint(
    survey_in: schemas.SurveyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admins only")
    return crud.create_survey(db, survey_in)