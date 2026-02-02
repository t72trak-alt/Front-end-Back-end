from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
import logging
import app.database as database
import app.models as models
router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)
# Зависимость для получения сессии БД
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket подключен. Всего: {len(self.active_connections)}")
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"❌ WebSocket отключен. Осталось: {len(self.active_connections)}")
    async def broadcast(self, message: str):
        logger.info(f"📢 Broadcast для {len(self.active_connections)} клиентов")
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Ошибка отправки: {e}")
manager = ConnectionManager()
# HTTP эндпоинт для получения истории чата
@router.get("/history/{user_id}")
async def get_chat_history(user_id: int, db: Session = Depends(get_db)):
    """Получить историю сообщений пользователя"""
    messages = db.query(models.Message).filter(
        models.Message.sender_id == user_id
    ).order_by(models.Message.created_at.asc()).all()
    return {
        "status": "success",
        "count": len(messages),
        "messages": messages
    }
# WebSocket эндпоинт для реального времени
@router.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    logger.info(f"🔄 WebSocket подключение для user_id={user_id}")
    await manager.connect(websocket)
    # Отправляем приветственное сообщение
    welcome_msg = {
        "type": "system",
        "content": f"Добро пожаловать в чат! Ваш ID: {user_id}"
    }
    await websocket.send_text(json.dumps(welcome_msg))
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            # Сохраняем сообщение в БД
            db = database.SessionLocal()
            try:
                new_message = models.Message(
                    content=message_data.get("content", ""),
                    sender_id=user_id,
                    is_owner=True,
                )
                db.add(new_message)
                db.commit()
                # Добавляем отправителя в данные для broadcast
                message_data["sender_id"] = user_id
                message_data["timestamp"] = new_message.created_at.isoformat()
                # Отправляем всем подключенным клиентам
                await manager.broadcast(json.dumps(message_data))
                logger.info(f"💬 Сообщение от user_id={user_id}: {message_data['content'][:50]}...")
            finally:
                db.close()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"👋 WebSocket отключен для user_id={user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка в WebSocket: {e}")
        manager.disconnect(websocket)