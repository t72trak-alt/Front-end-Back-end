# fix_encoding.py
import sqlite3
import json
def fix_services_encoding():
    conn = sqlite3.connect('app/database.db')
    cursor = conn.cursor()
    print("Исправление кодировки услуг...")
    # Получаем все услуги
    cursor.execute("SELECT id, title, short_description, features FROM services")
    services = cursor.fetchall()
    for service in services:
        service_id, title, short_desc, features = service
        # Исправляем заголовки (они уже правильные в базе, но отображаются некорректно)
        # Это может быть проблема с кодировкой при отображении в PowerShell/браузере
        print(f"Услуга ID {service_id}: {title}")
    # Давайте просто проверим, что данные в порядке
    print("\nТекущие данные в базе:")
    cursor.execute("SELECT id, title, price_range, duration FROM services")
    services = cursor.fetchall()
    for service in services:
        service_id, title, price_range, duration = service
        print(f"\nID: {service_id}")
        print(f"  Заголовок (сырой): {repr(title)}")
        print(f"  Заголовок (utf-8): {title}")
        print(f"  Цена: {price_range}")
        print(f"  Срок: {duration}")
    conn.close()
    print("\n✅ Проверка завершена")
    print("\nПроблема может быть в:")
    print("1. Кодировке при сохранении в базу")
    print("2. Кодировке при чтении из базы")
    print("3. Отображении в браузере/консоли")
if __name__ == "__main__":
    fix_services_encoding()
