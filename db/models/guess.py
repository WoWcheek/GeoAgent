from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey

class Guess(Base):
    __tablename__ = 'Guesses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    round_id = Column(Integer, ForeignKey('Rounds.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('Models.id'), nullable=False)
    predicted_latitude = Column(Float)
    predicted_longitude = Column(Float)
    reasoning = Column(String, nullable=True)

    round = relationship('Round', back_populates='guesses')
    model = relationship('Model', back_populates='guesses')