from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Service
from app.dependencies import get_current_user
router = APIRouter(prefix="/api/services", tags=["services"])
# API для получения всех услуг
@router.get("")
async def get_services(db: Session = Depends(get_db)):
    services = db.query(Service).filter(Service.is_active == True).all()
    return services
# API для создания услуги (только для админа)
@router.post("")
async def create_service(
    title: str,
    short_description: str,
    full_description: str = "",
    icon: str = "🛠️",
    features: list = None,
    technologies: list = None,
    price_range: str = "от 10 000 руб.",
    duration: str = "1-2 недели",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только для администраторов")
    new_service = Service(
        title=title,
        short_description=short_description,
        full_description=full_description,
        icon=icon,
        features=features or [],
        technologies=technologies or [],
        price_range=price_range,
        duration=duration
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return {"status": "success", "service": new_service}
