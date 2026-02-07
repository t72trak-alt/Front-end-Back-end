# update_services.py
import sqlite3
import json
from datetime import datetime
def update_services_pricing():
    conn = sqlite3.connect('app/database.db')
    cursor = conn.cursor()
    # Данные для обновления услуг
    services_updates = [
        {
            "id": 1,
            "title": "🎯 Промпт-инжиниринг",
            "icon": "🎯",
            "price_range": json.dumps({"min": 15000, "max": 50000}),
            "duration": json.dumps({"min": 3, "max": 7}),
            "features": json.dumps([
                "Анализ задачи и контекста",
                "Разработка эффективных промптов",
                "Тестирование и оптимизация",
                "Документация по использованию",
                "Консультация по интеграции"
            ])
        },
        {
            "id": 2,
            "title": "🤖 Разработка ИИ-решений",
            "icon": "🤖",
            "price_range": json.dumps({"min": 50000, "max": 200000}),
            "duration": json.dumps({"min": 14, "max": 30}),
            "features": json.dumps([
                "Проектирование архитектуры",
                "Разработка прототипа",
                "Интеграция AI моделей",
                "Оптимизация производительности",
                "Техническая документация"
            ])
        },
        {
            "id": 3,
            "title": "🔧 Интеграция ИИ в бизнес",
            "icon": "🔧",
            "price_range": json.dumps({"min": 100000, "max": 500000}),
            "duration": json.dumps({"min": 30, "max": 90}),
            "features": json.dumps([
                "Анализ бизнес-процессов",
                "Разработка плана интеграции",
                "Внедрение решения",
                "Обучение сотрудников",
                "Техническая поддержка"
            ])
        },
        {
            "id": 4,
            "title": "⚙️ Автоматизация бизнес-процессов",
            "icon": "⚙️",
            "price_range": json.dumps({"min": 50000, "max": 300000}),
            "duration": json.dumps({"min": 7, "max": 30}),
            "features": json.dumps([
                "Аудит процессов",
                "Проектирование автоматизации",
                "Разработка скриптов/ботов",
                "Интеграция с существующими системами",
                "Мониторинг и аналитика"
            ])
        }
    ]
    for service in services_updates:
        cursor.execute('''
            UPDATE services 
            SET price_range = ?, 
                duration = ?,
                features = ?,
                updated_at = ?
            WHERE id = ?
        ''', (
            service["price_range"],
            service["duration"],
            service["features"],
            datetime.now().isoformat(),
            service["id"]
        ))
        if cursor.rowcount == 0:
            print(f"⚠️ Услуга с ID {service['id']} не найдена")
        else:
            print(f"✅ Услуга '{service['title']}' обновлена")
    conn.commit()
    # Проверим результат
    print("\nОбновленные услуги:")
    cursor.execute("SELECT id, title, price_range, duration, features FROM services ORDER BY id")
    services = cursor.fetchall()
    for service in services:
        print(f"\n{service[1]} (ID: {service[0]})")
        try:
            price_data = json.loads(service[2]) if service[2] else {}
            print(f"  Цена: {price_data.get('min', 0):,} - {price_data.get('max', 0):,} ₽")
        except:
            print(f"  Цена: {service[2]}")
        try:
            duration_data = json.loads(service[3]) if service[3] else {}
            print(f"  Срок: {duration_data.get('min', 0)}-{duration_data.get('max', 0)} дней")
        except:
            print(f"  Срок: {service[3]}")
    conn.close()
    print("\n✅ Все услуги обновлены!")
if __name__ == "__main__":
    update_services_pricing()
