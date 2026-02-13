from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app.models import User
from app.schemas import UserCreate, UserResponse
router = APIRouter(prefix="/api/users", tags=["users"])
# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# GET /api/users - получить всех пользователей
@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
# GET /api/users/{user_id} - получить пользователя по ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
# GET /api/users/email/{email} - найти пользователя по email
@router.get("/email/{email}", response_model=UserResponse)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
# POST /api/users - создать нового пользователя
@router.post("/", response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, нет ли пользователя с таким email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    # Создаем пользователя
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        is_admin=user_data.is_admin,
        hashed_password=user_data.password if user_data.password else "",
        salt=""
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
# PUT /api/users/{user_id} - обновить пользователя
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    # Проверяем email на уникальность (если изменился)
    if user_data.email != user.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    # Обновляем поля
    user.email = user_data.email
    user.name = user_data.name
    user.is_admin = user_data.is_admin
    if user_data.password:
        user.hashed_password = user_data.password
    db.commit()
    db.refresh(user)
    return user
# DELETE /api/users/{user_id} - удалить пользователя
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(user)
    db.commit()
    return {"message": "Пользователь удален", "user_id": user_id}
