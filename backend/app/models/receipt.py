"""
Receipts daily model
"""
from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ReceiptsDaily(Base):
    """Daily receipts (incoming stock) model"""
    
    __tablename__ = "receipts_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    ts_date = Column(Date, nullable=False, index=True)
    qty_received = Column(Integer, nullable=False, default=0)
    
    # Relationships
    store = relationship("Store")
    sku = relationship("SKU")
    
    def __repr__(self):
        return f"<ReceiptsDaily(store={self.store_id}, sku={self.sku_id}, date={self.ts_date}, qty={self.qty_received})>"
