from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# ---------- Users ---------- #
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")          # "user" | "admin"
    surveys = relationship("Survey", back_populates="owner")

# ---------- Tests ---------- #
class Test(Base):
    """
    Заголовок теста: описание + время создания
    """
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    questions = relationship("TestQuestion", back_populates="test", cascade="all, delete-orphan")
    results = relationship("TestResult", back_populates="test", cascade="all, delete-orphan")

class TestQuestion(Base):
    """
    Вопросы и допустимые варианты (JSON-строка) для гибкости
    """
    __tablename__ = "test_questions"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    text = Column(Text, nullable=False)
    options = Column(Text, nullable=True)          # JSON: {value: label}
    weight = Column(Integer, default=1)
    test = relationship("Test", back_populates="questions")

class TestResult(Base):
    """
    Таблица «балл-диапазон → рекомендация».
    min_score ≤ user_score <= max_score
    """
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    min_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    recommendation = Column(Text, nullable=False)
    test = relationship("Test", back_populates="results")

# ---------- Surveys ---------- #
class Survey(Base):
    __tablename__ = "surveys"
    id = Column(Integer, primary_key=True, index=True)
    respondent_name = Column(String, index=True)
    answers = Column(Text)                         # JSON-строка с ответами
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    test_id = Column(Integer, ForeignKey("tests.id"))
    owner = relationship("User", back_populates="surveys")
    test = relationship("Test")
