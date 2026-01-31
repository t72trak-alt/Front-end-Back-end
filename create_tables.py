import sys
sys.path.insert(0, '.')

from app.database import Base, engine

print("Создание таблиц в базе данных SQLite...")
Base.metadata.create_all(bind=engine)
print("✅ Таблицы созданы успешно!")
