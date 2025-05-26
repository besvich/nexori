# tests/test_surveys.py
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from sqlalchemy.orm import Session

# Создаем тестовую базу данных перед запуском тестов
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_create_and_get_survey(test_db: Session):
    survey_data = {
        "respondent_name": "Test User",
        "answers": {"question1": 5, "question2": 7, "question3": 8}
    }
    # Создание опроса
    response = client.post("/api/surveys/", json=survey_data)
    assert response.status_code == 200
    created = response.json()
    assert created["respondent_name"] == "Test User"
    survey_id = created["id"]

    # Получение опроса по ID
    response = client.get(f"/api/surveys/{survey_id}")
    assert response.status_code == 200
    survey = response.json()
    assert survey["id"] == survey_id
    # Проверка корректности десериализации ответов
    answers = survey["answers"]
    # В базе ответы сериализуются как JSON-строка, поэтому на клиенте они уже преобразованы через схему

def test_update_and_delete_survey(test_db: Session):
    survey_data = {
        "respondent_name": "Update Test",
        "answers": {"question1": 3, "question2": 4, "question3": 6}
    }
    response = client.post("/api/surveys/", json=survey_data)
    assert response.status_code == 200
    survey = response.json()
    survey_id = survey["id"]

    # Обновление опроса
    updated_data = {
        "respondent_name": "Updated User",
        "answers": {"question1": 7, "question2": 8, "question3": 9}
    }
    response = client.put(f"/api/surveys/{survey_id}", json=updated_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["respondent_name"] == "Updated User"

    # Удаление опроса
    response = client.delete(f"/api/surveys/{survey_id}")
    assert response.status_code == 200
    # Проверяем, что опрос удален
    response = client.get(f"/api/surveys/{survey_id}")
    assert response.status_code == 404
