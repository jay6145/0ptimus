"""
Telemetry model for IoT sensor data
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Telemetry(Base):
    """Telemetry data from IoT sensors (Arduino, ESP32, etc.)"""
    
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sensor = Column(String, nullable=False, index=True)  # e.g., "cooler_temp", "bin_weight"
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)  # e.g., "celsius", "kg", "pct"
    ts_datetime = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    metadata_json = Column(String, nullable=True)  # Additional sensor metadata
    
    # Relationships
    store = relationship("Store")
    
    def __repr__(self):
        return f"<Telemetry(store={self.store_id}, sensor={self.sensor}, value={self.value}, time={self.ts_datetime})>"
