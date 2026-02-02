from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import app.database as database
import app.models as models
from app.dependencies import get_current_user
router = APIRouter(
    prefix="/api/projects",
    tags=["projects"]
)
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/")
async def get_user_projects(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    projects = db.query(models.Project).filter(
        models.Project.user_id == current_user.id
    ).all()
    return {
        "status": "success",
        "count": len(projects),
        "projects": projects
    }
@router.post("/")
async def create_project(
    title: str,
    description: str = "",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not title or len(title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Название проекта обязательно")
    new_project = models.Project(
        title=title.strip(),
        description=description.strip(),
        user_id=current_user.id,
        status="active",
        created_at=datetime.now()
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {
        "status": "success",
        "message": "Проект создан",
        "project": new_project
    }
@router.get("/{project_id}")
async def get_project(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return {
        "status": "success",
        "project": project
    }
@router.put("/{project_id}")
async def update_project(
    project_id: int,
    title: str = None,
    description: str = None,
    status: str = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    if title is not None:
        project.title = title.strip()
    if description is not None:
        project.description = description.strip()
    if status is not None:
        project.status = status
    db.commit()
    db.refresh(project)
    return {
        "status": "success",
        "message": "Проект обновлен",
        "project": project
    }
@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    db.delete(project)
    db.commit()
    return {
        "status": "success",
        "message": "Проект удален"
    }