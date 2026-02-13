from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import User, Service, Project, Message, Transaction
from app.schemas import StatisticResponse
router = APIRouter(prefix="/api/stats", tags=["statistics"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/", response_model=StatisticResponse)
def get_statistics(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar()
    total_services = db.query(func.count(Service.id)).scalar()
    total_projects = db.query(func.count(Project.id)).scalar()
    total_messages = db.query(func.count(Message.id)).scalar()
    total_transactions = db.query(func.count(Transaction.id)).scalar()
    return StatisticResponse(
        total_users=total_users,
        total_services=total_services,
        total_projects=total_projects,
        total_messages=total_messages,
        total_transactions=total_transactions
    )
