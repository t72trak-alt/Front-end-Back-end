from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app import models
from app.schemas import MessageResponse
router = APIRouter(prefix="/api/chat", tags=["chat-history"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/history/{user_id}", response_model=List[MessageResponse])
async def get_chat_history(user_id: int, db: Session = Depends(get_db)):
    """
    Получить историю сообщений для указанного пользователя
    """
    # Проверяем существование пользователя
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    # Получаем сообщения для этого пользователя
    # ИСПРАВЛЕНО: фильтруем по user_id вместо sender_id
    messages = db.query(models.Message).filter(
        models.Message.user_id == user_id
    ).order_by(models.Message.created_at).all()
    return messages
