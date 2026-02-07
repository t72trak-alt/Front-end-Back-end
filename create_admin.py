# create_admin.py
print("=== СОЗДАНИЕ АДМИНИСТРАТОРА ===")
import sys
sys.path.append('.')
try:
    from app.database import SessionLocal
    from app.models import User
    from datetime import datetime
    import bcrypt
    db = SessionLocal()
    email = "admin@aidevportal.com"
    password = "admin123"
    # Хешируем пароль
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # Проверяем существование
    admin = db.query(User).filter(User.email == email).first()
    if admin:
        admin.hashed_password = hashed_password
        admin.is_admin = True
        print("✅ Администратор обновлен")
    else:
        admin = User(
            email=email,
            name="Администратор",
            hashed_password=hashed_password,
            is_admin=True,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(admin)
        print("✅ Администратор создан")
    db.commit()
    print(f"Email: {email}")
    print(f"Пароль: {password}")
    print(f"is_admin: {admin.is_admin}")
    db.close()
except Exception as e:
    print(f"❌ Ошибка: {e}")
