from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import app.database as database
import app.models as models
from app.dependencies import get_current_user
router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Проверка, что пользователь администратор
def check_admin(user: models.User):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user
# Получить всех пользователей
@router.get("/users")
async def get_all_users(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin(current_user)
    users = db.query(models.User).all()
    return {
        "status": "success",
        "count": len(users),
        "users": users
    }
# Получить все проекты (всех пользователей)
@router.get("/projects")
async def get_all_projects(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_admin(current_user)
    projects = db.query(models.Project).all()
    return {
        "status": "success",
        "count": len(projects),
        "projects": projects
    }