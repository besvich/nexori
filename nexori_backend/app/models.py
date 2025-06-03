# app/models.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


# --------------------------------------------
#  Примерная структура модели User
# --------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Integer, default=1)  # Например, 1 = active, 0 = disabled

    # Связь с опросами (если вы храните, кто какие опросы проходил)
    # survey_responses = relationship("SurveyResponse", back_populates="user")


# --------------------------------------------
#  Примерная структура модели Survey
# --------------------------------------------
class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime)  # например, время создания

    # Связь с вопросами опроса
    questions = relationship(
        "SurveyQuestion",
        back_populates="survey",
        cascade="all, delete-orphan"
    )


class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    min_value = Column(Integer, default=0)
    max_value = Column(Integer, default=10)

    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))
    survey = relationship("Survey", back_populates="questions")


# --------------------------------------------
#  Модель Test (теперь с импортом Text исправлено)
# --------------------------------------------
class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    # Здесь мы используем Text, поэтому он должен быть импортирован выше
    description = Column(Text, nullable=True)

    # Связь с вопросами теста
    questions = relationship(
        "Question",
        back_populates="test",
        cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    min_value = Column(Integer, default=0)
    max_value = Column(Integer, default=10)

    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    test = relationship("Test", back_populates="questions")


# --------------------------------------------
#  Другие модели (SurveyResponse, Analytics и т.д.)
#  Привожу их только как пример; подкорректируйте под свой код
# --------------------------------------------

class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    respondent_name = Column(String, nullable=False)
    answers = Column(String, nullable=False)  # можно хранить JSON-строкой
    total_score = Column(Integer, nullable=False)
    recommendation = Column(String, nullable=True)
    created_at = Column(DateTime)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))

    # Связи, если нужны
    # user = relationship("User", back_populates="survey_responses")
    # survey = relationship("Survey", back_populates="responses")
