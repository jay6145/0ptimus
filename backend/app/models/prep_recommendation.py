"""
Prep schedule recommendation model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class PrepRecommendation(Base):
    """Prep schedule recommendation model"""
    
    __tablename__ = "prep_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    prep_time = Column(DateTime, nullable=False, index=True)  # When to prep
    qty_to_prep = Column(Integer, nullable=False)  # How much to prep
    reason = Column(Text, nullable=True)  # "For lunch rush at 12pm"
    priority = Column(String, default="medium")  # critical, high, medium, low
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, completed, skipped
    
    # Relationships
    store = relationship("Store")
    sku = relationship("SKU")
    
    def __repr__(self):
        return f"<PrepRecommendation(store={self.store_id}, sku={self.sku_id}, prep_time={self.prep_time}, qty={self.qty_to_prep})>"


class InventoryRealtime(Base):
    """Real-time inventory tracking model"""
    
    __tablename__ = "inventory_realtime"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    ts_datetime = Column(DateTime, nullable=False, index=True)
    on_hand = Column(Integer, nullable=False)
    prep_in_progress = Column(Integer, default=0)  # Being prepped now
    
    # Relationships
    store = relationship("Store")
    sku = relationship("SKU")
    
    def __repr__(self):
        return f"<InventoryRealtime(store={self.store_id}, sku={self.sku_id}, time={self.ts_datetime}, on_hand={self.on_hand})>"
