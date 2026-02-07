"""
SKU (Stock Keeping Unit) model
"""
from sqlalchemy import Column, Integer, String, Float, Boolean
from ..database import Base


class SKU(Base):
    """SKU/Product model"""
    
    __tablename__ = "skus"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    unit = Column(String, nullable=True)  # e.g., "each", "case", "lb"
    cost = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    is_perishable = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<SKU(id={self.id}, name='{self.name}', category='{self.category}')>"
