from flask import Blueprint, jsonify, request
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from .models import SessionLocal, OccupancyMetric, Zone

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/zones', methods=['GET'])
def get_zones():
    """Возвращает список всех зон для выпадающего списка"""
    db = SessionLocal()
    zones = db.query(Zone).all()
    db.close()
    return jsonify([{"id": z.id, "name": z.name} for z in zones])

@api.route('/occupancy/current', methods=['GET'])
def get_current_occupancy():
    """Возвращает текущую занятость по всем зонам и общую сводку"""
    db = SessionLocal()
    # Подзапрос для получения самой последней записи для каждой зоны
    subquery = db.query(
        OccupancyMetric.zone_id,
        func.max(OccupancyMetric.timestamp).label('max_ts')
    ).group_by(OccupancyMetric.zone_id).subquery()

    latest_metrics = db.query(
        OccupancyMetric.zone_id,
        OccupancyMetric.people_count,
        Zone.name,
        Zone.capacity
    ).join(
        subquery,
        and_(
            OccupancyMetric.zone_id == subquery.c.zone_id,
            OccupancyMetric.timestamp == subquery.c.max_ts
        )
    ).join(Zone, Zone.id == OccupancyMetric.zone_id).all()

    total_people = 0
    total_capacity = 0
    zones_data = []

    for zone_id, count, name, capacity in latest_metrics:
        total_people += count
        total_capacity += capacity
        zones_data.append({
            "id": zone_id,
            "name": name,
            "count": count,
            "capacity": capacity
        })

    occupancy_rate = (total_people / total_capacity * 100) if total_capacity > 0 else 0

    db.close()
    return jsonify({
        "total_people": total_people,
        "total_capacity": total_capacity,
        "occupancy_rate": round(occupancy_rate, 1),
        "zones": zones_data
    })

@api.route('/occupancy/history', methods=['GET'])
def get_occupancy_history():
    """Возвращает исторические данные для графика за выбранный период"""
    zone_id = request.args.get('zone_id', type=int)
    period = request.args.get('period', 'day') # 'day', 'week', 'month'

    db = SessionLocal()
    
    end_date = datetime.now()
    if period == 'day':
        start_date = end_date - timedelta(days=1)
        group_by = func.date_trunc('hour', OccupancyMetric.timestamp)
    elif period == 'week':
        start_date = end_date - timedelta(days=7)
        group_by = func.date_trunc('day', OccupancyMetric.timestamp)
    else: # month
        start_date = end_date - timedelta(days=30)
        group_by = func.date_trunc('day', OccupancyMetric.timestamp)

    query = db.query(
        group_by.label('period'),
        func.avg(OccupancyMetric.people_count).label('avg_people')
    ).filter(
        OccupancyMetric.timestamp >= start_date,
        OccupancyMetric.timestamp <= end_date
    )
    
    if zone_id:
        query = query.filter(OccupancyMetric.zone_id == zone_id)
    
    results = query.group_by('period').order_by('period').all()

    data = {
        "labels": [r.period.strftime('%Y-%m-%d %H:00') if period == 'day' else r.period.strftime('%Y-%m-%d') for r in results],
        "values": [round(r.avg_people, 1) for r in results]
    }
    db.close()
    return jsonify(data)

@api.route('/events/recent', methods=['GET'])
def get_recent_events():
    """Возвращает последние 10 событий (вход/выход)"""
    db = SessionLocal()
    # Этот запрос требует таблицу `events`, которую нужно создать
    # Для демонстрации заглушка
    db.close()
    return jsonify([
        {"time": "2026-06-02 15:30:22", "zone": "Переговорная", "type": "Вход"},
        {"time": "2026-06-02 15:28:15", "zone": "Open Space", "type": "Выход"},
    ])



@api.route('/heatmap', methods=['GET'])
def get_heatmap_data():
    """Возвращает данные для тепловой карты: матрица зоны x часы (средняя занятость)"""
    db = SessionLocal()
    # Данные за последние 24 часа, почасово, по зонам
    end = datetime.now()
    start = end - timedelta(hours=24)
    
    # Получаем все зоны
    zones = db.query(Zone).all()
    zone_names = [z.name for z in zones]
    zone_ids = [z.id for z in zones]
    
    # Для каждого часа (0-23) и каждой зоны – средняя занятость
    hours = list(range(24))
    data_matrix = []
    
    for hour in hours:
        hour_start = start.replace(hour=hour, minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        row = []
        for zid in zone_ids:
            avg = db.query(func.avg(OccupancyMetric.people_count)).filter(
                OccupancyMetric.zone_id == zid,
                OccupancyMetric.timestamp >= hour_start,
                OccupancyMetric.timestamp < hour_end
            ).scalar()
            row.append(round(avg or 0, 1))
        data_matrix.append(row)
    
    db.close()
    
    # Формат для ECharts heatmap: [час, индекс_зоны, значение]
    series_data = []
    for i, hour in enumerate(hours):
        for j, val in enumerate(data_matrix[i]):
            series_data.append([i, j, val])
    
    return jsonify({
        "zones": zone_names,
        "hours": [f"{h}:00" for h in hours],
        "data": series_data,
        "max": max([v for row in data_matrix for v in row]) if data_matrix else 1
    })