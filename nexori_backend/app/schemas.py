from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# ---------- User ---------- #
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    role: str
    class Config:
        from_attributes = True

# ---------- Test ---------- #
class TestQuestionCreate(BaseModel):
    text: str
    options: Optional[Dict[str, str]] = None   # value -> label
    weight: int = 1

class TestResultCreate(BaseModel):
    min_score: int
    max_score: int
    recommendation: str

class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    questions: List[TestQuestionCreate]
    results: List[TestResultCreate]

class TestOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    questions: List[TestQuestionCreate]
    results: List[TestResultCreate]
    class Config:
        from_attributes = True

# ---------- Survey ---------- #
class SurveyBase(BaseModel):
    respondent_name: str
    answers: Dict[str, Any]
    test_id: int

class SurveyCreate(SurveyBase):
    pass

class SurveyOut(SurveyBase):
    id: int
    created_at: datetime
    owner_id: int
    class Config:
        from_attributes = True

# ---------- Recommendation ---------- #
class RecommendationOut(BaseModel):
    survey_id: int
    recommendation: str


# ---------- Token (OAuth2) ----------
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str            # "user" | "admin"
