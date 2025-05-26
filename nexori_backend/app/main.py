from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routes import surveys, tests, auth, analytics, health
from app.logger import logger
from app.routes import admin  

# Создание таблиц в базе данных (если их еще нет)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nexori Backend",
    description="Система профориентации абитуриентов с поддержкой аутентификации, логирования, аналитики и ML",
    version="1.0.0"
)

# Добавляем CORS middleware, чтобы разрешить запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production рекомендуется указывать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(surveys.router, prefix="/api")
app.include_router(tests.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(analytics.router, prefix="/api/analytics")
app.include_router(health.router, prefix="/api")
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/ping")
def ping():
    logger.info("Ping received")
    return {"ping": "pong"}
@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Добро пожаловать в Nexori Backend!"}
