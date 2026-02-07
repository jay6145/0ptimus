"""
Store model
"""
from sqlalchemy import Column, Integer, String, Float
from ..database import Base


class Store(Base):
    """Store/Location model"""
    
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<Store(id={self.id}, name='{self.name}')>"
