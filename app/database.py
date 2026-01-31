from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env

# Получаем URL БД из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Если DATABASE_URL не указан, используем SQLite для тестов
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./app/database.db"
    print("⚠️  DATABASE_URL не найден в .env, используем SQLite")

# Создаем движок SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    # Для SQLite нужно добавить connect_args
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
