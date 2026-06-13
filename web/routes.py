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