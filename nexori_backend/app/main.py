from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import auth, surveys, admin   # admin-роут подключите аналогично

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexori API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== маршруты =====

app.include_router(auth.router,    prefix="/api")
app.include_router(surveys.router, prefix="/api")
app.include_router(admin.router,   prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}
