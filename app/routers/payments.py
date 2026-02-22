from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv

from app.database import get_db
from app.models import User, Payment, Transaction
from app.dependencies import get_current_user

# Попытка импорта ЮKassa (необязательно для тестового режима)
try:
    from yookassa import Configuration, Payment as YooPayment
    YOOKASSA_AVAILABLE = True
except ImportError:
    YOOKASSA_AVAILABLE = False
    print("ℹ️ ЮKassa не установлена. Работаем в тестовом режиме.")

load_dotenv()

router = APIRouter(
    prefix="/api/payments",
    tags=["payments"]
)

# Модели Pydantic для ответов
from pydantic import BaseModel

class PaymentResponse(BaseModel):
    id: int
    amount: int
    currency: str
    status: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentConfirmation(BaseModel):
    payment_id: str
    confirmation_url: str
    test_mode: bool = False

class PaymentInitiate(BaseModel):
    amount: int
    description: Optional[str] = None
    return_url: Optional[str] = None

@router.post("/initiate", response_model=PaymentConfirmation)
async def initiate_payment(
    payment_data: PaymentInitiate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Инициировать платеж (тестовый режим)"""
    
    # Проверка минимальной суммы (1 рубль = 100 копеек)
    if payment_data.amount < 100:
        raise HTTPException(status_code=400, detail="Минимальная сумма платежа 1 рубль")
    
    # Создаем запись в БД
    payment = Payment(
        user_id=current_user.id,
        amount=payment_data.amount,
        description=payment_data.description or "Пополнение баланса",
        status="pending",
        payment_metadata={
            "test_mode": True,
            "user_email": current_user.email
        }
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # ТЕСТОВЫЙ РЕЖИМ: сразу считаем платеж успешным
    # Через 3 секунды статус изменится на succeeded (имитация)
    
    # Генерируем тестовый payment_id
    test_payment_id = f"test-{uuid.uuid4()}"
    payment.transaction_id = test_payment_id
    db.commit()
    
    # В тестовом режиме возвращаем ссылку на локальный success
    return_url = payment_data.return_url or os.getenv("YOOKASSA_RETURN_URL", "http://localhost:8080/dashboard")
    
    return PaymentConfirmation(
        payment_id=test_payment_id,
        confirmation_url=f"{return_url}?payment_id={payment.id}&test_mode=true",
        test_mode=True
    )

@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook для уведомлений (тестовый режим)"""
    
    try:
        body = await request.json()
        
        # Тестовый режим: просто логируем
        print(f"🔔 Тестовый вебхук: {body}")
        
        event = body.get("event")
        payment_id = body.get("object", {}).get("id")
        
        if event == "payment.succeeded" and payment_id:
            payment = db.query(Payment).filter(
                Payment.transaction_id == payment_id
            ).first()
            
            if payment:
                payment.status = "succeeded"
                payment.updated_at = datetime.utcnow()
                
                # Создаем транзакцию
                transaction = Transaction(
                    user_id=payment.user_id,
                    amount=payment.amount,
                    status="completed",
                    currency=payment.currency
                )
                db.add(transaction)
                db.commit()
                print(f"✅ Тестовый платеж {payment_id} успешно обработан")
        
        return {"status": "ok", "test_mode": True}
        
    except Exception as e:
        print(f"❌ Ошибка тестового вебхука: {e}")
        return {"status": "error", "message": str(e), "test_mode": True}

# Эндпоинт для имитации успешного платежа (для тестирования)
@router.post("/test/success/{payment_id}")
async def test_payment_success(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Принудительно отметить платеж как успешный (только для тестирования)"""
    
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    payment.status = "succeeded"
    payment.updated_at = datetime.utcnow()
    
    # Создаем транзакцию
    transaction = Transaction(
        user_id=payment.user_id,
        amount=payment.amount,
        status="completed",
        currency=payment.currency
    )
    db.add(transaction)
    db.commit()
    
    return {"status": "success", "message": "Платеж отмечен как успешный"}

@router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Получить историю платежей пользователя"""
    
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(
        Payment.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return payments

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment_status(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статус платежа"""
    
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    return payment