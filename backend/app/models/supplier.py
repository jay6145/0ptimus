"""
Supplier models
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Supplier(Base):
    """Supplier model"""
    
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    avg_lead_time_days = Column(Integer, nullable=True)
    lead_time_std_days = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}', lead_time={self.avg_lead_time_days})>"


class SKUSupplier(Base):
    """SKU-Supplier relationship model"""
    
    __tablename__ = "sku_supplier"
    
    sku_id = Column(Integer, ForeignKey("skus.id"), primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), primary_key=True)
    case_pack = Column(Integer, nullable=True)
    min_order_qty = Column(Integer, nullable=True)
    
    # Relationships
    sku = relationship("SKU")
    supplier = relationship("Supplier")
    
    def __repr__(self):
        return f"<SKUSupplier(sku={self.sku_id}, supplier={self.supplier_id})>"
