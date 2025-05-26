# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_registration_and_login(test_db):
    # Регистрация пользователя
    user_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    registered = response.json()
    assert registered["username"] == "testuser"

    # Логин (получение токена)
    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/api/auth/token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
