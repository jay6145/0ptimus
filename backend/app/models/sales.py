"""
Sales daily model
"""
from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base


class SalesDaily(Base):
    """Daily sales transactions model"""
    
    __tablename__ = "sales_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    ts_date = Column(Date, nullable=False, index=True)
    qty_sold = Column(Integer, nullable=False, default=0)
    
    # Relationships
    store = relationship("Store")
    sku = relationship("SKU")
    
    # Unique constraint: one sales record per store/sku/date
    __table_args__ = (
        UniqueConstraint('store_id', 'sku_id', 'ts_date', name='uix_sales_store_sku_date'),
    )
    
    def __repr__(self):
        return f"<SalesDaily(store={self.store_id}, sku={self.sku_id}, date={self.ts_date}, qty={self.qty_sold})>"
