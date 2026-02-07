print("=== ИСПРАВЛЕНИЕ БАЗЫ ДАННЫХ ===")
import sys
sys.path.append('.')
try:
    # Подключаемся к базе
    from app.database import engine, Base
    print("✓ База данных подключена")
    # Загружаем модели
    from app.models import User, Project, Service
    print("✓ Основные модели загружены")
    try:
        from app.models import AdminLog
        print("✓ Модель AdminLog загружена")
    except ImportError:
        print("⚠ Модель AdminLog не найдена")
    # Создаем таблицы
    print("\nСоздаю таблицы...")
    Base.metadata.create_all(bind=engine)
    print("✅ ВСЕ ТАБЛИЦЫ СОЗДАНЫ!")
    # Проверяем
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nСоздано таблиц: {len(tables)}")
    for table in tables:
        print(f"  - {table}")
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
