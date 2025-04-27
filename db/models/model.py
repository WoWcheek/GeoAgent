from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey

class Model(Base):
    __tablename__ = 'Models'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey('Vendors.id'), nullable=False)
    model_name = Column(String(100), nullable=False)

    vendor = relationship('Vendor', back_populates='models')

Model.guesses = relationship('Guess', back_populates='model')