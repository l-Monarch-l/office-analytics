# init_db.py
from web.models import engine, Base, Zone
from sqlalchemy.orm import Session

print("Создание таблиц...")
Base.metadata.drop_all(engine)  # удалит старые таблицы (если были), для чистой инициализации
Base.metadata.create_all(engine)
print("Таблицы созданы.")

# Добавляем две тестовые зоны
with Session(engine) as session:
    if session.query(Zone).count() == 0:
        zone1 = Zone(id=1, name="Open Space", type="workplace", capacity=20)
        zone2 = Zone(id=2, name="Переговорная комната", type="meeting", capacity=6)
        session.add_all([zone1, zone2])
        session.commit()
        print("Добавлены зоны: Open Space, Переговорная комната")
    else:
        print("Зоны уже есть")