# update_descriptions.py
import sqlite3
import json
from datetime import datetime
def update_service_descriptions():
    conn = sqlite3.connect('app/database.db')
    cursor = conn.cursor()
    # Данные для обновления
    services_data = [
        {
            "id": 1,
            "short_description": "Создание и оптимизация промптов для AI-моделей",
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
            "short_description": "Разработка интеллектуальных ассистентов для бизнеса",
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
            "short_description": "Внедрение AI-решений в бизнес-процессы",
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
            "short_description": "Анализ и автоматизация рутинных процессов",
            "features": json.dumps([
                "Аудит процессов",
                "Проектирование автоматизации", 
                "Разработка скриптов/ботов",
                "Интеграция с системами",
                "Мониторинг и аналитика"
            ])
        }
    ]
    for service in services_data:
        cursor.execute('''
            UPDATE services 
            SET short_description = ?,
                features = ?,
                updated_at = ?
            WHERE id = ?
        ''', (
            service["short_description"],
            service["features"],
            datetime.now().isoformat(),
            service["id"]
        ))
        print(f"✅ Обновлено описание для услуги ID {service['id']}")
    conn.commit()
    # Проверим результат
    print("\n" + "="*60)
    print("Обновленные данные:")
    cursor.execute("SELECT id, title, short_description, features FROM services ORDER BY id")
    services = cursor.fetchall()
    for service in services:
        service_id, title, short_desc, features = service
        print(f"\n📋 {title} (ID: {service_id})")
        print(f"   Описание: {short_desc}")
        try:
            if features:
                features_list = json.loads(features)
                print(f"   Особенностей: {len(features_list)}")
        except:
            print(f"   Особенности: ошибка парсинга")
    conn.close()
    print("\n" + "="*60)
    print("✅ Все описания обновлены!")
if __name__ == "__main__":
    update_service_descriptions()
