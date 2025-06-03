# app/schemas.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --------------------------------------------
#  User Schemas (пример, если уже были)
# --------------------------------------------
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True


# --------------------------------------------
#  Token Schemas (пример, если уже были)
# --------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str  # передаём роль вместе с токеном


class TokenData(BaseModel):
    username: Optional[str] = None


# --------------------------------------------
#  Test Schemas (оставляю без изменений,
#  раз у вас больше не используются)
# --------------------------------------------
# (если вы окончательно отказались от Test, их можно удалить)


# --------------------------------------------
#  Survey Schemas
# --------------------------------------------

class SurveyQuestionBase(BaseModel):
    """
    Базовый класс для вопроса опроса (общие поля).
    """
    text: str = Field(..., description="Текст вопроса")
    min_value: int = Field(0, ge=0, description="Минимальное значение ответа")
    max_value: int = Field(10, ge=0, description="Максимальное значение ответа (>= min_value)")

    class Config:
        schema_extra = {
            "example": {
                "text": "Сколько часов в неделю вы готовы работать?",
                "min_value": 0,
                "max_value": 40
            }
        }


class SurveyQuestionCreate(SurveyQuestionBase):
    """
    При создании опроса от админа: список вопросов — именно этого класса.
    """
    # Наследуем всё из SurveyQuestionBase (нет дополнительных полей)


class SurveyQuestionOut(SurveyQuestionBase):
    """
    Схема, возвращаемая клиенту при GET-запросе (есть id и связь с survey_id).
    """
    id: int

    class Config:
        from_attributes = True


class SurveyBase(BaseModel):
    """
    Базовая схема опроса — общие поля: title, description.
    """
    title: str = Field(..., description="Название опроса")
    description: Optional[str] = Field(None, description="Описание опроса")

    class Config:
        schema_extra = {
            "example": {
                "title": "Тест профориентации для абитуриентов",
                "description": "Ответьте на вопросы, чтобы получить рекомендации."
            }
        }


class SurveyCreate(SurveyBase):
    """
    Схема для создания нового опроса (админом).
    Содержит title, description и массив вопросов.
    """
    questions: List[SurveyQuestionCreate] = Field(
        ..., description="Список вопросов для опроса"
    )


class SurveyUpdate(BaseModel):
    """
    Схема для обновления опроса: title и/или description и/или список вопросов.
    Всё необязательно.
    """
    title: Optional[str] = Field(None, description="Новое название опроса")
    description: Optional[str] = Field(None, description="Новое описание")
    questions: Optional[List[SurveyQuestionCreate]] = Field(
        None, description="Новый список вопросов"
    )


class SurveyOut(SurveyBase):
    """
    Схема, возвращаемая клиенту при GET-запросе опроса:
    id, title, description, created_at, список вопросов SurveyQuestionOut.
    """
    id: int
    created_at: Optional[Any] = Field(None, description="Дата/время создания")
    questions: List[SurveyQuestionOut] = []

    class Config:
        from_attributes = True


# --------------------------------------------
#  SurveyResponse Schemas (ответ пользователя)
# --------------------------------------------

class SurveyAnswer(BaseModel):
    """
    Один ответ пользователя на конкретный вопрос:
    ключ — id вопроса, значение — число (оценка).
    """
    question_id: int
    answer_value: int


class SurveySubmit(BaseModel):
    """
    Схема тела POST-запроса при отправке ответов на опрос.
    """
    respondent_name: str = Field(..., description="Имя респондента")
    answers: List[SurveyAnswer] = Field(..., description="Список ответов на вопросы")


class SurveyResponseOut(BaseModel):
    """
    Схема, которую возвращаем после удачной записи ответов:
    содержит id, respondent_name, answers (как словарь id→значение),
    total_score, recommendation, created_at, а также связь с survey_id.
    """
    id: int
    respondent_name: str
    answers: Dict[int, int] = Field(..., description="Словарь {question_id: answer_value}")
    total_score: int
    recommendation: Optional[str] = None
    created_at: Optional[Any] = None

    class Config:
        from_attributes = True



class ResultRangeBase(BaseModel):
    min_score: int
    max_score: int
    message: str
    
class ResultRangeCreate(ResultRangeBase):
    survey_id: int
    
class ResultRangeOut(ResultRangeBase):
    id: int
    class Config: from_attributes = True
