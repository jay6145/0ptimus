"""
Cross-store transfer recommendation engine with distance optimization
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from ..models import (
    Store, SKU, InventorySnapshot, StoreDistance,
    TransferRecommendation
)
from .forecasting import calculate_demand_forecast, calculate_days_of_cover


def calculate_urgency(days_of_cover: float, daily_demand: float) -> float:
    """
    Calculate urgency score (0-1) based on days of cover
    Lower days of cover = higher urgency
    """
    if days_of_cover <= 0:
        return 1.0  # Critical
    elif days_of_cover <= 3:
        return 0.9
    elif days_of_cover <= 7:
        return 0.7
    elif days_of_cover <= 14:
        return 0.5
    else:
        return 0.3


def find_best_donor(
    db: Session,
    receiver_store_id: int,
    donors: List[Dict],
    sku_id: int
) -> Optional[Dict]:
    """
    Find best donor store based on surplus and distance
    Score = surplus / (1 + distance_penalty)
    """
    if not donors:
        return None
    
    scored_donors = []
    
    for donor in donors:
        if donor['surplus'] <= 0:
            continue
        
        # Get distance between stores
        distance_record = db.query(StoreDistance).filter(
            StoreDistance.from_store_id == donor['store_id'],
            StoreDistance.to_store_id == receiver_store_id
        ).first()
        
        distance = distance_record.distance_km if distance_record else 1000.0
        
        # Score = surplus / (1 + distance_penalty)
        # Closer stores get higher scores
        distance_penalty = distance / 100  # Normalize distance
        score = donor['surplus'] / (1 + distance_penalty)
        
        scored_donors.append({
            **donor,
            'distance': distance,
            'score': score
        })
    
    if not scored_donors:
        return None
    
    # Return highest scoring donor
    return max(scored_donors, key=lambda x: x['score'])


def generate_transfer_recommendations(
    db: Session,
    target_cover_days: int = 10,
    safety_buffer_days: int = 2,
    min_urgency: float = 0.5
) -> List[Dict]:
    """
    Generate transfer recommendations to prevent stockouts
    Prioritizes nearby stores and high-urgency receivers
    """
    recommendations = []
    
    # Get all stores
    stores = db.query(Store).all()
    
    # Get all SKUs
    skus = db.query(SKU).all()
    
    # Get latest inventory date
    latest_date = datetime.now().date() - timedelta(days=1)
    
    # Process each SKU
    for sku in skus:
        receivers = []
        donors = []
        
        # Analyze each store for this SKU
        for store in stores:
            # Get current inventory
            snapshot = db.query(InventorySnapshot).filter(
                InventorySnapshot.store_id == store.id,
                InventorySnapshot.sku_id == sku.id,
                InventorySnapshot.ts_date == latest_date
            ).first()
            
            if not snapshot:
                continue
            
            on_hand = snapshot.on_hand
            
            # Get demand forecast
            forecast = calculate_demand_forecast(db, store.id, sku.id)
            daily_demand = forecast["daily_demand"]
            
            if daily_demand < 0.1:
                continue  # Skip items with no demand
            
            # Calculate target and buffer
            target_on_hand = daily_demand * target_cover_days
            buffer_on_hand = daily_demand * safety_buffer_days
            
            # Calculate need and surplus
            need = max(0, target_on_hand - on_hand)
            surplus = max(0, on_hand - (target_on_hand + buffer_on_hand))
            
            days_of_cover = calculate_days_of_cover(db, store.id, sku.id, on_hand)
            
            if need > 0:
                urgency = calculate_urgency(days_of_cover, daily_demand)
                
                if urgency >= min_urgency:
                    receivers.append({
                        'store_id': store.id,
                        'store_name': store.name,
                        'need': need,
                        'urgency': urgency,
                        'days_of_cover': days_of_cover,
                        'on_hand': on_hand,
                        'daily_demand': daily_demand
                    })
            
            if surplus > 0:
                donors.append({
                    'store_id': store.id,
                    'store_name': store.name,
                    'surplus': surplus,
                    'days_of_cover': days_of_cover,
                    'on_hand': on_hand,
                    'daily_demand': daily_demand
                })
        
        # Sort receivers by urgency (highest first)
        receivers.sort(key=lambda x: x['urgency'], reverse=True)
        
        # Match receivers with donors
        for receiver in receivers:
            if receiver['need'] <= 0:
                continue
            
            # Find best donor
            best_donor = find_best_donor(
                db,
                receiver['store_id'],
                donors,
                sku.id
            )
            
            if best_donor:
                # Calculate transfer quantity
                transfer_qty = min(
                    receiver['need'],
                    best_donor['surplus'],
                    receiver['daily_demand'] * 7  # Max 1 week supply
                )
                
                transfer_qty = int(transfer_qty)
                
                if transfer_qty < 1:
                    continue
                
                # Calculate days of cover after transfer
                receiver_days_after = (receiver['on_hand'] + transfer_qty) / receiver['daily_demand']
                donor_days_after = (best_donor['on_hand'] - transfer_qty) / best_donor['daily_demand']
                
                # Generate rationale
                rationale = (
                    f"Receiver ({receiver['store_name']}) will stock out in {receiver['days_of_cover']:.1f} days. "
                    f"Donor ({best_donor['store_name']}) has {best_donor['days_of_cover']:.1f} days excess. "
                    f"Transfer {transfer_qty} units prevents stockout. "
                    f"After transfer: receiver {receiver_days_after:.1f} days, donor {donor_days_after:.1f} days."
                )
                
                # Get distance info
                distance_record = db.query(StoreDistance).filter(
                    StoreDistance.from_store_id == best_donor['store_id'],
                    StoreDistance.to_store_id == receiver['store_id']
                ).first()
                
                recommendations.append({
                    'from_store_id': best_donor['store_id'],
                    'from_store_name': best_donor['store_name'],
                    'to_store_id': receiver['store_id'],
                    'to_store_name': receiver['store_name'],
                    'sku_id': sku.id,
                    'sku_name': sku.name,
                    'qty': transfer_qty,
                    'urgency_score': receiver['urgency'],
                    'rationale': rationale,
                    'distance_km': distance_record.distance_km if distance_record else None,
                    'transfer_cost': distance_record.transfer_cost if distance_record else None,
                    'receiver_days_before': receiver['days_of_cover'],
                    'receiver_days_after': round(receiver_days_after, 1),
                    'donor_days_before': best_donor['days_of_cover'],
                    'donor_days_after': round(donor_days_after, 1)
                })
                
                # Update donor surplus
                best_donor['surplus'] -= transfer_qty
                best_donor['on_hand'] -= transfer_qty
                receiver['need'] -= transfer_qty
    
    # Sort by urgency (highest first)
    recommendations.sort(key=lambda x: x['urgency_score'], reverse=True)
    
    return recommendations


def save_transfer_recommendations(
    db: Session,
    recommendations: List[Dict]
) -> int:
    """
    Save transfer recommendations to database
    """
    # Clear old pending recommendations
    db.query(TransferRecommendation).filter(
        TransferRecommendation.status == 'pending'
    ).delete()
    
    saved_count = 0
    
    for rec in recommendations:
        transfer_rec = TransferRecommendation(
            from_store_id=rec['from_store_id'],
            to_store_id=rec['to_store_id'],
            sku_id=rec['sku_id'],
            qty=rec['qty'],
            urgency_score=rec['urgency_score'],
            rationale=rec['rationale'],
            status='pending'
        )
        db.add(transfer_rec)
        saved_count += 1
    
    db.commit()
    
    return saved_count


def create_transfer_from_recommendation(
    db: Session,
    recommendation_id: int
) -> Optional[int]:
    """
    Create a transfer draft from a recommendation
    """
    from ..models import Transfer
    
    rec = db.query(TransferRecommendation).filter(
        TransferRecommendation.id == recommendation_id
    ).first()
    
    if not rec:
        return None
    
    # Create transfer
    transfer = Transfer(
        from_store_id=rec.from_store_id,
        to_store_id=rec.to_store_id,
        sku_id=rec.sku_id,
        qty=rec.qty,
        status='draft'
    )
    db.add(transfer)
    
    # Update recommendation status
    rec.status = 'accepted'
    
    db.commit()
    
    return transfer.id


def get_transfer_opportunities_summary(db: Session) -> Dict:
    """
    Get summary of transfer opportunities
    """
    recommendations = generate_transfer_recommendations(db)
    
    if not recommendations:
        return {
            "total_opportunities": 0,
            "high_urgency": 0,
            "medium_urgency": 0,
            "low_urgency": 0,
            "total_units": 0,
            "estimated_savings": 0
        }
    
    high_urgency = sum(1 for r in recommendations if r['urgency_score'] >= 0.8)
    medium_urgency = sum(1 for r in recommendations if 0.5 <= r['urgency_score'] < 0.8)
    low_urgency = sum(1 for r in recommendations if r['urgency_score'] < 0.5)
    
    total_units = sum(r['qty'] for r in recommendations)
    
    # Estimate savings (assume $50 per prevented stockout)
    estimated_savings = len(recommendations) * 50
    
    return {
        "total_opportunities": len(recommendations),
        "high_urgency": high_urgency,
        "medium_urgency": medium_urgency,
        "low_urgency": low_urgency,
        "total_units": total_units,
        "estimated_savings": estimated_savings
    }
