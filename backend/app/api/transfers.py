"""
Transfer management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models import Transfer, Store, SKU
from ..services.transfer_optimizer import (
    generate_transfer_recommendations,
    save_transfer_recommendations,
    create_transfer_from_recommendation,
    get_transfer_opportunities_summary
)

router = APIRouter()


class TransferCreate(BaseModel):
    from_store_id: int
    to_store_id: int
    sku_id: int
    qty: int
    recommendation_id: Optional[int] = None


class TransferUpdate(BaseModel):
    status: str


@router.get("/transfers/recommendations")
async def get_transfer_recommendations(
    min_urgency: float = 0.5,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get transfer recommendations
    """
    recommendations = generate_transfer_recommendations(
        db,
        min_urgency=min_urgency
    )
    
    # Limit results
    recommendations = recommendations[:limit]
    
    # Group by receiver store
    grouped = {}
    for rec in recommendations:
        receiver_name = rec['to_store_name']
        if receiver_name not in grouped:
            grouped[receiver_name] = []
        grouped[receiver_name].append(rec)
    
    return {
        "recommendations": recommendations,
        "grouped_by_receiver": grouped,
        "total": len(recommendations),
        "summary": get_transfer_opportunities_summary(db)
    }


@router.post("/transfers/draft")
async def create_transfer_draft(
    transfer: TransferCreate,
    db: Session = Depends(get_db)
):
    """
    Create a transfer draft
    """
    # Validate stores and SKU exist
    from_store = db.query(Store).filter(Store.id == transfer.from_store_id).first()
    to_store = db.query(Store).filter(Store.id == transfer.to_store_id).first()
    sku = db.query(SKU).filter(SKU.id == transfer.sku_id).first()
    
    if not from_store or not to_store or not sku:
        raise HTTPException(status_code=404, detail="Store or SKU not found")
    
    if transfer.from_store_id == transfer.to_store_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to same store")
    
    # Create transfer
    new_transfer = Transfer(
        from_store_id=transfer.from_store_id,
        to_store_id=transfer.to_store_id,
        sku_id=transfer.sku_id,
        qty=transfer.qty,
        status="draft"
    )
    db.add(new_transfer)
    db.commit()
    db.refresh(new_transfer)
    
    return {
        "id": new_transfer.id,
        "from_store_id": new_transfer.from_store_id,
        "from_store_name": from_store.name,
        "to_store_id": new_transfer.to_store_id,
        "to_store_name": to_store.name,
        "sku_id": new_transfer.sku_id,
        "sku_name": sku.name,
        "qty": new_transfer.qty,
        "status": new_transfer.status,
        "created_at": new_transfer.created_at.isoformat()
    }


@router.get("/transfers")
async def get_transfers(
    status: Optional[str] = None,
    store_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get transfers with optional filters
    """
    query = db.query(Transfer)
    
    if status:
        query = query.filter(Transfer.status == status)
    
    if store_id:
        query = query.filter(
            (Transfer.from_store_id == store_id) | (Transfer.to_store_id == store_id)
        )
    
    transfers = query.order_by(Transfer.created_at.desc()).limit(limit).all()
    
    result = []
    for t in transfers:
        from_store = db.query(Store).filter(Store.id == t.from_store_id).first()
        to_store = db.query(Store).filter(Store.id == t.to_store_id).first()
        sku = db.query(SKU).filter(SKU.id == t.sku_id).first()
        
        result.append({
            "id": t.id,
            "from_store_id": t.from_store_id,
            "from_store_name": from_store.name if from_store else None,
            "to_store_id": t.to_store_id,
            "to_store_name": to_store.name if to_store else None,
            "sku_id": t.sku_id,
            "sku_name": sku.name if sku else None,
            "qty": t.qty,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
            "received_at": t.received_at.isoformat() if t.received_at else None
        })
    
    return {
        "transfers": result,
        "total": len(result)
    }


@router.patch("/transfers/{transfer_id}")
async def update_transfer(
    transfer_id: int,
    update: TransferUpdate,
    db: Session = Depends(get_db)
):
    """
    Update transfer status
    """
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    # Validate status transition
    valid_statuses = ["draft", "approved", "in_transit", "received", "cancelled"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    transfer.status = update.status
    
    # Set received_at if status is received
    if update.status == "received":
        from datetime import datetime
        transfer.received_at = datetime.utcnow()
    
    db.commit()
    db.refresh(transfer)
    
    return {
        "id": transfer.id,
        "status": transfer.status,
        "received_at": transfer.received_at.isoformat() if transfer.received_at else None
    }


@router.post("/transfers/generate-recommendations")
async def generate_and_save_recommendations(
    target_cover_days: int = 10,
    safety_buffer_days: int = 2,
    min_urgency: float = 0.5,
    db: Session = Depends(get_db)
):
    """
    Generate and save transfer recommendations
    """
    recommendations = generate_transfer_recommendations(
        db,
        target_cover_days=target_cover_days,
        safety_buffer_days=safety_buffer_days,
        min_urgency=min_urgency
    )
    
    saved_count = save_transfer_recommendations(db, recommendations)
    
    return {
        "generated": len(recommendations),
        "saved": saved_count,
        "message": f"Generated and saved {saved_count} transfer recommendations"
    }
