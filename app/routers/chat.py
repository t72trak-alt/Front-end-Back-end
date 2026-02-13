from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import List
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import Message, User

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# ========== ЭНДПОИНТ ДЛЯ ПРОВЕРКИ БД ==========
@router.get("/check-db")
async def check_db(db: Session = Depends(get_db)):
    """
    Проверить, какая БД реально используется
    """
    try:
        db_url = str(db.bind.url)
        user_count = db.query(User).count()
        users = db.query(User).all()
        
        return {
            "db_url": db_url,
            "user_count": user_count,
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "name": u.name,
                    "is_admin": u.is_admin
                } for u in users
            ]
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }

# ========== ТЕСТОВЫЙ ЭНДПОИНТ ДЛЯ ПРОВЕРКИ ПОЛЬЗОВАТЕЛЕЙ ==========
@router.get("/test-users")
async def test_users(db: Session = Depends(get_db)):
    """
    Тестовый эндпоинт для проверки пользователей в БД
    """
    try:
        print("\n🔍 ТЕСТОВЫЙ ЗАПРОС: ПОЛУЧЕНИЕ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ")
        users = db.query(User).all()
        result = {
            "count": len(users),
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "name": u.name,
                    "is_admin": u.is_admin
                } for u in users
            ]
        }
        print(f"✅ Найдено пользователей: {len(users)}")
        return result
    except Exception as e:
        print(f"❌ Ошибка в test-users: {str(e)}")
        return {"error": str(e)}

@router.get("/history/{user_id}")
async def get_chat_history(user_id: int, db: Session = Depends(get_db)):
    """
    Получить историю сообщений для конкретного пользователя
    """
    print(f"\n{'='*50}")
    print(f"🔥 ВЫЗВАНА get_chat_history ДЛЯ user_id={user_id}")
    print(f"{'='*50}")
    
    try:
        print(f"🔍 Ищем пользователя с id={user_id}...")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"❌ Пользователь с id={user_id} НЕ НАЙДЕН в БД!")
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        print(f"✅ Пользователь найден: {user.email} (админ: {user.is_admin})")
        print(f"🔍 Ищем сообщения для user_id={user_id}...")
        
        messages = db.query(Message).filter(
            (Message.sender_id == user_id) | (Message.receiver_id == user_id)
        ).order_by(Message.created_at.asc()).all()
        
        print(f"📊 Найдено сообщений: {len(messages)}")
        
        result = []
        for i, msg in enumerate(messages):
            print(f"  📝 Сообщение {i+1}: id={msg.id}, sender={msg.sender_id}, receiver={msg.receiver_id}, owner={msg.is_owner}")
            result.append({
                "id": msg.id,
                "content": msg.content,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "is_from_admin": not msg.is_owner,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        print(f"✅ Возвращаем {len(result)} сообщений")
        return result
        
    except HTTPException:
        print(f"⚠️ HTTP исключение: пользователь не найден")
        raise
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА в get_chat_history:")
        print(f"   Тип ошибки: {type(e).__name__}")
        print(f"   Текст ошибки: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"\n")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории: {str(e)}")

@router.get("/stats/total")
async def get_total_messages(db: Session = Depends(get_db)):
    """
    Получить общее количество сообщений
    """
    try:
        total = db.query(Message).count()
        return {"total": total}
    except Exception as e:
        print(f"❌ Ошибка stats/total: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")

@router.websocket("/admin")
async def websocket_admin_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    db = SessionLocal()
    
    try:
        await websocket.send_json({
            "type": "connection_established",
            "status": "connected",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_type = message_data.get("type")
            
            if message_type == "admin_message":
                target_user_id = message_data.get("user_id")
                content = message_data.get("content")
                
                if not target_user_id or not content:
                    continue
                
                try:
                    # Сохраняем сообщение в БД
                    db_message = Message(
                        content=content,
                        sender_id=1,
                        receiver_id=target_user_id,
                        is_owner=False,
                        created_at=datetime.now()
                    )
                    db.add(db_message)
                    db.commit()
                    
                    print(f"✅ Сообщение от админа сохранено в БД для user_id={target_user_id}")
                    
                    # Показываем сообщение в чате админа
                    await websocket.send_json({
                        "type": "new_message",
                        "user_id": target_user_id,
                        "content": content,
                        "sender_id": 1,
                        "is_from_admin": True,
                        "created_at": datetime.now().isoformat()
                    })
                    
                    # Отправляем сообщение пользователю
                    user_sent = False
                    for connection in manager.active_connections:
                        if connection != websocket:
                            try:
                                await connection.send_json({
                                    "type": "new_message",
                                    "user_id": target_user_id,
                                    "content": content,
                                    "sender_id": 1,
                                    "is_from_admin": True,
                                    "created_at": datetime.now().isoformat()
                                })
                                user_sent = True
                                print(f"📨 Сообщение от админа отправлено пользователю {target_user_id}")
                            except Exception as e:
                                print(f"❌ Ошибка отправки пользователю: {e}")
                    
                    if not user_sent:
                        print(f"⚠️ Пользователь {target_user_id} не в сети, сообщение сохранено в БД")
                    
                except Exception as e:
                    db.rollback()
                    print(f"❌ Ошибка БД: {e}")
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🔌 Админ отключился")
    finally:
        db.close()

@router.websocket("/ws/chat/{user_id}")
async def websocket_user_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket)
    db = SessionLocal()
    
    try:
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                content = data.get("content")
                if not content:
                    continue
                
                try:
                    # Сохраняем сообщение в БД
                    message = Message(
                        sender_id=user_id,
                        receiver_id=1,
                        content=content,
                        is_owner=True,
                        created_at=datetime.now()
                    )
                    db.add(message)
                    db.commit()
                    
                    print(f"✅ Сообщение от пользователя {user_id} сохранено в БД: {content}")
                    
                    # Показываем сообщение в чате пользователя
                    await websocket.send_json({
                        "type": "new_message",
                        "user_id": user_id,
                        "content": content,
                        "sender_id": user_id,
                        "is_from_admin": False,
                        "created_at": datetime.now().isoformat()
                    })
                    
                    # Отправляем сообщение админу
                    admin_sent = False
                    for connection in manager.active_connections:
                        if connection != websocket:
                            try:
                                await connection.send_json({
                                    "type": "new_message",
                                    "user_id": user_id,
                                    "content": content,
                                    "sender_id": user_id,
                                    "is_from_admin": False,
                                    "created_at": datetime.now().isoformat()
                                })
                                admin_sent = True
                                print(f"📨 Сообщение от пользователя {user_id} отправлено админу")
                            except Exception as e:
                                print(f"❌ Ошибка отправки админу: {e}")
                    
                    if not admin_sent:
                        print("⚠️ Админ не в сети, сообщение сохранено в БД")
                    
                except Exception as e:
                    print(f"❌ Ошибка сохранения: {e}")
                    db.rollback()
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"🔌 Пользователь {user_id} отключился")
    except Exception as e:
        print(f"❌ Ошибка в websocket_user_endpoint: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()