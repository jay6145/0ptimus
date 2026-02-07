"""
Transfer recommendation and store distance models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class TransferRecommendation(Base):
    """Transfer recommendation model"""
    
    __tablename__ = "transfer_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    from_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    to_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    urgency_score = Column(Float, nullable=True)
    rationale = Column(Text, nullable=True)  # Plain-English explanation
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, accepted, rejected
    
    # Relationships
    from_store = relationship("Store", foreign_keys=[from_store_id])
    to_store = relationship("Store", foreign_keys=[to_store_id])
    sku = relationship("SKU")
    
    def __repr__(self):
        return f"<TransferRecommendation(id={self.id}, from={self.from_store_id}, to={self.to_store_id}, sku={self.sku_id}, urgency={self.urgency_score})>"


class StoreDistance(Base):
    """Store distance matrix for transfer optimization"""
    
    __tablename__ = "store_distances"
    
    from_store_id = Column(Integer, ForeignKey("stores.id"), primary_key=True)
    to_store_id = Column(Integer, ForeignKey("stores.id"), primary_key=True)
    distance_km = Column(Float, nullable=True)
    transfer_cost = Column(Float, nullable=True)
    
    # Relationships
    from_store = relationship("Store", foreign_keys=[from_store_id])
    to_store = relationship("Store", foreign_keys=[to_store_id])
    
    def __repr__(self):
        return f"<StoreDistance(from={self.from_store_id}, to={self.to_store_id}, distance={self.distance_km}km)>"
