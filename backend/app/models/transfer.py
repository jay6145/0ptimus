"""
Transfer model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Transfer(Base):
    """Inter-store transfer model"""
    
    __tablename__ = "transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    from_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    to_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    status = Column(String, default="draft")  # draft, approved, in_transit, received
    created_at = Column(DateTime, default=datetime.utcnow)
    received_at = Column(DateTime, nullable=True)
    
    # Relationships
    from_store = relationship("Store", foreign_keys=[from_store_id])
    to_store = relationship("Store", foreign_keys=[to_store_id])
    sku = relationship("SKU")
    
    def __repr__(self):
        return f"<Transfer(id={self.id}, from={self.from_store_id}, to={self.to_store_id}, sku={self.sku_id}, qty={self.qty}, status='{self.status}')>"
