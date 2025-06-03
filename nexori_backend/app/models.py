from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email    = Column(String, nullable=True)
    password = Column(String, nullable=False)
    role     = Column(String, default="user")

    # связи
    responses = relationship("SurveyResponse", back_populates="user")

# ---------- опросы ----------
class Survey(Base):
    __tablename__ = "surveys"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    questions = relationship("SurveyQuestion", back_populates="survey",
                             cascade="all, delete-orphan")
    ranges    = relationship("SurveyResultRange", back_populates="survey",
                             cascade="all, delete-orphan")
    responses = relationship("SurveyResponse", back_populates="survey",
                             cascade="all, delete-orphan")

class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id         = Column(Integer, primary_key=True, index=True)
    survey_id  = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))
    text       = Column(Text, nullable=False)
    min_value  = Column(Integer, default=0)
    max_value  = Column(Integer, default=10)

    survey = relationship("Survey", back_populates="questions")

class SurveyResultRange(Base):
    """
    Диапазон баллов → текст рекомендации
    """
    __tablename__ = "survey_result_ranges"

    id         = Column(Integer, primary_key=True, index=True)
    survey_id  = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))
    min_score  = Column(Integer, nullable=False)
    max_score  = Column(Integer, nullable=False)
    message    = Column(Text,     nullable=False)

    survey = relationship("Survey", back_populates="ranges")

# ---------- ответы ----------
class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id        = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"))
    user_id   = Column(Integer, ForeignKey("users.id",    ondelete="SET NULL"))
    respondent_name = Column(String, nullable=False)

    total_score     = Column(Integer, default=0)
    recommendation  = Column(Text,    nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    # JSON-строка «{question_id: answer_value, …}»
    answers_raw = Column(Text, nullable=False)

    survey = relationship("Survey", back_populates="responses")
    user   = relationship("User",   back_populates="responses")
