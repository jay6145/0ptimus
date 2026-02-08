"""
Peak hour demand forecasting service for restaurant operations
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import SalesHourly, InventorySnapshot, SKU, PrepRecommendation
from functools import lru_cache


# Peak hour definitions for Chipotle
LUNCH_HOURS = [11, 12, 13]  # 11am-2pm
DINNER_HOURS = [17, 18, 19]  # 5pm-8pm
PEAK_HOURS = LUNCH_HOURS + DINNER_HOURS

# Simple in-memory cache for hourly forecasts (TTL: 5 minutes)
_forecast_cache = {}
_cache_ttl = 300  # 5 minutes


def is_peak_hour(hour: int) -> bool:
    """Check if hour is a peak period"""
    return hour in PEAK_HOURS


def get_peak_period_name(hour: int) -> Optional[str]:
    """Get name of peak period"""
    if hour in LUNCH_HOURS:
        return "lunch"
    elif hour in DINNER_HOURS:
        return "dinner"
    return None


def calculate_hourly_demand_forecast(
    db: Session,
    store_id: int,
    sku_id: int,
    target_hour: int,
    target_day_of_week: int,
    lookback_weeks: int = 8
) -> Dict:
    """
    Predict demand for specific hour based on historical patterns
    Uses last N weeks of data for the same hour/day combination
    WITH CACHING for performance
    """
    # Check cache
    cache_key = f"{store_id}_{sku_id}_{target_hour}_{target_day_of_week}"
    if cache_key in _forecast_cache:
        cached_data, cached_time = _forecast_cache[cache_key]
        if (datetime.now() - cached_time).total_seconds() < _cache_ttl:
            return cached_data
    
    # Get historical sales for this hour/day combination
    historical_sales = db.query(SalesHourly).filter(
        SalesHourly.store_id == store_id,
        SalesHourly.sku_id == sku_id,
        SalesHourly.hour_of_day == target_hour,
        SalesHourly.day_of_week == target_day_of_week
    ).order_by(SalesHourly.ts_datetime.desc()).limit(lookback_weeks).all()
    
    if not historical_sales:
        # Fallback to any data for this hour
        historical_sales = db.query(SalesHourly).filter(
            SalesHourly.store_id == store_id,
            SalesHourly.sku_id == sku_id,
            SalesHourly.hour_of_day == target_hour
        ).order_by(SalesHourly.ts_datetime.desc()).limit(lookback_weeks).all()
    
    if not historical_sales:
        result = {
            "predicted_demand": 0.0,
            "confidence": "low",
            "is_peak_hour": is_peak_hour(target_hour),
            "peak_period": get_peak_period_name(target_hour),
            "data_points": 0
        }
        _forecast_cache[cache_key] = (result, datetime.now())
        return result
    
    # Weighted average (recent weeks weighted higher)
    weights = [0.95 ** i for i in range(len(historical_sales))]
    weights.reverse()  # Most recent gets highest weight
    
    weighted_demand = sum(s.qty_sold * w for s, w in zip(historical_sales, weights))
    total_weight = sum(weights)
    
    predicted = weighted_demand / total_weight if total_weight > 0 else 0.0
    
    # Peak hour adjustment
    is_peak = is_peak_hour(target_hour)
    if is_peak and predicted > 0:
        predicted *= 1.15  # 15% buffer for peak hours
    
    # Confidence based on data availability
    confidence = "high" if len(historical_sales) >= 6 else \
                 "medium" if len(historical_sales) >= 3 else "low"
    
    result = {
        "predicted_demand": round(predicted, 1),
        "confidence": confidence,
        "is_peak_hour": is_peak,
        "peak_period": get_peak_period_name(target_hour),
        "data_points": len(historical_sales)
    }
    
    # Cache result
    _forecast_cache[cache_key] = (result, datetime.now())
    
    return result


def predict_stockout_time(
    db: Session,
    store_id: int,
    sku_id: int,
    current_on_hand: int,
    start_hour: Optional[int] = None
) -> Dict:
    """
    Predict exact hour when SKU will run out during the day
    """
    current_time = datetime.now()
    current_hour = start_hour if start_hour is not None else current_time.hour
    current_day = current_time.weekday()
    
    remaining = current_on_hand
    
    for hour in range(current_hour, 24):
        forecast = calculate_hourly_demand_forecast(
            db, store_id, sku_id, hour, current_day
        )
        
        demand = forecast["predicted_demand"]
        remaining -= demand
        
        if remaining <= 0:
            stockout_time = current_time.replace(hour=hour, minute=30, second=0, microsecond=0)
            hours_until = hour - current_hour
            
            return {
                "will_stockout": True,
                "stockout_time": stockout_time.isoformat(),
                "stockout_hour": hour,
                "hours_until_stockout": hours_until,
                "minutes_until_stockout": hours_until * 60,
                "is_during_peak": forecast["is_peak_hour"],
                "peak_period": forecast["peak_period"],
                "severity": "critical" if forecast["is_peak_hour"] else "high",
                "deficit": abs(remaining)
            }
    
    return {
        "will_stockout": False,
        "safe_until": "end_of_day",
        "remaining_at_close": remaining
    }


def generate_prep_schedule(
    db: Session,
    store_id: int,
    prep_lead_time_hours: int = 2,
    target_date: Optional[datetime] = None
) -> List[Dict]:
    """
    Generate prep schedule for the day based on hourly forecasts
    Focuses on critical items that might run out during peak hours
    OPTIMIZED: Limits queries and uses caching
    """
    if target_date is None:
        target_date = datetime.now()
    
    recommendations = []
    
    # Focus on high-demand perishable items - LIMIT TO 5 FOR PERFORMANCE
    critical_skus = db.query(SKU).filter(
        SKU.category.in_(["Proteins", "Salsas & Sauces", "Produce"])
    ).limit(5).all()  # Reduced from 10 to 5 for speed
    
    for sku in critical_skus:
        # Get current inventory
        latest_snapshot = db.query(InventorySnapshot).filter(
            InventorySnapshot.store_id == store_id,
            InventorySnapshot.sku_id == sku.id
        ).order_by(InventorySnapshot.ts_date.desc()).first()
        
        current_inv = latest_snapshot.on_hand if latest_snapshot else 0
        
        # Skip if plenty of inventory (optimization)
        if current_inv > 100:
            continue
        
        # Predict stockout time
        stockout_pred = predict_stockout_time(
            db, store_id, sku.id, current_inv
        )
        
        if stockout_pred["will_stockout"]:
            stockout_hour = stockout_pred["stockout_hour"]
            stockout_time = datetime.fromisoformat(stockout_pred["stockout_time"])
            prep_time = stockout_time - timedelta(hours=prep_lead_time_hours)
            
            # Only recommend if prep time is in the future
            if prep_time > target_date:
                # Calculate how much to prep (cover next 4 hours) - REDUCED TO 2 HOURS FOR SPEED
                total_demand = 0
                for hour in range(stockout_hour, min(stockout_hour + 2, 24)):  # Changed from 4 to 2
                    forecast = calculate_hourly_demand_forecast(
                        db, store_id, sku.id, hour, target_date.weekday()
                    )
                    total_demand += forecast["predicted_demand"]
                
                qty_to_prep = int(total_demand * 1.1)  # 10% buffer
                
                # Determine priority
                if stockout_pred["is_during_peak"]:
                    priority = "critical"
                    reason = f"Will run out at {stockout_time.strftime('%I:%M %p')} during {stockout_pred['peak_period']} rush. Prep immediately!"
                else:
                    priority = "high"
                    reason = f"Will run out at {stockout_time.strftime('%I:%M %p')}. Prep by {prep_time.strftime('%I:%M %p')}."
                
                recommendations.append({
                    "sku_id": sku.id,
                    "sku_name": sku.name,
                    "category": sku.category,
                    "prep_time": prep_time.isoformat(),
                    "prep_time_display": prep_time.strftime("%I:%M %p"),
                    "qty_to_prep": qty_to_prep,
                    "reason": reason,
                    "priority": priority,
                    "current_on_hand": current_inv,
                    "stockout_time": stockout_time.strftime("%I:%M %p"),
                    "is_peak_stockout": stockout_pred["is_during_peak"],
                    "hours_until_prep": (prep_time - target_date).total_seconds() / 3600
                })
    
    # Sort by prep time (soonest first)
    recommendations.sort(key=lambda x: x["prep_time"])
    
    return recommendations


def get_hourly_forecast_for_day(
    db: Session,
    store_id: int,
    sku_id: int,
    target_date: Optional[datetime] = None
) -> List[Dict]:
    """
    Get hourly demand forecast for entire day
    """
    if target_date is None:
        target_date = datetime.now()
    
    day_of_week = target_date.weekday()
    forecasts = []
    
    # Operating hours: 6am - 10pm
    for hour in range(6, 23):
        forecast = calculate_hourly_demand_forecast(
            db, store_id, sku_id, hour, day_of_week
        )
        
        forecasts.append({
            "hour": hour,
            "hour_display": f"{hour % 12 or 12}{'am' if hour < 12 else 'pm'}",
            "predicted_demand": forecast["predicted_demand"],
            "is_peak_hour": forecast["is_peak_hour"],
            "peak_period": forecast["peak_period"],
            "confidence": forecast["confidence"]
        })
    
    return forecasts


def get_peak_hour_summary(
    db: Session,
    store_id: int
) -> Dict:
    """
    Get summary of peak hour status for dashboard
    """
    current_time = datetime.now()
    current_hour = current_time.hour
    
    # Determine current/next peak period
    if current_hour < 11:
        next_peak = "lunch"
        next_peak_hour = 11
        hours_until = 11 - current_hour
    elif current_hour < 14:
        next_peak = "lunch"
        next_peak_hour = current_hour
        hours_until = 0  # In progress
    elif current_hour < 17:
        next_peak = "dinner"
        next_peak_hour = 17
        hours_until = 17 - current_hour
    elif current_hour < 20:
        next_peak = "dinner"
        next_peak_hour = current_hour
        hours_until = 0  # In progress
    else:
        next_peak = "lunch"
        next_peak_hour = 11
        hours_until = 24 - current_hour + 11  # Tomorrow
    
    # Get critical items (proteins and guac) - LIMIT FOR PERFORMANCE
    critical_skus = db.query(SKU).filter(
        SKU.category.in_(["Proteins", "Salsas & Sauces"])
    ).limit(5).all()  # Only check top 5 items
    
    at_risk_items = []
    
    for sku in critical_skus:
        latest_snapshot = db.query(InventorySnapshot).filter(
            InventorySnapshot.store_id == store_id,
            InventorySnapshot.sku_id == sku.id
        ).order_by(InventorySnapshot.ts_date.desc()).first()
        
        if latest_snapshot:
            stockout_pred = predict_stockout_time(
                db, store_id, sku.id, latest_snapshot.on_hand
            )
            
            if stockout_pred["will_stockout"] and stockout_pred["is_during_peak"]:
                at_risk_items.append({
                    "sku_name": sku.name,
                    "stockout_time": stockout_pred["stockout_time"],
                    "hours_until": stockout_pred["hours_until_stockout"],
                    "peak_period": stockout_pred["peak_period"]
                })
    
    return {
        "current_time": current_time.isoformat(),
        "current_hour": current_hour,
        "next_peak_period": next_peak,
        "next_peak_hour": next_peak_hour,
        "hours_until_peak": hours_until,
        "minutes_until_peak": hours_until * 60,
        "is_currently_peak": hours_until == 0,
        "at_risk_items": at_risk_items,
        "total_at_risk": len(at_risk_items)
    }


def save_prep_recommendations(
    db: Session,
    store_id: int,
    recommendations: List[Dict]
) -> int:
    """
    Save prep recommendations to database
    """
    # Clear old pending recommendations for today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    db.query(PrepRecommendation).filter(
        PrepRecommendation.store_id == store_id,
        PrepRecommendation.prep_time >= today_start,
        PrepRecommendation.prep_time < today_end,
        PrepRecommendation.status == 'pending'
    ).delete()
    
    saved_count = 0
    
    for rec in recommendations:
        prep_rec = PrepRecommendation(
            store_id=store_id,
            sku_id=rec['sku_id'],
            prep_time=datetime.fromisoformat(rec['prep_time']),
            qty_to_prep=rec['qty_to_prep'],
            reason=rec['reason'],
            priority=rec['priority'],
            status='pending'
        )
        db.add(prep_rec)
        saved_count += 1
    
    db.commit()
    
    return saved_count
