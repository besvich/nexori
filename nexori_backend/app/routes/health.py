# app/routes/health.py
from fastapi import APIRouter
from app.logger import logger

router = APIRouter()

@router.get("/health")
def health_check():
    logger.info("Health check accessed")
    return {"status": "ok"}
