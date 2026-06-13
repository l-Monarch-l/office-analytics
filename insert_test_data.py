import psycopg2
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Подключение к БД (использует переменные из .env)
conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME', 'office_analytics'),
    user=os.getenv('DB_USER', 'admin'),
    password=os.getenv('DB_PASSWORD', 'admin123'),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432')
)
cur = conn.cursor()

# Создаём зоны, если их нет
cur.execute("SELECT id FROM zones WHERE id = 1")
if not cur.fetchone():
    cur.execute("INSERT INTO zones (id, name, type, capacity) VALUES (1, 'Open Space', 'workplace', 20)")

cur.execute("SELECT id FROM zones WHERE id = 2")
if not cur.fetchone():
    cur.execute("INSERT INTO zones (id, name, type, capacity) VALUES (2, 'Переговорная комната', 'meeting', 6)")

# Очистим старые метрики (чтобы не было дублей)
cur.execute("DELETE FROM occupancy_metrics")
conn.commit()

# Генерируем данные за последние 7 дней с шагом 5 минут
end_date = datetime.now().replace(minute=0, second=0, microsecond=0)
start_date = end_date - timedelta(days=7)

current = start_date
while current <= end_date:
    hour = current.hour
    # Open Space: пик с 9 до 12 и с 14 до 18
    if 9 <= hour <= 12 or 14 <= hour <= 18:
        count1 = random.randint(8, 18)
    else:
        count1 = random.randint(1, 5)
    
    # Переговорная: пик с 10 до 16
    if 10 <= hour <= 16:
        count2 = random.randint(2, 5)
    else:
        count2 = random.randint(0, 2)
    
    cur.execute(
        "INSERT INTO occupancy_metrics (zone_id, timestamp, people_count) VALUES (%s, %s, %s)",
        (1, current, count1)
    )
    cur.execute(
        "INSERT INTO occupancy_metrics (zone_id, timestamp, people_count) VALUES (%s, %s, %s)",
        (2, current, count2)
    )
    current += timedelta(minutes=5)

conn.commit()
cur.close()
conn.close()
print(f"✅ Данные добавлены: с {start_date.strftime('%Y-%m-%d %H:%M')} по {end_date.strftime('%Y-%m-%d %H:%M')}")