from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String

class Vendor(Base):
    __tablename__ = 'Vendors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

Vendor.models = relationship('Model', back_populates='vendor')