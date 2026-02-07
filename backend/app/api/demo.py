"""
Demo data management API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..utils.demo_data import generate_demo_data
from ..models import (
    Store, SKU, InventorySnapshot, SalesDaily, 
    AnomalyEvent, TransferRecommendation
)

router = APIRouter()


class DemoDataRequest(BaseModel):
    num_stores: Optional[int] = 5
    num_skus: Optional[int] = 200
    days_history: Optional[int] = 60


@router.post("/demo/regenerate")
async def regenerate_demo_data(
    request: DemoDataRequest,
    db: Session = Depends(get_db)
):
    """
    Regenerate demo data with specified parameters
    """
    try:
        stats = generate_demo_data(
            num_stores=request.num_stores,
            num_skus=request.num_skus,
            days_history=request.days_history
        )
        
        return {
            "success": True,
            "message": "Demo data regenerated successfully",
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error generating demo data: {str(e)}"
        }


@router.get("/demo/stats")
async def get_demo_stats(db: Session = Depends(get_db)):
    """
    Get current database statistics
    """
    stats = {
        "stores": db.query(Store).count(),
        "skus": db.query(SKU).count(),
        "inventory_snapshots": db.query(InventorySnapshot).count(),
        "sales_records": db.query(SalesDaily).count(),
        "anomalies": db.query(AnomalyEvent).count(),
        "transfer_recommendations": db.query(TransferRecommendation).count()
    }
    
    # Get date range
    from sqlalchemy import func
    date_range = db.query(
        func.min(InventorySnapshot.ts_date).label('min_date'),
        func.max(InventorySnapshot.ts_date).label('max_date')
    ).first()
    
    if date_range and date_range.min_date:
        stats["date_range"] = {
            "start": date_range.min_date.isoformat(),
            "end": date_range.max_date.isoformat(),
            "days": (date_range.max_date - date_range.min_date).days + 1
        }
    
    return stats
