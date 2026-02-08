"""
Telemetry API endpoints for IoT sensor data
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Store, Telemetry

router = APIRouter()


class TelemetryInput(BaseModel):
    """Telemetry input schema"""
    store_id: int = Field(..., description="Store ID")
    sensor: str = Field(..., description="Sensor identifier (e.g., 'cooler_humidity_pct')")
    value: float = Field(..., description="Sensor reading value")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., 'pct', 'celsius')")
    metadata: Optional[str] = Field(None, description="Additional metadata as JSON string")


class TelemetryResponse(BaseModel):
    """Telemetry response schema"""
    id: int
    store_id: int
    sensor: str
    value: float
    unit: Optional[str]
    ts_datetime: str
    
    class Config:
        from_attributes = True


@router.post("/telemetry")
async def create_telemetry(
    data: TelemetryInput,
    db: Session = Depends(get_db)
):
    """
    Accept telemetry data from IoT sensors
    
    Example:
    ```json
    {
        "store_id": 1,
        "sensor": "cooler_humidity_pct",
        "value": 25.40
    }
    ```
    """
    # Verify store exists
    store = db.query(Store).filter(Store.id == data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {data.store_id} not found")
    
    # Create telemetry record
    telemetry = Telemetry(
        store_id=data.store_id,
        sensor=data.sensor,
        value=data.value,
        unit=data.unit,
        ts_datetime=datetime.utcnow(),
        metadata_json=data.metadata
    )
    
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)
    
    return {
        "success": True,
        "message": "Telemetry data received",
        "data": {
            "id": telemetry.id,
            "store_id": telemetry.store_id,
            "sensor": telemetry.sensor,
            "value": telemetry.value,
            "unit": telemetry.unit,
            "ts_datetime": telemetry.ts_datetime.isoformat()
        }
    }


@router.get("/telemetry/{store_id}")
async def get_telemetry(
    store_id: int,
    sensor: Optional[str] = Query(None, description="Filter by sensor type"),
    hours: int = Query(24, description="Hours of history to retrieve"),
    limit: int = Query(100, description="Maximum records"),
    db: Session = Depends(get_db)
):
    """
    Get telemetry data for a store
    """
    # Verify store exists
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")
    
    # Build query
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(Telemetry).filter(
        Telemetry.store_id == store_id,
        Telemetry.ts_datetime >= cutoff_time
    )
    
    if sensor:
        query = query.filter(Telemetry.sensor == sensor)
    
    results = query.order_by(Telemetry.ts_datetime.desc()).limit(limit).all()
    
    return {
        "store_id": store_id,
        "store_name": store.name,
        "sensor_filter": sensor,
        "hours": hours,
        "total": len(results),
        "readings": [
            {
                "id": t.id,
                "sensor": t.sensor,
                "value": t.value,
                "unit": t.unit,
                "ts_datetime": t.ts_datetime.isoformat()
            }
            for t in results
        ]
    }


@router.get("/telemetry/{store_id}/latest")
async def get_latest_telemetry(
    store_id: int,
    db: Session = Depends(get_db)
):
    """
    Get latest reading for each sensor at a store
    """
    # Verify store exists
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")
    
    # Get distinct sensors
    sensors = db.query(Telemetry.sensor).filter(
        Telemetry.store_id == store_id
    ).distinct().all()
    
    latest_readings = {}
    
    for (sensor_name,) in sensors:
        latest = db.query(Telemetry).filter(
            Telemetry.store_id == store_id,
            Telemetry.sensor == sensor_name
        ).order_by(Telemetry.ts_datetime.desc()).first()
        
        if latest:
            latest_readings[sensor_name] = {
                "value": latest.value,
                "unit": latest.unit,
                "ts_datetime": latest.ts_datetime.isoformat(),
                "age_seconds": (datetime.utcnow() - latest.ts_datetime).total_seconds()
            }
    
    return {
        "store_id": store_id,
        "store_name": store.name,
        "sensors": latest_readings,
        "total_sensors": len(latest_readings)
    }
