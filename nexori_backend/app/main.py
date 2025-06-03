# app/main.py

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import auth, surveys, health, admin  # смотрите, админ-роут мы назвали admin.py

# создаём все таблицы (если их ещё нет)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexori API")

# Разрешаем CORS из фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ваш фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем каждый роутер (префиксы прописаны внутри этих файлов)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(surveys.router, prefix="/api/surveys", tags=["surveys"])
app.include_router(health.router, prefix="/api/health")
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])