"""
Inventory snapshot model
"""
from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class InventorySnapshot(Base):
    """Daily inventory snapshot model"""
    
    __tablename__ = "inventory_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    ts_date = Column(Date, nullable=False, index=True)
    on_hand = Column(Integer, nullable=False)
    
    # Relationships
    store = relationship("Store")
    sku = relationship("SKU")
    
    # Unique constraint: one snapshot per store/sku/date
    __table_args__ = (
        UniqueConstraint('store_id', 'sku_id', 'ts_date', name='uix_store_sku_date'),
    )
    
    def __repr__(self):
        return f"<InventorySnapshot(store={self.store_id}, sku={self.sku_id}, date={self.ts_date}, on_hand={self.on_hand})>"
