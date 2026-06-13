from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Zone(Base):
    __tablename__ = 'zones'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    type = Column(String(50))
    capacity = Column(Integer)

class OccupancyMetric(Base):
    __tablename__ = 'occupancy_metrics'
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer)
    timestamp = Column(DateTime)
    people_count = Column(Integer)

class OccupancyEvent(Base):
    __tablename__ = 'occupancy_events'
    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer)
    event_type = Column(String(20))
    timestamp = Column(DateTime)