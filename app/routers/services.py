from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import json
from datetime import datetime

from app.database import get_db
from app.models import Service, User, Project
from app.dependencies import get_current_user
from fastapi.templating import Jinja2Templates; templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/services", tags=["services"])

@router.get("", response_class=HTMLResponse)
async def services_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Страница услуг"""
    services = db.query(Service).filter(Service.is_active == True).order_by(Service.order_index).all()
    
    # Преобразуем JSON
    for service in services:
        if service.features and isinstance(service.features, str):
            try:
                service.features = json.loads(service.features)
            except:
                service.features = []
        
        if service.technologies and isinstance(service.technologies, str):
            try:
                service.technologies = json.loads(service.technologies)
            except:
                service.technologies = []
    
    return templates.TemplateResponse(
        "services.html",
        {
            "request": request,
            "user": current_user,
            "services": services,
            "active_page": "services"
        }
    )

@router.get("/{service_id}", response_class=HTMLResponse)
async def service_detail(
    request: Request,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Детальная страница услуги"""
    service = db.query(Service).filter(Service.id == service_id, Service.is_active == True).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    # Преобразуем JSON
    if service.features and isinstance(service.features, str):
        try:
            service.features = json.loads(service.features)
        except:
            service.features = []
    
    if service.technologies and isinstance(service.technologies, str):
        try:
            service.technologies = json.loads(service.technologies)
        except:
            service.technologies = []
    
    return templates.TemplateResponse(
        "service_detail.html",
        {
            "request": request,
            "user": current_user,
            "service": service,
            "active_page": "services"
        }
    )

@router.post("/order/{service_id}")
async def order_service(
    service_id: int,
    request: Request,
    message: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Заказ услуги (создание проекта)"""
    service = db.query(Service).filter(Service.id == service_id, Service.is_active == True).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    # Создаем новый проект
    project = Project(
        title=f"Заказ услуги: {service.title}",
        description=f"""Услуга: {service.title}
        
Сообщение от клиента: {message}

Дата заказа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
        status="new",
        user_id=current_user.id,
        service_id=service.id,
        created_at=datetime.now()
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Перенаправляем в чат проекта
    return RedirectResponse(url=f"/chat/{project.id}", status_code=303)
