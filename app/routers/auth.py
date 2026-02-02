from fastapi import APIRouter, HTTPException, Depends, Response, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
import jwt
from datetime import datetime, timedelta
import hashlib
import secrets

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = "your-super-secret-jwt-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class LoginRequest(BaseModel):
    email: str
    password: str

def hash_password(password: str, salt: str = None) -> tuple:
    if salt is None:
        salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256()
    hash_obj.update(f"{password}{salt}".encode('utf-8'))
    hashed_password = hash_obj.hexdigest()
    return hashed_password, salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    test_hash, _ = hash_password(password, salt)
    return test_hash == hashed_password

def create_access_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@router.post("/register")
async def register(
    email: str,
    name: str,
    password: str,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    hashed_password, salt = hash_password(password)
    new_user = User(
        email=email,
        name=name,
        hashed_password=hashed_password,
        salt=salt
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "status": "success",
        "message": "Пользователь зарегистрирован",
        "user_id": new_user.id
    }

@router.post("/login")
async def login(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == login_data.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    if not verify_password(login_data.password, db_user.hashed_password, db_user.salt):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    access_token = create_access_token(login_data.email)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        path="/"
    )
    return {
        "status": "success",
        "message": "Вход выполнен",
        "access_token": access_token,
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "name": db_user.name
        }
    }

from app.dependencies import get_current_user

@router.get("/me")
async def get_current_user_info(request: Request):
    user = await get_current_user(request)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at
    }