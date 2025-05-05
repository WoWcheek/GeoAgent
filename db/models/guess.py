from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey

class Guess(Base):
    __tablename__ = 'Guesses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    round_id = Column(Integer, ForeignKey('Rounds.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('Models.id'), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    country_code = Column(String(2))
    reasoning = Column(String, nullable=False)
    seconds_spent = Column(Integer, nullable=False)
    score = Column(Integer)
    distance_km = Column(Float)

    round = relationship('Round', back_populates='guesses')
    model = relationship('Model', back_populates='guesses')